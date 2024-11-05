import re

from flask import render_template, render_template_string

class JinjaProcessor:
    class MissingComponent(Exception):
        """Exception raised when a template file is not found."""

        def __init__(self, template_name):
            super().__init__(
                f"Component '{template_name}.jinja' not found at render-time in any available template folders."
            )
            self.template_name = template_name

    class MissingAttributeList(Exception):
        """Exception raised when a component file lacks the required attribute list."""

        def __init__(self, template_name):
            super().__init__(
                f"Component '{template_name}.jinja' is missing an attribute list in the required format."
            )
            self.template_name = template_name

    class MissingAttributeInCall(Exception):
        """Exception raised when a required attribute is missing in the component call."""

        def __init__(self, template_name, attribute):
            super().__init__(
                f"Component '{template_name}.jinja' requires attribute '{attribute}' when it's called."
            )
            self.template_name = template_name
            self.attribute = attribute

    def __init__(self, app=None):
        if app:
            self.init(app)

    def init(self, app):
        self.app = app
        self.env = self.app.jinja_env

    def render(self, file: str, **kwargs) -> str:
        """Searches all template folders (in blueprints, and the global one), finds a .jinja file matching the name, and returns a processed/rendered component.

        Args:
            file (str): name of the file you want to render, like 'page.html'

        Returns:
            rendered template: returns the results of Jinja's render_template_string evaluated on the component after pre-processing.
        """
        try:
            template_source, _, _ = self.env.loader.get_source(self.env, file)

            # Apply any custom processing to the template source
            processed_template = self.preprocess_components(template_source, **kwargs)

            # Render the processed template with context variables
            return render_template_string(processed_template, **kwargs)
        except AttributeError:
            raise AttributeError(
                "'DeepRender' has no environment variable set. Did you forget to pass the 'app' object?\n\ndr = DeepRender(app)\n\nOR\n\ndr = DeepRender()\ndr.init(app)"
            )

    def preprocess_components(self, html, **kwargs):
        """
        Uses Regex to find and replace all custom tags with their rendered versions.

        Takes raw HTML string and whatever other arguments were passed to the original render.
        """

        # Pattern to match custom component tags
        pattern = r"<([A-Z]\w+)([^>]*)>(.*?)</\1>"

        # Use `re.finditer` to iterate over all matches of custom components
        result = []
        last_end = 0

        for match in re.finditer(pattern, html, re.DOTALL):
            # finds the first match, copies all html before, and adds it to the result array
            result.append(html[last_end : match.start()])

            # gets the full component match group
            component_str = match.group(0)

            # try tp parse the component
            parsed = self.parse_component(component_str)
            if parsed:
                # get string name of component and its arguments
                component, arguments = parsed

                # open file and get component's required attributes
                attributes = self.get_component_attributes(component)

                # flesh out arguments based on attributes, and ensure that all the needed ones are there
                self.validate_and_complete_arguments(component, attributes, arguments)

                # process the component (yes recursion!)
                processed_content = self.preprocess_components(
                    self.render_template(component + ".jinja", **arguments, **kwargs),
                    **kwargs,
                )
                # append the processed content to the HTML result array
                result.append(processed_content)

            last_end = match.end()

        # append the remaining HTML after the last match
        result.append(html[last_end:])

        # convert array to string
        return "".join(result)

    def parse_component(self, text):
        # Pattern to match the component tag
        pattern = r"<(?P<component>[A-Z]\w*)(?P<attributes>[^>]*)>(?P<content>.*?)</\1>"
        match = re.search(pattern, text, re.DOTALL)
        if not match:
            # returns a None if no match is found, but that (probably) would literally never happen
            return None

        component = match.group("component")
        attributes_text = match.group("attributes")

        # if you try to use the keyword "content", it crashes
        # because that's the reserved keyword for the stuff between the tags!
        if "content" in attributes_text:
            raise KeyError(
                f"Reserved keyword 'content' used when calling {component}. Try changing the attribute name to 'text', 'material', or 'contents'."
            )

        # Updated pattern to match attributes with or without values
        attributes_pattern = r'([-\w]+)(?:="([^"]*)")?'
        arguments = {}
        for attr, value in re.findall(attributes_pattern, attributes_text):
            # replace hyphens with underscores
            # HTML hates underscores (at least, my syntax highlighting does)
            # and python doesn't allow hyphens in variable names
            # so, 'active-link' in HTML will become 'active_link' in Jinja
            attr = attr.replace("-", "_")
            arguments[attr] = (
                value if value else True
            )  # assign True if nothing is provided, a la HTML :)

        # add the content (stuff between the tags) to arguments, stripping whitespace
        arguments["content"] = match.group("content").strip()

        return component, arguments

    def get_component_attributes(self, component_name):
        try:
            # load component file
            jinja_env = self.env
            template_source, _, _ = jinja_env.loader.get_source(
                jinja_env, f"{component_name}.jinja"
            )
            first_line = template_source.splitlines()[0].strip()

            # look for the attributes comment
            attribute_pattern = r"^\{# attributes (.*?) #\}$"
            match = re.match(attribute_pattern, first_line)
            if not match:
                raise self.MissingAttributeList(component_name)

            # parse attributes from the comment
            attributes = {}
            for attr_def in match.group(1).split(","):
                attr_def = attr_def.strip()
                if "=" in attr_def:
                    attr, default = attr_def.split("=", 1)
                    attributes[attr.strip()] = eval(default.strip())
                else:
                    attributes[attr_def] = (
                        None  # required attribute doesn't have a default value
                    )

            return attributes
        except Exception:
            raise self.MissingAttributeList(component_name)

    def validate_and_complete_arguments(self, component, attributes, arguments):
        for attr, default in attributes.items():
            if attr not in arguments:
                if default is None:
                    raise self.MissingAttributeInCall(component, attr)
                arguments[attr] = default

    def render_template(self, name, **kwargs):
        try:
            return render_template(name, **kwargs)
        except:
            raise self.MissingComponent(name)

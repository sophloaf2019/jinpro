# jinpro

jinpro is a module that makes it easy to render custom Jinja components in HTML templates for Flask applications. It enables the use of custom component tags, which can simplify your templates and make your code more readable, and closely mimics the same functionality of Vue or React (without the reactivity, of course).

This guide will walk you through each part of the JinjaProcessor class and provide an example of how to use it in your Flask project.

## Overview

The main purpose of JinjaProcessor is to:

1. Parse custom component tags in your HTML.
2. Ensure all required attributes are passed in.
3. Render the components into full HTML using Jinja templates.

## Getting Started

To start, create an instance of JinjaProcessor and initialize it with your Flask app:

```
from flask import Flask
app = Flask(__name__)

# Initialize JinjaProcessor like this
jinja_processor = JinjaProcessor(app)

# or this
jinja_processor = JinjaProcessor()
jinja_processor.init(app)
```

You can then use `jinja_processor.render()` (directly replacing Flask's `render_template`) to render templates that contain custom tags.

## Example Usage

Let's say you have a custom component for a button that you want to use throughout your templates. Here's what the process might look like:

### Create the Component Template

In any of your templates folders, create a file called `Button.jinja` for your custom button component:

```
{# attributes content, color="blue", size="medium", non_clickable = False #}
<button class="btn btn-{{ color }} btn-{{ size }}" {% if non_clickable %} disabled {% endif %}>
    {{ content }}
</button>
```

This component expects the automatic content attribute (more on that in the exceptions section), and color and size attributes (optional, with defaults), as indicated by the commented line on the top.

This commented line is always required. At present, if you include an attribute in this list and the component is called without one of these attributes, it will throw an error. However, the component will still render attributes passed to it if they're not in the list. Components are also rendered "in context", meaning that variables and data passed to the parent `.html` template are also passed to the components.

### Use the Custom Tag in a Template
In another template, use the Button tag with your custom attributes:

```
<h1>Welcome to My Site</h1>
<Button color="green" size="large" non-clickable>Click Me</Button>
```

As you can see, the `content` attribute is missing. This is because it refers to the stuff in between the tags, and for that reason, it is "reserved".

Additionally, arguments with a hyphen, like `non-clickable`, get converted to an underscore, like `non_clickable`. HTML syntax highlighting usually doesn't like underscores in HTML, and Python doesn't allow for hyphens in variable names.

And, lastly, in typical HTML style, passing an argument without a value defaults it to True.

### Render the Template with JinjaProcessor
Now, render the parent template using JinjaProcessor, and it will replace the `<Button>` tag with the actual HTML from `Button.jinja`:

```
@app.route('/')
def home():
    html = jinja_processor.render("welcometomysite.html")
    return html
```
The rendered HTML will look like this:

```
<h1>Welcome to My Site</h1>
<button class="btn btn-green btn-large">Click Me</button>
```

JinjaProcessor scans your code to look for components first, and then scans those to look for components, and so on, until it's all out of components to find. After that, the entire page is rendered "regularly" by `render_template_string`.

The idea is that you replace all your render calls with this `.render()` function. Since it looks in the same folders and can take the same arguments, it will enable you to use components wherever you want.

For instance, instead of typing this...

```
{% extends 'base.html' %}

{% block content %}
    <p>Hi!</p>
{% endblock %}
```

You can now just type this...

```
<PageLayout>
    <p>Hi!</p>
</PageLayout>
```

### Exceptions and other notes

`MissingComponent`: Raised when the specified component file isn't found.

`MissingAttributeList`: Raised if the component template lacks a required attribute list.

`MissingAttributeInCall`: Raised if a required attribute is missing in the component call.

Additionally, it will throw a `KeyError` if the `content` attribute is used in a component. The `content` attribute is considered "reserved", and refers to the text in between the opening and closing tags.

Since the components are passed the template context and are rendered recursively, you can access page-specific variables in templates without defining them as part of your commented attributes list -- in example, if you pass a name variable to your page, you can access the name variable inside of your components without declaring it as part of the required attributes or passed components. They have a shared context.
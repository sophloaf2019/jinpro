from setuptools import setup, find_packages

setup(
    name="jinpro",  # Must be unique on PyPI
    version="1.0.2",
    description="A component preprocessor for Flask/Jinja that mimics React/Vue-style components",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Sophia Turner",
    author_email="sophia-r-turner@protonmail.com",
    url="https://github.com/sophloaf2019/jinpro",  # Your project’s URL
    packages=find_packages(),  # Automatically find packages in your project
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],

    python_requires='>=3.6',  # Adjust based on compatibility
    install_requires=[  # Dependencies, if any
        'Flask>=3',
    ],
)
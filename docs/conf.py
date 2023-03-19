# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

from ..pylav import __version__

project = 'PyLav'
copyright = '2023, Drapersniper'
author = 'Draper'
release = __version__
version = __version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.doctest",
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_context = {
    "display_github": True,
    "github_user": "PyLav",
    "github_repo": "PyLav",
    "github_version": "master/docs/",
}

source_suffix = ".rst"
master_doc = "index"


# Autodoc options
autodoc_default_options = {"show-inheritance": True}
autodoc_typehints = "none"


from docutils import nodes
from sphinx.transforms import SphinxTransform


# d.py's |coro| substitution leaks into our docs because we don't replace some of the docstrings
class IgnoreCoroSubstitution(SphinxTransform):
    default_priority = 210

    def apply(self, **kwargs) -> None:
        for ref in self.document.traverse(nodes.substitution_reference):
            if ref["refname"] == "coro":
                ref.replace_self(nodes.Text("", ""))
            elif ref["refname"] == "maybecoro":
                ref.replace_self(nodes.Text("", ""))


def setup(app):
    app.add_transform(IgnoreCoroSubstitution)
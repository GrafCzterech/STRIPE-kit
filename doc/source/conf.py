# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "STRIPE-kit"
copyright = "2025, Graf Czterech"
author = "Tomasz Chady, Jakub Markil, Patryk Olszewski, Oskar Winiarski"
release = "0.3.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_rtd_theme",
]


templates_path = ["_templates"]
exclude_patterns = []

autodoc_mock_imports = ["isaaclab", "isaacsim", "pxr", "trimesh", "gymnasium"]

latex_elements = {"extraclassoptions": "openany,oneside"}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

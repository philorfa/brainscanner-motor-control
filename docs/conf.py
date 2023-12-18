# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
sys.path.insert(0, os.path.abspath('../src'))


project = 'Motor Control'
copyright = '2023, Philippos Orfanoudakis'
author = 'Philippos Orfanoudakis'
release = '0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.napoleon',
              'sphinx.ext.intersphinx']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Napoleon configuration --------------------------------------------------

napoleon_numpy_docstring = False
napoleon_google_docstring = True


# -- Intersphinx configuration -----------------------------------------------
pyvisapy_url = 'https://pyvisa.readthedocs.io/projects/pyvisa-py/en/latest/'
intersphinx_mapping = {
    'pyvisa': ('https://pyvisa.readthedocs.io/en/latest/', None),
    'PyVISA-Py': (pyvisapy_url, None),
}
intersphinx_disabled_reftypes = ['*']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']

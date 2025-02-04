# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# import packages
import os
import sys
from datetime import datetime
#sys.path.insert(0, os.path.abspath('../IPTpy'))
#ys.path.insert(0, os.path.abspath('../src'))
#sys.path.insert(0, os.path.abspath('.'))
print("sys.path:", sys.path) # returns sys.path: ['/Users/user/Desktop/YuanSun-UoM/IPTpy/docs'
#import iptpy
# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'IPTpy'
#copyright = '2025, Yuan Sun, Zhonghua Zheng'
copyright = str(datetime.now().year)
author = 'Yuan Sun, Zhonghua Zheng'
release = "'v0.0.0'"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'recommonmark', # for markdown, similar to myst_parser
    #'myst_parser', 
    'myst_nb', # for ipynb, check 'myst_nb' or 'myst-nb' as typo
    'sphinx.ext.napoleon',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.mathjax',
    #'sphinx_markdown_tables', # not 'sphinx-markdown-tables',
    'sphinx_design', # for grid layout
    #'nbsphinx', for ipynb
    #'nbconvert' # for ipynb

]
# If you are using MyST-NB in your documentation, do not activate `myst-parser`. It will be automatically activated by `myst-nb`. Ref: https://github.com/executablebooks/MyST-NB/issues/421
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

#html_theme = 'alabaster'
html_theme = 'sphinx_book_theme'
html_static_path = ['_static']

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    "repository_url":
        "https://github.com/YuanSun-UoM/IPTpy",
    "repository_branch":
        "main",
    "path_to_docs":
        "docs",
    "use_edit_page_button":
        True,
    "use_repository_button":
        True,
    "use_issues_button":
        True,
    "home_page_in_toc":
        False,
    #"navbar_footer_text":
        #"",
    #"logo": {
        #"image_light": '_static/images/logos/NSF_NCAR_light.svg',
        #"image_dark": '_static/images/logos/NSF_NCAR_dark.svg',
    #},
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/YuanSun-UoM/IPTpy",
            "icon": "fa-brands fa-github",
        }
    ]
    #"extra_footer":
        #"<em>This material is based upon work supported by the NSF National Center for Atmospheric Research, a major facility sponsored by the U.S. National Science Foundation and managed by the University Corporation for Atmospheric Research. Any opinions, findings and conclusions or recommendations expressed in this material do not necessarily reflect the views of the U.S. National Science Foundation.</em>",
}
html_last_updated_fmt = ""
# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
source_suffix = ['.rst', '.md']
'''
source_suffix = {
    '.md': 'markdown',
    '.rst': 'restructuredtext',
    #'.ipynb': 'myst-nb',
    #'.myst': 'myst-nb',
}
'''

# jupyter_execute_notebooks = "off"
nb_execution_mode = "off"

# The master toctree document.
autosummary_generate = True
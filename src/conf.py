# Configuration file for the Sphinx documentation builder.

# -- Project information

project = 'EROFS'
copyright = '2023, EROFS filesystem developers'
author = 'EROFS filesystem developers'

version = '0.1'
release = version

# -- General configuration

extensions = [
    'myst_parser',
    'sphinx_design',
#    'sphinx.ext.duration',
#    'sphinx.ext.doctest',
#    'sphinx.ext.autodoc',
#    'sphinx.ext.autosummary',
#    'sphinx.ext.intersphinx',
]

myst_enable_extensions = ["colon_fence"]
myst_heading_anchors = 3

templates_path = ['_templates']

# -- Options for HTML output

html_static_path = ["_static"]

html_theme = 'sphinx_book_theme'
#html_theme = 'sphinx_rtd_theme'

html_logo = "_static/logo_wide.svg"
html_title = "EROFS filesystem project"

html_theme_options = {
    "home_page_in_toc": True,
    "repository_url": "https://github.com/erofs/docs",
    "repository_branch": "main",
    "path_to_docs": "src",
    "use_repository_button": True,
    "use_edit_page_button": True,
}

# -- Options for EPUB output
epub_show_urls = 'footnote'

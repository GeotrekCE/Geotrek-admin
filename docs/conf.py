import sphinx_rtd_theme # noqa
import datetime

extensions = [
    'sphinx.ext.todo',
    'sphinx_rtd_theme',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'Geotrek'
copyright = f'2013-{datetime.date.today().year}, Makina Corpus'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = '2.109'
# The full version, including alpha/beta/rc tags.
release = '2.109.0'

exclude_patterns = ['_build']

pygments_style = 'sphinx'

html_theme = 'sphinx_rtd_theme'

html_logo = "_static/logo.svg"
html_theme_options = {
    "logo_only": True,
    'style_external_links': True,
}
html_favicon = "_static/favicon.png"

html_static_path = ['_static']

# Output file base name for HTML help builder.
htmlhelp_basename = 'Geotrekdoc'

latex_documents = [
    ('index', 'Geotrek.tex', 'Geotrek Documentation',
     'Makina Corpus', 'manual'),
]

man_pages = [
    ('index', 'geotrek', 'Geotrek Documentation',
     ['Makina Corpus'], 1)
]

texinfo_documents = [
    ('index', 'Geotrek', 'Geotrek Documentation',
     'Makina Corpus', 'Geotrek', 'One line description of project.',
     'Miscellaneous'),
]

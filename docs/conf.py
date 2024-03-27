import datetime

from sphinx_pyproject import SphinxConfig


config = SphinxConfig(
    "../pyproject.toml",
    globalns=globals(),
    config_overrides={
        "copyright": f"2013-{datetime.date.today().year}, Makina Corpus",
        "html_theme_options": {
            "logo_only": True,
            "style_external_links": True,
        },
        "latex_documents": [
            (
                "index",
                "Geotrek.tex",
                "Geotrek Documentation",
                "Makina Corpus",
                "manual",
            ),
        ],
        "man_pages": [
            ("index", "geotrek", "Geotrek Documentation", ["Makina Corpus"], 1)
        ],
        "texinfo_documents": [
            (
                "index",
                "Geotrek",
                "Geotrek Documentation",
                "Makina Corpus",
                "Geotrek",
                "One line description of project.",
                "Miscellaneous",
            ),
        ],
    },
)

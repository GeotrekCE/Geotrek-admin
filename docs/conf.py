import datetime
from pathlib import Path

from sphinx_pyproject import SphinxConfig


ROOT = Path(__file__).resolve().parents[1]
version = (ROOT / "VERSION").read_text().strip()

config = SphinxConfig(
    ROOT / "pyproject.toml",
    globalns=globals(),
    config_overrides={
        "version": version,
        "release": version,
        "copyright": (
            f"2013-{datetime.date.today().year}, Makina Corpus Territoires / "
            "Parc national des Ecrins - Parc National du Mercantour - "
            "Parco delle Alpi Marittime"
        ),
        "sphinx_immaterial_custom_admonitions": [
            {
                "name": "legend",
                "color": (142, 142, 142),
                "icon": "fontawesome/solid/eye",
            },
            {
                "name": "ns-only-fr",
                "color": (72, 138, 87),
                "icon": None,
                "title": "✨ Disponible uniquement en segmentation dynamique",
            },
            {
                "name": "ns-only",
                "color": (72, 138, 87),
                "icon": None,
                "title": "✨ Only available in dynamic segmentation",
            },
            {
                "name": "ns-detail-fr",
                "color": (72, 138, 87),
                "icon": None,
                "title": "🗺️ Données stockées via segmentation dynamique lorsqu'elle est activée",
            },
            {
                "name": "ns-detail",
                "color": (72, 138, 87),
                "icon": None,
                "title": "🗺️ Data stored via dynamic segmentation when enabled",
            },
        ],
        "html_theme_options": {
            "icon": {
                "repo": "fontawesome/brands/github",
                "edit": "material/file-edit-outline",
            },
            "site_url": "https://geotrek.fr/",
            "repo_url": "https://github.com/GeotrekCE/Geotrek-admin/",
            "repo_name": "Geotrek-admin",
            "edit_uri": "tree/master/docs",
            "globaltoc_collapse": True,
            "features": [
                "navigation.expand",
                "navigation.sections",
                "navigation.top",
                "search.share",
                "toc.follow",
                "toc.sticky",
                "content.tabs.link",
                "announce.dismiss",
            ],
            "palette": [
                {
                    "media": "(prefers-color-scheme: light)",
                    "scheme": "default",
                    "primary": "green",
                    "accent": "light-green",
                    "toggle": {
                        "icon": "material/weather-night",
                        "name": "Switch to dark mode",
                    },
                },
                {
                    "media": "(prefers-color-scheme: dark)",
                    "scheme": "slate",
                    "primary": "green",
                    "accent": "light-green",
                    "toggle": {
                        "icon": "material/weather-sunny",
                        "name": "Switch to light mode",
                    },
                },
            ],
            "social": [
                {
                    "icon": "fontawesome/brands/github",
                    "link": "https://github.com/GeotrekCE/Geotrek-admin",
                },
                {
                    "icon": "fontawesome/brands/linkedin",
                    "link": "https://www.linkedin.com/company/geotrek-application",
                },
            ],
            "toc_title_is_page_title": True,
        },
        "html_css_files": ["extra_css.css"],
        "htmlhelp_basename": "Geotrekdoc",
        "latex_documents": [
            ("index", "Geotrek.tex", "Geotrek-admin Documentation", "Makina Corpus", "manual"),
        ],
        "man_pages": [("index", "geotrek", "Geotrek-admin Documentation", ["Makina Corpus"], 1)],
        "html_sidebars": {
            "**": ["logo-text.html", "globaltoc.html", "localtoc.html", "searchbox.html"],
        },
        "texinfo_documents": [
            ("index", "Geotrek", "Geotrek-admin Documentation", "Makina Corpus", "Geotrek-admin", "Miscellaneous"),
        ],
    },
)

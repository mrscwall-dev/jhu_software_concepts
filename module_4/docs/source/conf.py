import sys
from pathlib import Path


MODULE_DIR = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(MODULE_DIR),
)


project = "Grad Cafe Analytics"
copyright = "2026, Lynn Wall"
author = "Lynn Wall"
release = "1.0"


extensions = [
    "sphinx.ext.autodoc",
]


templates_path = ["_templates"]

exclude_patterns = []


html_theme = "alabaster"

html_static_path = ["_static"]
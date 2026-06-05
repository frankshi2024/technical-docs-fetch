"""Framework detection and routing gateway.

Detects which documentation framework generated an HTML page and routes
to the appropriate converter. New frameworks register here — no other
module needs modification.
"""

from .frameworks.base import BaseConverter
from .frameworks.deepwiki.converter import DeepwikiConverter
from .frameworks.mkdocs_material.converter import MkdocsMaterialConverter
from .frameworks.readthedocs.converter import ReadthedocsConverter

# ── Import version helpers for human-readable logging ────────────────────
from .frameworks.deepwiki.validator import get_version as _deepwiki_version
from .frameworks.mkdocs_material.validator import get_version as _mkdocs_version
from .frameworks.readthedocs.validator import get_version as _rtd_version


# ── Converter registry ───────────────────────────────────────────────────
# Each registered converter must implement BaseConverter.
# detect() is called in order; the first match wins.
# All detect() methods are mutually exclusive by design, so order is
# cosmetic (most common framework first for a tiny perf edge).

_CONVERTERS: list[type[BaseConverter]] = [
    MkdocsMaterialConverter,
    ReadthedocsConverter,
    DeepwikiConverter,
]

# Quick lookup: class → version function
# Used by get_framework_name() to produce human-readable log output.
_CONVERTER_NAME_MAP: dict[type[BaseConverter], str] = {
    MkdocsMaterialConverter: "mkdocs-material",
    ReadthedocsConverter: "sphinx-rtd",
    DeepwikiConverter: "deepwiki",
}


class UnsupportedFrameworkError(Exception):
    """Raised when no converter can handle the given HTML."""


def detect_framework(html: str) -> BaseConverter | None:
    """Try each registered converter; return the first matching one."""
    for cls in _CONVERTERS:
        if cls.detect(html):
            return cls()
    return None


def get_converter(html: str) -> BaseConverter:
    """Detect and return the appropriate converter, or raise an error.

    Raises:
        UnsupportedFrameworkError: If no converter matches.
    """
    converter = detect_framework(html)
    if converter is None:
        raise UnsupportedFrameworkError(
            "Error: Unsupported framework. "
            "This tool currently supports: "
            "MkDocs (Material), Read the Docs (Sphinx), DeepWiki."
        )
    return converter


def get_framework_name(html: str) -> str:
    """Return a human-readable framework + version string for logging.

    Falls back to framework class name if no version info is available.
    """
    # Try each registered converter
    for cls in _CONVERTERS:
        if cls.detect(html):
            base_name = _CONVERTER_NAME_MAP.get(cls, cls.__name__)

            # Per-framework version extraction
            if cls is MkdocsMaterialConverter:
                version = _mkdocs_version(html)
                return version if version else base_name
            elif cls is ReadthedocsConverter:
                version = _rtd_version(html)
                return version if version else base_name
            elif cls is DeepwikiConverter:
                version = _deepwiki_version(html)
                return version if version else base_name
            else:
                return base_name

    return "unknown"

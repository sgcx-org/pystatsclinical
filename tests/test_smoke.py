"""Smoke tests for the pystatsclinical package skeleton."""

import re

import pystatsclinical


def test_version_is_semver():
    assert isinstance(pystatsclinical.__version__, str)
    assert re.match(r"^\d+\.\d+\.\d+", pystatsclinical.__version__)


def test_maintainer_metadata():
    assert pystatsclinical.__author__ == "Hai-Shuo"
    assert pystatsclinical.__email__ == "contact@sgcx.org"

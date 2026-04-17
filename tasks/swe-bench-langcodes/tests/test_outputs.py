import pickle
import sys
from pathlib import Path


REPO_ROOT = Path("/app/langcodes")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from langcodes import Language


def clear_language_caches() -> None:
    Language._INSTANCES = {}
    Language._PARSE_CACHE = {}


def test_repo_exists() -> None:
    assert REPO_ROOT.exists(), "Expected repository at /app/langcodes"
    assert (REPO_ROOT / "langcodes" / "__init__.py").exists(), "Missing langcodes source tree"


def test_equal_language_objects_have_equal_hashes() -> None:
    clear_language_caches()
    en1 = Language.get("en")

    clear_language_caches()
    en2 = Language.get("en")

    assert en1 == en2
    assert hash(en1) == hash(en2)


def test_pickle_round_trip_preserves_hash() -> None:
    clear_language_caches()
    original = Language.get("en")
    loaded = pickle.loads(pickle.dumps(original))

    assert loaded == original
    assert hash(loaded) == hash(original)


def test_different_language_tags_do_not_match() -> None:
    clear_language_caches()
    en = Language.get("en")

    clear_language_caches()
    en_us = Language.get("en-US")

    assert en != en_us
    assert hash(en) != hash(en_us)

from __future__ import annotations


class Language:
    _INSTANCES: dict[str, "Language"] = {}
    _PARSE_CACHE: dict[str, str] = {}

    def __init__(self, tag: str):
        self._str_tag = tag

    @classmethod
    def normalize_tag(cls, tag: str) -> str:
        return tag.replace("_", "-")

    @classmethod
    def get(cls, tag: str) -> "Language":
        if tag in cls._INSTANCES:
            return cls._INSTANCES[tag]

        normalized = cls._PARSE_CACHE.get(tag)
        if normalized is None:
            normalized = cls.normalize_tag(tag)
            cls._PARSE_CACHE[tag] = normalized

        language = cls(normalized)
        cls._INSTANCES[tag] = language
        return language

    def __repr__(self) -> str:
        return f"Language({self._str_tag!r})"

    def __eq__(self, other):
        if not isinstance(other, Language):
            return NotImplemented
        return self._str_tag == other._str_tag

    def __hash__(self) -> int:
        return hash(id(self))

"""Schema class for Hebrew transliteration (port of hebrew-transliteration Schema)."""

from __future__ import annotations

from typing import Any, Callable, Iterable, Iterator, Mapping, MutableMapping


class Schema(MutableMapping[str, Any]):
    """Dict-like schema for mapping Hebrew orthography to transliteration output.

    Supports attribute access (``schema.PATAH``), item access (``schema["PATAH"]``),
    and ``ADDITIONAL_FEATURES`` / syllabification options used by havarot ``Text``.
    """

    def __init__(self, schema: Mapping[str, Any] | None = None) -> None:
        object.__setattr__(self, "_data", {})
        if schema:
            for key, value in schema.items():
                self[key] = value

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(name)
        try:
            return self._data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_") or name == "_data":
            object.__setattr__(self, name, value)
        else:
            self._data[name] = value

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = value

    def __delitem__(self, key: str) -> None:
        del self._data[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __contains__(self, key: object) -> bool:
        return key in self._data

    def get(self, key: str, default: Any = None) -> Any:  # type: ignore[override]
        return self._data.get(key, default)

    def keys(self) -> Iterable[str]:  # type: ignore[override]
        return self._data.keys()

    def values(self) -> Iterable[Any]:  # type: ignore[override]
        return self._data.values()

    def items(self) -> Iterable[tuple[str, Any]]:  # type: ignore[override]
        return self._data.items()

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def syl_opts(self) -> dict[str, Any]:
        """Syllabification options passed into havarot ``Text`` / ``Word``."""
        keys = (
            "allowNoNiqqud",
            "article",
            "holemHaser",
            "ketivQeres",
            "longVowels",
            "qametsQatan",
            "shevaAfterMeteg",
            "shevaWithMeteg",
            "sqnmlvy",
            "strict",
            "wawShureq",
        )
        return {k: self._data[k] for k in keys if k in self._data}


# Type alias for ADDITIONAL_FEATURES callbacks
FeatureCallback = Callable[..., str]

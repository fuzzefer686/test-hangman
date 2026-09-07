"""Vocabulary loading and random word selection."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path
import random
import unicodedata

from .game import normalise_secret_word


MINIMUM_WORD_COUNT = 30


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass(frozen=True, slots=True)
class DifficultyRule:
    min_letters: int
    max_letters: int | None
    max_wrong_guesses: int

    def accepts(self, letter_count: int) -> bool:
        return letter_count >= self.min_letters and (
            self.max_letters is None or letter_count <= self.max_letters
        )


DIFFICULTY_RULES: dict[Difficulty, DifficultyRule] = {
    Difficulty.EASY: DifficultyRule(1, 5, 6),
    Difficulty.MEDIUM: DifficultyRule(6, 8, 5),
    Difficulty.HARD: DifficultyRule(9, None, 4),
}


@dataclass(frozen=True, slots=True)
class WordEntry:
    word: str
    category: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "word", normalise_secret_word(self.word))
        category = unicodedata.normalize("NFC", self.category.strip())
        if not category:
            raise ValueError("word category must not be empty")
        object.__setattr__(self, "category", category)

    @property
    def letter_count(self) -> int:
        return sum(character.isalpha() for character in self.word)


class WordRepository:
    """Validated in-memory view of an external vocabulary file."""

    def __init__(
        self,
        entries: list[WordEntry],
        *,
        minimum_words: int = MINIMUM_WORD_COUNT,
    ) -> None:
        if len(entries) < minimum_words:
            raise ValueError(
                f"vocabulary must contain at least {minimum_words} words; "
                f"found {len(entries)}"
            )

        unique_words = {entry.word.casefold() for entry in entries}
        if len(unique_words) != len(entries):
            raise ValueError("vocabulary contains duplicate words")

        self._entries = tuple(entries)

    @classmethod
    def from_json(
        cls,
        path: str | Path,
        *,
        minimum_words: int = MINIMUM_WORD_COUNT,
    ) -> WordRepository:
        source_path = Path(path)
        try:
            payload = json.loads(source_path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise ValueError(f"vocabulary file not found: {source_path}") from exc
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid vocabulary JSON: {exc}") from exc

        rows = payload.get("words") if isinstance(payload, dict) else payload
        if not isinstance(rows, list):
            raise ValueError("vocabulary JSON must be a list or contain a 'words' list")

        entries: list[WordEntry] = []
        for index, row in enumerate(rows, start=1):
            if not isinstance(row, dict):
                raise ValueError(f"word entry #{index} must be an object")
            try:
                word = row["word"]
                category = row["category"]
            except KeyError as exc:
                raise ValueError(
                    f"word entry #{index} is missing field {exc.args[0]!r}"
                ) from exc
            if not isinstance(word, str) or not isinstance(category, str):
                raise ValueError(
                    f"word entry #{index} fields 'word' and 'category' must be strings"
                )
            entries.append(WordEntry(word=word, category=category))

        return cls(entries, minimum_words=minimum_words)

    @property
    def entries(self) -> tuple[WordEntry, ...]:
        return self._entries

    @property
    def categories(self) -> tuple[str, ...]:
        return tuple(sorted({entry.category for entry in self._entries}, key=str.casefold))

    def choose(
        self,
        *,
        difficulty: Difficulty,
        category: str | None = None,
        rng: random.Random | None = None,
    ) -> WordEntry:
        if not isinstance(difficulty, Difficulty):
            raise TypeError("difficulty must be a Difficulty value")

        category_key = category.casefold() if category is not None else None
        rule = DIFFICULTY_RULES[difficulty]
        candidates = [
            entry
            for entry in self._entries
            if (category_key is None or entry.category.casefold() == category_key)
            and rule.accepts(entry.letter_count)
        ]
        if not candidates:
            scope = f" in category {category!r}" if category is not None else ""
            raise LookupError(
                f"no {difficulty.value} vocabulary words are available{scope}"
            )

        chooser = rng or random.SystemRandom()
        return chooser.choice(candidates)


def default_vocabulary_path() -> Path:
    return Path(__file__).resolve().parent / "data" / "words.json"


def load_default_repository() -> WordRepository:
    return WordRepository.from_json(default_vocabulary_path())

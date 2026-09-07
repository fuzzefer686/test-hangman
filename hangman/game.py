"""Core Hangman domain model.

This module deliberately contains no calls to ``input`` or ``print`` so the game
rules can be reused by a console, web, or desktop interface.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import random
import unicodedata


class GameStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    WON = "won"
    LOST = "lost"


class GuessOutcome(str, Enum):
    CORRECT = "correct"
    INCORRECT = "incorrect"
    DUPLICATE = "duplicate"
    INVALID = "invalid"
    GAME_OVER = "game_over"


class InvalidGuessReason(str, Enum):
    EMPTY = "empty"
    TOO_LONG = "too_long"
    NOT_A_LETTER = "not_a_letter"


class HintOutcome(str, Enum):
    REVEALED = "revealed"
    ALREADY_USED = "already_used"
    GAME_OVER = "game_over"
    NO_HIDDEN_LETTER = "no_hidden_letter"


@dataclass(frozen=True, slots=True)
class GuessResult:
    outcome: GuessOutcome
    letter: str | None = None
    invalid_reason: InvalidGuessReason | None = None
    revealed_positions: tuple[int, ...] = ()


@dataclass(frozen=True, slots=True)
class HintResult:
    outcome: HintOutcome
    letter: str | None = None
    revealed_positions: tuple[int, ...] = ()


_VISIBLE_SEPARATORS = frozenset({" ", "-", "'", "’"})


def _letter_key(character: str) -> str:
    """Return the canonical, case-insensitive key for one letter."""

    return unicodedata.normalize("NFC", character.casefold())


def normalise_secret_word(secret_word: str) -> str:
    """Validate and NFC-normalise a word or short phrase used by the game."""

    if not isinstance(secret_word, str):
        raise TypeError("secret_word must be a string")

    word = unicodedata.normalize("NFC", secret_word.strip())
    if not word:
        raise ValueError("secret_word must not be empty")

    if not any(character.isalpha() for character in word):
        raise ValueError("secret_word must contain at least one letter")

    for character in word:
        if not character.isalpha() and character not in _VISIBLE_SEPARATORS:
            raise ValueError(
                "secret_word may contain only letters, spaces, hyphens, and apostrophes"
            )
        if character.isalpha() and len(_letter_key(character)) != 1:
            raise ValueError(
                f"letter {character!r} cannot be represented by a one-letter guess"
            )

    return word


def _normalise_guess(
    raw_guess: str,
) -> tuple[str | None, InvalidGuessReason | None]:
    if not isinstance(raw_guess, str):
        return None, InvalidGuessReason.NOT_A_LETTER

    stripped = raw_guess.strip()
    if not stripped:
        return None, InvalidGuessReason.EMPTY

    guess = _letter_key(unicodedata.normalize("NFC", stripped))
    if len(guess) != 1:
        return None, InvalidGuessReason.TOO_LONG
    if not guess.isalpha():
        return None, InvalidGuessReason.NOT_A_LETTER

    return guess, None


class HangmanGame:
    """Stateful, interface-independent implementation of Hangman rules."""

    def __init__(
        self,
        secret_word: str,
        *,
        max_wrong_guesses: int = 6,
        rng: random.Random | None = None,
    ) -> None:
        if isinstance(max_wrong_guesses, bool) or not isinstance(
            max_wrong_guesses, int
        ):
            raise TypeError("max_wrong_guesses must be an integer")
        if max_wrong_guesses <= 0:
            raise ValueError("max_wrong_guesses must be greater than zero")

        self._secret_word = normalise_secret_word(secret_word)
        self._max_wrong_guesses = max_wrong_guesses
        self._guessed_letters: set[str] = set()
        self._incorrect_guesses: set[str] = set()
        self._hint_penalties = 0
        self._hint_used = False
        self._rng = rng or random.Random()

    @property
    def secret_word(self) -> str:
        return self._secret_word

    @property
    def max_wrong_guesses(self) -> int:
        return self._max_wrong_guesses

    @property
    def guessed_letters(self) -> tuple[str, ...]:
        return tuple(sorted(self._guessed_letters))

    @property
    def incorrect_guesses(self) -> tuple[str, ...]:
        return tuple(sorted(self._incorrect_guesses))

    @property
    def attempts_used(self) -> int:
        return len(self._incorrect_guesses) + self._hint_penalties

    @property
    def remaining_attempts(self) -> int:
        return max(0, self._max_wrong_guesses - self.attempts_used)

    @property
    def hint_used(self) -> bool:
        return self._hint_used

    @property
    def visible_characters(self) -> tuple[str, ...]:
        return tuple(
            character
            if not character.isalpha()
            or _letter_key(character) in self._guessed_letters
            else "_"
            for character in self._secret_word
        )

    @property
    def masked_word(self) -> str:
        """Return a UI-ready word state with a space between each character."""

        return " ".join(self.visible_characters)

    @property
    def status(self) -> GameStatus:
        # A hint can consume the final attempt while revealing the final letter.
        # Completing the word takes precedence in that edge case.
        if all(
            not character.isalpha()
            or _letter_key(character) in self._guessed_letters
            for character in self._secret_word
        ):
            return GameStatus.WON
        if self.remaining_attempts == 0:
            return GameStatus.LOST
        return GameStatus.IN_PROGRESS

    def guess(self, raw_guess: str) -> GuessResult:
        """Apply one letter guess and return a structured result."""

        if self.status is not GameStatus.IN_PROGRESS:
            return GuessResult(GuessOutcome.GAME_OVER)

        letter, invalid_reason = _normalise_guess(raw_guess)
        if invalid_reason is not None:
            return GuessResult(
                GuessOutcome.INVALID,
                invalid_reason=invalid_reason,
            )

        assert letter is not None
        if letter in self._guessed_letters:
            return GuessResult(GuessOutcome.DUPLICATE, letter=letter)

        self._guessed_letters.add(letter)
        positions = tuple(
            index
            for index, character in enumerate(self._secret_word)
            if character.isalpha() and _letter_key(character) == letter
        )

        if positions:
            return GuessResult(
                GuessOutcome.CORRECT,
                letter=letter,
                revealed_positions=positions,
            )

        self._incorrect_guesses.add(letter)
        return GuessResult(GuessOutcome.INCORRECT, letter=letter)

    def use_hint(self) -> HintResult:
        """Reveal one random hidden letter and charge one remaining attempt."""

        if self.status is not GameStatus.IN_PROGRESS:
            return HintResult(HintOutcome.GAME_OVER)
        if self._hint_used:
            return HintResult(HintOutcome.ALREADY_USED)

        hidden_letters = list(
            dict.fromkeys(
                _letter_key(character)
                for character in self._secret_word
                if character.isalpha()
                and _letter_key(character) not in self._guessed_letters
            )
        )
        if not hidden_letters:
            return HintResult(HintOutcome.NO_HIDDEN_LETTER)

        letter = self._rng.choice(hidden_letters)
        self._guessed_letters.add(letter)
        self._hint_penalties += 1
        self._hint_used = True
        positions = tuple(
            index
            for index, character in enumerate(self._secret_word)
            if character.isalpha() and _letter_key(character) == letter
        )
        return HintResult(
            HintOutcome.REVEALED,
            letter=letter,
            revealed_positions=positions,
        )

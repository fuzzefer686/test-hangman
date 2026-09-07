import random
import unittest

from hangman.game import (
    GameStatus,
    GuessOutcome,
    HangmanGame,
    HintOutcome,
    InvalidGuessReason,
)


class HangmanGameTests(unittest.TestCase):
    def test_correct_guess_reveals_every_occurrence_without_penalty(self) -> None:
        game = HangmanGame("banana")

        result = game.guess("A")

        self.assertEqual(result.outcome, GuessOutcome.CORRECT)
        self.assertEqual(result.revealed_positions, (1, 3, 5))
        self.assertEqual(game.masked_word, "_ a _ a _ a")
        self.assertEqual(game.remaining_attempts, 6)

    def test_incorrect_guess_deducts_one_attempt_and_is_recorded(self) -> None:
        game = HangmanGame("mèo", max_wrong_guesses=3)

        result = game.guess("x")

        self.assertEqual(result.outcome, GuessOutcome.INCORRECT)
        self.assertEqual(game.incorrect_guesses, ("x",))
        self.assertEqual(game.remaining_attempts, 2)

    def test_duplicate_guess_is_case_insensitive_and_has_no_penalty(self) -> None:
        game = HangmanGame("Mèo")
        game.guess("m")
        attempts_before_duplicate = game.remaining_attempts

        result = game.guess(" M ")

        self.assertEqual(result.outcome, GuessOutcome.DUPLICATE)
        self.assertEqual(game.remaining_attempts, attempts_before_duplicate)
        self.assertEqual(game.guessed_letters, ("m",))

    def test_invalid_inputs_do_not_change_state_or_deduct_attempts(self) -> None:
        game = HangmanGame("mèo")
        cases = (
            ("", InvalidGuessReason.EMPTY),
            ("   ", InvalidGuessReason.EMPTY),
            ("ab", InvalidGuessReason.TOO_LONG),
            ("7", InvalidGuessReason.NOT_A_LETTER),
        )

        for raw_guess, expected_reason in cases:
            with self.subTest(raw_guess=raw_guess):
                result = game.guess(raw_guess)
                self.assertEqual(result.outcome, GuessOutcome.INVALID)
                self.assertEqual(result.invalid_reason, expected_reason)
                self.assertEqual(game.remaining_attempts, 6)
                self.assertEqual(game.guessed_letters, ())

    def test_player_wins_after_revealing_all_letters(self) -> None:
        game = HangmanGame("mẹ")

        game.guess("M")
        final_result = game.guess("ẹ")

        self.assertEqual(final_result.outcome, GuessOutcome.CORRECT)
        self.assertEqual(game.status, GameStatus.WON)
        self.assertEqual(game.masked_word, "m ẹ")

    def test_player_loses_after_maximum_wrong_guesses(self) -> None:
        game = HangmanGame("mèo", max_wrong_guesses=2)

        game.guess("x")
        game.guess("y")

        self.assertEqual(game.status, GameStatus.LOST)
        self.assertEqual(game.remaining_attempts, 0)
        self.assertEqual(game.secret_word, "mèo")

    def test_guess_after_game_over_does_not_mutate_game(self) -> None:
        game = HangmanGame("a", max_wrong_guesses=1)
        game.guess("x")

        result = game.guess("a")

        self.assertEqual(result.outcome, GuessOutcome.GAME_OVER)
        self.assertEqual(game.guessed_letters, ("x",))
        self.assertEqual(game.status, GameStatus.LOST)

    def test_unicode_combining_guess_is_normalised(self) -> None:
        game = HangmanGame("é")

        result = game.guess("e\u0301")

        self.assertEqual(result.outcome, GuessOutcome.CORRECT)
        self.assertEqual(game.status, GameStatus.WON)

    def test_spaces_and_hyphens_are_visible_without_guessing(self) -> None:
        game = HangmanGame("cá-mập trắng")

        self.assertEqual(game.visible_characters[2], "-")
        self.assertEqual(game.visible_characters[6], " ")
        self.assertEqual(game.remaining_attempts, 6)

    def test_hint_reveals_a_letter_only_once_and_costs_one_attempt(self) -> None:
        game = HangmanGame("abc", rng=random.Random(7))

        first_result = game.use_hint()
        attempts_after_first_hint = game.remaining_attempts
        second_result = game.use_hint()

        self.assertEqual(first_result.outcome, HintOutcome.REVEALED)
        self.assertIn(first_result.letter, {"a", "b", "c"})
        self.assertEqual(attempts_after_first_hint, 5)
        self.assertEqual(second_result.outcome, HintOutcome.ALREADY_USED)
        self.assertEqual(game.remaining_attempts, attempts_after_first_hint)

    def test_hint_on_final_attempt_wins_if_it_completes_word(self) -> None:
        game = HangmanGame("a", max_wrong_guesses=1)

        result = game.use_hint()

        self.assertEqual(result.outcome, HintOutcome.REVEALED)
        self.assertEqual(game.remaining_attempts, 0)
        self.assertEqual(game.status, GameStatus.WON)

    def test_constructor_rejects_invalid_secret_or_attempt_limit(self) -> None:
        with self.assertRaises(ValueError):
            HangmanGame("")
        with self.assertRaises(ValueError):
            HangmanGame("abc1")
        with self.assertRaises(ValueError):
            HangmanGame("abc", max_wrong_guesses=0)


if __name__ == "__main__":
    unittest.main()

import random
import unittest

from hangman.cli import run
from hangman.words import WordEntry, WordRepository


class ConsoleIntegrationTests(unittest.TestCase):
    def test_complete_console_game_and_decline_replay(self) -> None:
        repository = WordRepository(
            [WordEntry("mèo", "Động vật")],
            minimum_words=1,
        )
        answers = iter(("0", "1", "m", "è", "o", "k"))
        output: list[str] = []

        run(
            repository=repository,
            rng=random.Random(1),
            input_fn=lambda _prompt: next(answers),
            output=output.append,
        )

        transcript = "\n".join(output)
        self.assertIn("Bạn thắng! Từ bí mật là: mèo", transcript)
        self.assertIn("Cảm ơn bạn đã chơi!", transcript)


if __name__ == "__main__":
    unittest.main()

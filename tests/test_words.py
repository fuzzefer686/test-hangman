import random
import unittest

from hangman.words import (
    DIFFICULTY_RULES,
    MINIMUM_WORD_COUNT,
    Difficulty,
    WordEntry,
    WordRepository,
    load_default_repository,
)


class WordRepositoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repository = load_default_repository()

    def test_default_vocabulary_has_at_least_30_unique_words(self) -> None:
        words = [entry.word.casefold() for entry in self.repository.entries]

        self.assertGreaterEqual(len(words), MINIMUM_WORD_COUNT)
        self.assertEqual(len(words), len(set(words)))

    def test_every_category_supports_every_difficulty(self) -> None:
        rng = random.Random(42)

        for category in self.repository.categories:
            for difficulty, rule in DIFFICULTY_RULES.items():
                with self.subTest(category=category, difficulty=difficulty):
                    entry = self.repository.choose(
                        category=category,
                        difficulty=difficulty,
                        rng=rng,
                    )
                    self.assertEqual(entry.category, category)
                    self.assertTrue(rule.accepts(entry.letter_count))

    def test_repository_rejects_too_few_words(self) -> None:
        with self.assertRaises(ValueError):
            WordRepository([WordEntry("mèo", "Động vật")])

    def test_choose_requires_difficulty_enum(self) -> None:
        with self.assertRaises(TypeError):
            self.repository.choose(difficulty="easy")  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()

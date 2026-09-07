class HangmanGame:
    """Phần luật chơi Hangman, không phụ thuộc input hoặc print."""

    MAX_WRONG_GUESSES = 6

    def __init__(self, secret_word):
        word = secret_word.strip().lower()
        if not word or not word.isalpha():
            raise ValueError("Từ bí mật phải chỉ chứa chữ cái")

        self.secret_word = word
        self.guessed_letters = set()
        self.wrong_letters = set()

    @property
    def remaining_turns(self):
        return self.MAX_WRONG_GUESSES - len(self.wrong_letters)

    @property
    def word_state(self):
        return " ".join(
            letter if letter in self.guessed_letters else "_"
            for letter in self.secret_word
        )

    @property
    def is_won(self):
        return all(letter in self.guessed_letters for letter in self.secret_word)

    @property
    def is_lost(self):
        return self.remaining_turns == 0 and not self.is_won

    @property
    def is_over(self):
        return self.is_won or self.is_lost

    def guess(self, value):
        """Đoán một chữ và trả về trạng thái của lượt đoán."""

        if self.is_over:
            return "game_over"

        letter = value.strip().lower()
        if len(letter) != 1 or not letter.isalpha():
            return "invalid"
        if letter in self.guessed_letters:
            return "duplicate"

        self.guessed_letters.add(letter)
        if letter in self.secret_word:
            return "correct"

        self.wrong_letters.add(letter)
        return "wrong"

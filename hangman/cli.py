"""Vietnamese command-line interface for the Hangman game."""

from __future__ import annotations

import random
from typing import Callable

from .game import (
    GameStatus,
    GuessOutcome,
    GuessResult,
    HangmanGame,
    HintOutcome,
    HintResult,
    InvalidGuessReason,
)
from .words import (
    DIFFICULTY_RULES,
    Difficulty,
    WordRepository,
    load_default_repository,
)


InputFn = Callable[[str], str]
OutputFn = Callable[[str], None]


_DIFFICULTY_LABELS = {
    Difficulty.EASY: "Dễ (1-5 chữ cái, 6 lượt sai)",
    Difficulty.MEDIUM: "Trung bình (6-8 chữ cái, 5 lượt sai)",
    Difficulty.HARD: "Khó (từ 9 chữ cái, 4 lượt sai)",
}


def _format_letters(letters: tuple[str, ...]) -> str:
    return ", ".join(letters) if letters else "(chưa có)"


def _show_state(game: HangmanGame, output: OutputFn) -> None:
    output("")
    output(f"Từ bí mật:          {game.masked_word}")
    output(f"Các chữ đã đoán:    {_format_letters(game.guessed_letters)}")
    output(f"Các chữ đoán sai:   {_format_letters(game.incorrect_guesses)}")
    output(
        "Lượt sai còn lại:   "
        f"{game.remaining_attempts}/{game.max_wrong_guesses}"
    )
    hint_state = "đã dùng" if game.hint_used else "còn 1 lần (nhập ?)"
    output(f"Gợi ý:              {hint_state}")


def _describe_guess(result: GuessResult) -> str:
    if result.outcome is GuessOutcome.CORRECT:
        return f"Chính xác! Có chữ {result.letter!r} trong từ."
    if result.outcome is GuessOutcome.INCORRECT:
        return f"Chưa đúng. Không có chữ {result.letter!r}; bạn mất 1 lượt."
    if result.outcome is GuessOutcome.DUPLICATE:
        return f"Bạn đã đoán chữ {result.letter!r} rồi; lượt không bị trừ."
    if result.outcome is GuessOutcome.GAME_OVER:
        return "Ván chơi đã kết thúc."

    invalid_messages = {
        InvalidGuessReason.EMPTY: "Hãy nhập một chữ cái; lượt không bị trừ.",
        InvalidGuessReason.TOO_LONG: "Chỉ được nhập đúng một chữ cái; lượt không bị trừ.",
        InvalidGuessReason.NOT_A_LETTER: "Ký tự nhập vào phải là chữ cái; lượt không bị trừ.",
    }
    return invalid_messages[result.invalid_reason]


def _describe_hint(result: HintResult) -> str:
    if result.outcome is HintOutcome.REVEALED:
        return f"Gợi ý đã mở chữ {result.letter!r} và trừ 1 lượt."
    if result.outcome is HintOutcome.ALREADY_USED:
        return "Bạn đã dùng gợi ý trong ván này; lượt không bị trừ."
    if result.outcome is HintOutcome.GAME_OVER:
        return "Ván chơi đã kết thúc."
    return "Không còn chữ ẩn để gợi ý."


def _choose_category(
    repository: WordRepository,
    input_fn: InputFn,
    output: OutputFn,
) -> str | None:
    categories = repository.categories
    while True:
        output("\nChọn chủ đề:")
        output("  0. Tất cả chủ đề")
        for index, category in enumerate(categories, start=1):
            output(f"  {index}. {category}")

        answer = input_fn("Lựa chọn [0]: ").strip()
        if answer in {"", "0"}:
            return None
        if answer.isdigit() and 1 <= int(answer) <= len(categories):
            return categories[int(answer) - 1]
        output("Lựa chọn chủ đề không hợp lệ. Vui lòng thử lại.")


def _choose_difficulty(input_fn: InputFn, output: OutputFn) -> Difficulty:
    choices = tuple(Difficulty)
    while True:
        output("\nChọn độ khó:")
        for index, difficulty in enumerate(choices, start=1):
            output(f"  {index}. {_DIFFICULTY_LABELS[difficulty]}")

        answer = input_fn("Lựa chọn [2]: ").strip()
        if answer == "":
            return Difficulty.MEDIUM
        if answer.isdigit() and 1 <= int(answer) <= len(choices):
            return choices[int(answer) - 1]
        output("Lựa chọn độ khó không hợp lệ. Vui lòng thử lại.")


def _ask_to_play_again(input_fn: InputFn, output: OutputFn) -> bool:
    yes_answers = {"c", "co", "có", "y", "yes"}
    no_answers = {"", "k", "khong", "không", "n", "no"}
    while True:
        answer = input_fn("\nBạn có muốn chơi lại không? [c/K]: ").strip().casefold()
        if answer in yes_answers:
            return True
        if answer in no_answers:
            return False
        output("Vui lòng nhập 'c' (có) hoặc 'k' (không).")


def run(
    *,
    repository: WordRepository | None = None,
    rng: random.Random | None = None,
    input_fn: InputFn = input,
    output: OutputFn = print,
) -> None:
    """Run the interactive game; dependencies are injectable for testing."""

    repository = repository or load_default_repository()
    rng = rng or random.Random()

    output("=" * 46)
    output("         ĐOÁN CHỮ - HANGMAN")
    output("=" * 46)
    output("Đoán từng chữ cái. Nhập ? để dùng gợi ý một lần.")

    while True:
        category = _choose_category(repository, input_fn, output)
        difficulty = _choose_difficulty(input_fn, output)
        selected_word = repository.choose(
            difficulty=difficulty,
            category=category,
            rng=rng,
        )
        rule = DIFFICULTY_RULES[difficulty]
        game = HangmanGame(
            selected_word.word,
            max_wrong_guesses=rule.max_wrong_guesses,
            rng=rng,
        )

        category_label = category or "Tất cả"
        output(
            f"\nBắt đầu ván mới - Chủ đề: {category_label}; "
            f"Độ khó: {_DIFFICULTY_LABELS[difficulty]}"
        )

        while game.status is GameStatus.IN_PROGRESS:
            _show_state(game, output)
            raw_guess = input_fn("\nNhập một chữ cái (hoặc ? để gợi ý): ")
            if raw_guess.strip() == "?":
                output(_describe_hint(game.use_hint()))
            else:
                output(_describe_guess(game.guess(raw_guess)))

        _show_state(game, output)
        if game.status is GameStatus.WON:
            output(f"\nBạn thắng! Từ bí mật là: {game.secret_word}")
        else:
            output(f"\nBạn thua. Từ bí mật là: {game.secret_word}")

        if not _ask_to_play_again(input_fn, output):
            output("Cảm ơn bạn đã chơi!")
            return


def main() -> None:
    try:
        run()
    except (EOFError, KeyboardInterrupt):
        print("\nĐã thoát trò chơi. Hẹn gặp lại!")


if __name__ == "__main__":
    main()

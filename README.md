# Trò chơi Đoán chữ (Hangman)

Bản Python console tối thiểu, chỉ triển khai các yêu cầu bắt buộc của đề bài.

## Cài đặt và chạy

Yêu cầu Python 3. Không cần cài thư viện ngoài.

```bash
python3 main.py
```

## Chạy test

```bash
python3 -m unittest -v
```

Có 7 unit test, bao gồm 5 trường hợp bắt buộc: đoán đúng, đoán sai, đoán trùng, thắng và thua.

## Cấu trúc

- `game.py`: luật chơi độc lập, không dùng `input` hoặc `print`.
- `main.py`: giao diện console và chọn từ ngẫu nhiên.
- `words.txt`: danh sách 30 từ riêng biệt.
- `test_game.py`: unit test cho phần logic.

## Quyết định thiết kế

- Mỗi ván có đúng 6 lượt đoán sai.
- Tất cả từ trong `words.txt` là một từ tiếng Anh chỉ gồm chữ cái để phần xử lý đơn giản nhất.
- Chữ hoa và chữ thường được chuyển về chữ thường trước khi so sánh.
- Input không hợp lệ và chữ đã đoán không bị trừ lượt.
- Không triển khai các mục nâng cao vì đây là phiên bản tối thiểu.

## Nếu có thêm thời gian

Có thể thêm độ khó, gợi ý, chủ đề, điểm số, từ tiếng Việt và giao diện web.

## Sử dụng AI

OpenAI Codex được dùng để hỗ trợ đọc đề, tạo mã nguồn, unit test và README. Người nộp bài cần đọc và hiểu toàn bộ mã trước khi trình bày.

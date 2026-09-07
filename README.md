# Trò chơi Đoán chữ (Hangman)

Ứng dụng Hangman chạy trên terminal, viết bằng Python thuần. Dự án ưu tiên phần luật chơi dễ kiểm thử và không phụ thuộc giao diện; giao diện console chỉ có nhiệm vụ nhận input và hiển thị kết quả.

## Chức năng

- Chọn ngẫu nhiên từ kho 45 từ trong file JSON riêng, chia theo 3 chủ đề.
- Hiển thị trạng thái từ, toàn bộ chữ đã đoán, chữ đoán sai và số lượt còn lại sau mỗi lượt.
- Không trừ lượt khi input rỗng, dài hơn một ký tự, không phải chữ cái hoặc đã đoán trước đó.
- So khớp không phân biệt hoa/thường.
- Thông báo thắng/thua, công khai từ bí mật và hỏi chơi lại.
- Ba độ khó, ảnh hưởng đến độ dài từ và số lượt sai được phép.
- Một gợi ý mỗi ván: mở một chữ cái ngẫu nhiên và mất một lượt.
- Chọn chủ đề: Động vật, Đồ vật, Nghề nghiệp hoặc tất cả.
- Hỗ trợ chữ cái tiếng Việt có dấu.

## Yêu cầu môi trường

- Python 3.10 trở lên.
- Không có thư viện bên thứ ba; không cần chạy `pip install`.

Kiểm tra phiên bản Python:

```bash
python3 --version
```

## Cách chạy

Từ thư mục gốc của dự án:

```bash
python3 main.py
```

Hoặc chạy package trực tiếp:

```bash
python3 -m hangman
```

Trong ván chơi, nhập một chữ cái để đoán hoặc nhập `?` để dùng gợi ý.

## Cách chạy test

```bash
python3 -m unittest discover -s tests -v
```

Bộ test bao phủ các tình huống bắt buộc: đoán đúng, đoán sai, đoán trùng, thắng, thua; đồng thời kiểm tra input không hợp lệ, Unicode, gợi ý, dữ liệu từ vựng và một luồng console hoàn chỉnh.

## Cấu trúc dự án

```text
.
├── hangman/
│   ├── game.py          # Luật chơi thuần, không dùng input/print
│   ├── words.py         # Đọc, kiểm tra và chọn từ từ JSON
│   ├── cli.py           # Giao diện terminal
│   └── data/words.json  # 45 từ vựng, không hard-code trong logic
├── tests/               # Unit test và integration test console
├── main.py              # Điểm chạy thuận tiện
└── README.md
```

## Quyết định thiết kế

### Tách logic và giao diện

`HangmanGame` không gọi `input()` hoặc `print()`. Phương thức `guess()` và `use_hint()` nhận dữ liệu, cập nhật state rồi trả về các result object có kiểu rõ ràng. Vì vậy có thể tái sử dụng nguyên logic này cho web/desktop và test mà không giả lập terminal.

`cli.py` chuyển các result object thành câu tiếng Việt và điều phối vòng lặp chơi. Các hàm input/output cũng được inject để luồng console có thể kiểm thử tự động.

### Độ khó

| Mức | Độ dài từ (chỉ đếm chữ cái) | Số lượt sai tối đa |
| --- | ---: | ---: |
| Dễ | 1-5 | 6 |
| Trung bình | 6-8 | 5 |
| Khó | Từ 9 | 4 |

Mọi mức đều không vượt quá giới hạn 6 lượt sai trong đề. Kho dữ liệu bảo đảm mỗi tổ hợp chủ đề/độ khó đều có từ để chọn.

### Unicode tiếng Việt

- Cả từ bí mật và input được chuẩn hóa về Unicode NFC để `é` dạng ký tự dựng sẵn và `e` + dấu kết hợp được coi là một chữ.
- So khớp bằng `casefold()`, do đó hoa/thường được xem như nhau.
- Dấu thanh là một phần của chữ: `e`, `è`, `é` là các lượt đoán khác nhau. Chữ `đ` cũng khác `d`.
- Khoảng trắng, dấu gạch nối và dấu nháy trong cụm từ được lộ sẵn; người chơi chỉ cần đoán chữ cái.

Cách so khớp giữ nguyên dấu được chọn vì rõ ràng, không làm nhiều chữ khác nhau cùng khớp vào một lượt đoán và phù hợp quy tắc “mỗi dấu gạch dưới tương ứng một ký tự”.

### Các giả định ở điểm mơ hồ

- Chữ đã đoán bao gồm cả chữ đúng lẫn chữ sai. Đoán lại bất kỳ chữ nào đều không bị trừ lượt.
- Gợi ý chỉ được dùng thành công một lần và tiêu tốn một lượt giống như một lần đoán sai, nhưng chữ được mở không nằm trong danh sách “đoán sai”.
- Nếu gợi ý vừa dùng lượt cuối vừa mở chữ cuối cùng, người chơi thắng vì đã hoàn thành từ.
- Chọn sai menu chủ đề/độ khó không phải một lượt chơi và được yêu cầu nhập lại.

## Nếu có thêm thời gian

- Thêm điểm số, tên người chơi và bảng xếp hạng lưu bền vững (A4).
- Xây dựng giao diện web responsive và hỗ trợ bàn phím ảo (A6).
- Mở rộng kho từ, thêm mô tả gợi ý theo nghĩa thay vì chỉ mở chữ.
- Thêm kiểm thử property-based và báo cáo coverage tự động trong CI.

## Việc sử dụng AI

OpenAI Codex được dùng để hỗ trợ đọc/diễn giải đề bài, đề xuất cấu trúc, viết mã nguồn ban đầu, unit test và tài liệu README. Người nộp bài cần tự đọc, chạy thử và hiểu toàn bộ mã trước khi trình bày hoặc tiếp tục phát triển.

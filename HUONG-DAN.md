# Hướng dẫn sử dụng Selenium Automation Hub

## Giới thiệu

Đây là công cụ tự động hóa web sử dụng Selenium WebDriver với Brave Browser, hỗ trợ các tác vụ như tìm kiếm Google, truy cập Facebook, và thu thập dữ liệu từ Shopee.

## Yêu cầu hệ thống

- Python 3.6+
- Brave Browser đã được cài đặt
- Windows 10/11 (hoặc Linux/macOS với một số điều chỉnh đường dẫn)

## Cài đặt

1. Cài đặt Brave Browser từ [trang chủ Brave](https://brave.com/download/)
2. Cài đặt các thư viện Python cần thiết:

```
pip install -r requirements.txt
```

## Cách sử dụng

### Chạy từ dòng lệnh

Mở terminal (Command Prompt hoặc PowerShell) và chạy:

```
python run_brave_automation.py --task LOAI_TAC_VU --keyword TU_KHOA
```

Trong đó:
- `LOAI_TAC_VU` là một trong các giá trị: `google`, `facebook`, `shopee`
- `TU_KHOA` là từ khóa tìm kiếm (cần thiết cho Google và Shopee)

### Các tùy chọn khác

- `--headless` hoặc `-l`: Chạy ở chế độ ẩn (không hiển thị giao diện)
- `--keep-open` hoặc `-o`: Giữ trình duyệt mở sau khi hoàn thành

### Ví dụ cụ thể

1. **Tìm kiếm Google với từ khóa "python automation"**:

```
python run_brave_automation.py --task google --keyword "python automation"
```

2. **Tìm kiếm Shopee với từ khóa "laptop" và giữ trình duyệt mở**:

```
python run_brave_automation.py --task shopee --keyword "laptop" --keep-open
```

3. **Tìm kiếm Google ở chế độ headless (không hiển thị giao diện)**:

```
python run_brave_automation.py --task google --keyword "selenium python" --headless
```

4. **Truy cập Facebook sử dụng profile đã đăng nhập**:

```
python run_brave_automation.py --task facebook
```

## Xử lý sự cố

1. **Không tìm thấy Brave Browser**
   - Kiểm tra đường dẫn cài đặt Brave
   - Mặc định: `C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe`

2. **Lỗi ChromeDriver**
   - Đảm bảo máy tính có kết nối internet để tải driver
   - Thử chạy lại script

3. **Không thu thập được kết quả**
   - Có thể do cấu trúc trang web đã thay đổi
   - Liên hệ người phát triển để cập nhật

4. **Lỗi đăng nhập Facebook**
   - Mở Brave, đăng nhập vào Facebook thủ công
   - Sau đó chạy lại script để sử dụng profile đã đăng nhập

## Lưu ý

- Công cụ này sử dụng profile Brave của bạn để duy trì phiên đăng nhập
- Nếu bạn đã đăng nhập vào Facebook, Shopee... trong Brave, công cụ sẽ tự động sử dụng thông tin đăng nhập đó
- Các cài đặt đường dẫn profile mặc định: `C:\Users\<tên người dùng>\AppData\Local\BraveSoftware\Brave-Browser\User Data\Default` 
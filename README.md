# Selenium Automation Hub với Brave Browser

Công cụ tự động hóa web sử dụng Selenium WebDriver với Brave Browser, hỗ trợ các tác vụ như tìm kiếm Google, truy cập Facebook, và thu thập dữ liệu từ Shopee.

## Yêu cầu

- Python 3.6+
- Brave Browser đã cài đặt ([Tải tại đây](https://brave.com/download/))
- Các thư viện Python cần thiết (xem `requirements.txt`)

## Cài đặt

1. Clone hoặc tải về repository này
2. Cài đặt các thư viện cần thiết:

```bash
pip install -r requirements.txt
```

## Cách sử dụng

### Chạy qua giao diện dòng lệnh

```bash
python run_brave_automation.py [OPTIONS]
```

Các tùy chọn:

- `--task`, `-t`: Loại tác vụ (`google`, `facebook`, `shopee`), mặc định: `google`
- `--keyword`, `-k`: Từ khóa tìm kiếm
- `--headless`, `-l`: Chạy ở chế độ headless (không hiển thị giao diện)
- `--keep-open`, `-o`: Giữ trình duyệt mở sau khi hoàn thành

### Ví dụ

1. Tìm kiếm Google:

```bash
python run_brave_automation.py --task google --keyword "python automation"
```

2. Tìm kiếm Shopee và giữ trình duyệt mở:

```bash
python run_brave_automation.py --task shopee --keyword "laptop gaming" --keep-open
```

3. Tìm kiếm Google ở chế độ headless:

```bash
python run_brave_automation.py --task google --keyword "selenium python" --headless
```

4. Truy cập Facebook:

```bash
python run_brave_automation.py --task facebook
```

## Chức năng

### 1. Tìm kiếm Google
- Tự động truy cập Google
- Thực hiện tìm kiếm với từ khóa được cung cấp
- Thu thập và hiển thị kết quả tìm kiếm

### 2. Truy cập Facebook
- Tự động truy cập Facebook
- Sử dụng profile Brave đã lưu để đăng nhập (nếu có)
- Kiểm tra trạng thái đăng nhập

### 3. Tìm kiếm Shopee
- Tự động truy cập Shopee
- Đóng popup (nếu có)
- Thực hiện tìm kiếm sản phẩm
- Thu thập và hiển thị thông tin sản phẩm

## Tính năng đặc biệt

- **Chống phát hiện automation**: Sử dụng các kỹ thuật để tránh bị phát hiện là bot
- **Hỗ trợ profile**: Sử dụng profile Brave đã có sẵn để duy trì trạng thái đăng nhập
- **Chế độ headless**: Chạy tự động không cần hiển thị giao diện
- **Tùy chọn giữ trình duyệt mở**: Cho phép kiểm tra kết quả sau khi chạy

## Ghi chú

- Script này được thiết kế để hoạt động với Brave Browser. Nếu bạn muốn sử dụng trình duyệt khác, hãy chỉnh sửa đường dẫn binary và các tùy chọn phù hợp.
- Đảm bảo rằng bạn đã cài đặt Brave Browser trước khi chạy script.
- Các cấu trúc HTML của trang web có thể thay đổi theo thời gian, có thể cần cập nhật selectors nếu script không hoạt động như mong đợi.

## Giải quyết vấn đề

1. **Không tìm thấy Brave Browser**: Kiểm tra đường dẫn cài đặt hoặc cài đặt lại Brave
2. **Lỗi ChromeDriver**: Đảm bảo đã cài đặt `webdriver-manager` và có kết nối internet để tải driver
3. **Không thu thập được kết quả**: Selectors có thể đã thay đổi, cần điều chỉnh CSS selectors hoặc XPath
4. **Lỗi đăng nhập**: Đảm bảo profile Brave đã được đăng nhập trước khi chạy script

## Cấu trúc dự án 
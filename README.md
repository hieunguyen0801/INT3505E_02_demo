# INT3505E_02_NguyenTrungHieu_demo_01
BT demo cá nhân môn Kiến Trúc Hướng Dịch Vụ
# Flask Library Demo
Quản lý sách + mượn/trả (Flask 3, Python 3.13, SQLite).

## Tính năng
- Thêm/xem sách: `title, author, year, shelf_code, location_url`
- Mượn/Trả (mỗi sách một bản duy nhất), hiển thị hạn trả
- Xoá sách (chỉ khi không có mượn đang mở)
- Chống thêm trùng (title+author+year) ở **app** và **DB**

## Chạy (Windows)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m flask --app app run --debug

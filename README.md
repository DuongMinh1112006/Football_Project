# Hệ Thống Quản Lý Giải Đấu Bóng Đá (Premier League)

Dự án ứng dụng Web quản lý giải đấu bóng đá chuyên nghiệp, tập trung vào mô phỏng giải Ngoại hạng Anh (Premier League). Hệ thống cung cấp các luồng nghiệp vụ quản lý câu lạc bộ, cầu thủ, lịch thi đấu và tự động thống kê chỉ số chuyên môn như bảng xếp hạng, bàn thắng, kiến tạo,...theo thời gian thực (Real-time).

Dự án còn cho phép người dùng thêm trận đấu, thêm thông số cầu thủ trong trận đấu; tìm kiếm cầu thủ, câu lạc bộ theo tên, vị trí.

Dự án được phát triển làm Bài tập lớn học phần **Cơ sở dữ liệu**.

##  Tính năng nổi bật

* **Xem thông tin câu lạc bộ:** Thông tin câu lạc bộ bao gồm, tên, năm thành lập, sân nhà và danh sách cầu thủ trong mùa giải.

* **Xem thông tin cầu thủ:** Thông tin cầu thủ bao gồm tên, tuổi, quốc tịch, ngày sinh, nơi sinh,...(tuổi được tính tự động theo ngày sinh).

* **Quản lý lịch thi đấu:** Thêm trận đấu mới với tính năng tự động bắt lỗi logic (trùng đội nhà/khách, đội đã thi đấu trong lượt đi/về).

* **Thống kê trận đấu:** Ghi nhận chỉ số cầu thủ trong trận (bàn thắng, kiến tạo, số phút, thẻ phạt).

* **Bảng xếp hạng Real-time:** Tự động tính toán điểm số (Thắng 3, Hòa 1, Thua 0), hiệu số bàn thắng bại và xếp hạng các câu lạc bộ.

* **Tra cứu & Báo cáo:** Tìm kiếm cầu thủ/đội bóng không phân biệt viết hoa viết thường, tìm kiếm gần đúng. Tổng hợp danh sách vua phá lưới, vua kiến tạo, thẻ vàng,....

* **Nạp dữ liệu tự động:** Tích hợp API-Football để thu thập dữ liệu khởi tạo.

## Yêu cầu hệ thống (Prerequisites)

Để chạy dự án này trên máy local, máy tính của bạn cần cài đặt sẵn:

* Python 3.10+ (khuyên dùng 3.12)

* PostgreSQL 14+ (khuyên dùng 16)

* Git

## Hướng dẫn cài đặt (Installation)

**1. Clone dự án về máy**

```
git clone https://github.com/DuongMinh1112006/Football_Project.git
cd Football_Project

```

**2. Khởi tạo môi trường ảo (Virtual Environment) và cài đặt thư viện**

```
# Tạo môi trường ảo
python3 -m venv venv

# Kích hoạt môi trường (trên Linux/macOS)
source venv/bin/activate
# (Hoặc trên Windows: venv\Scripts\activate)

# Cài đặt các thư viện cần thiết
pip install -r requirements.txt

```

## Cấu hình môi trường và Cơ sở dữ liệu

**1. Cấu hình file `.env`**
Tạo một file `.env` tại thư mục gốc của dự án (ngang hàng với `manage.py`) và thiết lập các biến môi trường sau:

```
DB_NAME=football_db
DB_USER=postgres
DB_PASSWORD=mat_khau_postgres_cua_ban
DB_HOST=localhost
DB_PORT=5432
FOOTBALL_API_KEY=your_api_key_here  # Bỏ trống nếu không chạy lại script crawl data

```

**2. Khởi tạo và nạp dữ liệu vào PostgreSQL**
Dự án đã đính kèm sẵn file dump (`database/football_db_dump.sql`) chứa toàn bộ cấu trúc bảng và dữ liệu mẫu của giải đấu. Bạn **không cần** chạy lệnh `python manage.py migrate`.

Chạy các lệnh sau trên terminal để nạp dữ liệu:

```
# Tạo cơ sở dữ liệu mới
sudo -u postgres psql -c "CREATE DATABASE football_db;"

# Nạp dữ liệu từ file dump vào database vừa tạo
sudo -u postgres psql football_db < database/football_db.sql

```

## Khởi chạy ứng dụng (Usage)

Khi đã nạp database thành công, bạn chỉ cần khởi động server của Django:

```
cd my_web

python manage.py runserver

#nếu port 8000 đã sử dựng rồi thì chạy lệnh
python manage.py runserver 0.0.0.0:8001 #(8001 là các port sẵn trong máy có thể là giá trị khác)

```

Truy cập trình duyệt tại địa chỉ: `http://127.0.0.1:8000/` để sử dụng hệ thống.

## Cấu trúc dự án (Folder Structure)

```
├── database/
├── my_web/
│   ├── club/
│   │   ├── migrations/
│   │   ├── templates/club/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── my_web/
│   ├── cao_club.py
│   ├── cao_match.py
│   ├── cao_player.py
│   ├── cao_player_fixture.py
│   └── manage.py
├── .gitignore
└── requirements.txt

```
# test ci

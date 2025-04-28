# S3-MRS  
**Smart Study Space Management and Reservation System**  
S3-MRS (Smart Study Space Management and Reservation System) là hệ thống hỗ trợ sinh viên HCMUT tìm kiếm, đặt chỗ và sử dụng các không gian học tập thông minh.  
Hệ thống cho phép:
- Đặt chỗ linh hoạt qua web-app và mobile-app.
- Check-in bằng QR code và tự động kích hoạt thiết bị (đèn, điều hòa).
- Cập nhật trạng thái phòng theo thời gian thực thông qua cảm biến.
- Xác thực người dùng an toàn bằng HCMUT_SSO.
- Quản lý và thống kê hiệu quả việc sử dụng không gian học tập.

S3-MRS nhằm tối ưu hóa trải nghiệm học tập của sinh viên, hiện đại hóa quản lý cơ sở vật chất, và thúc đẩy ứng dụng công nghệ IoT trong môi trường giáo dục thông minh.

---

## Table of Contents
- [Mô tả dự án](mô-tả-dự-án)
- [Tính năng chính](tính-năng-chính)
- [Công nghệ & Công cụ](công-nghệ--công-cụ)
- [Cài đặt](cài-đặt)


## Mô tả dự án
Trong bối cảnh nhu cầu tự học, nghiên cứu và học nhóm tại HCMUT ngày càng tăng, dự án S3-MRS ra đời nhằm:
- Giúp sinh viên dễ dàng tìm, đặt và sử dụng các không gian tự học thông minh.
- Tích hợp IoT để theo dõi trạng thái phòng (trống/đang sử dụng).
- Tự động bật/tắt thiết bị (đèn, điều hòa…) khi có/sau khi hết người dùng.
- Hỗ trợ nhắc nhở qua web & mobile app.
- Cung cấp báo cáo sử dụng cho ban quản lý.

---

## Tính năng chính
- **Xác thực người dùng** qua HCMUT_SSO  
- **Xem & tìm kiếm** danh sách không gian với trạng thái thời gian thực  
- **Đặt chỗ linh hoạt** trên cả Web-app và Mobile-app  
- **Check-in, Unlock** QR code để vào phòng  
- **Thông báo nhắc nhở** trước giờ đặt và khi trạng thái thay đổi  
- **Quản lý và báo cáo**: thống kê mức độ sử dụng, lịch sử đặt chỗ  
- **Tích hợp IoT**: mô phỏng/giả lập cảm biến trạng thái và điều khiển thiết bị

---

## Công nghệ & Công cụ

- **Frontend Web**: HTML5, CSS3, JavaScript, React.js   
- **Backend**: Flask/Django Python 
- **Giao thức IoT**: MQTT (giả lập broker)  
- **Xác thực**: OAuth2 tích hợp HCMUT_SSO  

---

### Cài đặt
1. Clone repository:  
   ```bash
   git clone https://github.com/nguyenthinhthanh/S3-MRS
   ```
2. Cài đặt dependencies:
    ```
   pip install -r requirements.txt
    ```
3. Khởi động server:
   ```
   python app.py
   ```
4. Mở trình duyệt tại:
   ```
   http://localhost:5000
   ```

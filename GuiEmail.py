import smtplib
import os
from email.message import EmailMessage

# Định nghĩa thông tin hàm gửi email:
# Tên, mô tả, các tham số và kiểu dữ liệu tham chiếu
send_email_declaration = {
    "name": "send_mail",
    "description": "Gửi email qua SMTP với tiêu đề, nội dung và địa chỉ người nhận xác định trước.",
    "parameters": {
        "type": "object",
        "properties": {
            "subject": {
                "type": "string",
                "description": "Tiêu đề email"
            },
            "body": {
                "type": "string",
                "description": "Nội dung email"
            },
            "to_email": {
                "type": "string",
                "description": "Địa chỉ email người nhận"
            }
        },
        "required": ["subject", "body", "to_email"]
    },
}

def send_mail(subject, body, to_email):
    # Địa chỉ email người gửi (có thể chỉnh sửa)
    sender = "Private Person <from@example.com>"

    # Tạo đối tượng EmailMessage
    message = EmailMessage()
    # Đặt nội dung chính cho email
    message.set_content(body)
    # Tiêu đề email
    message['Subject'] = subject
    # Người gửi
    message['From'] = sender
    # Người nhận
    message['To'] = to_email

    # Kết nối đến máy chủ SMTP (Mailtrap trong ví dụ này)
    # Lưu ý: Thông tin tài khoản và mật khẩu (login, pass) là giả lập, thay bằng thông tin thật
    with smtplib.SMTP("sandbox.smtp.mailtrap.io", 2525) as server:
        server.login("bi mat", "bi mat")
        server.send_message(message)
        return "Email đã được gửi thành công"

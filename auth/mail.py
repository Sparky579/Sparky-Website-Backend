import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import random
import os
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
from sqlalchemy import desc
from create_app import createLimiter, createApp
limiter = createLimiter()

from extension import db

mail_bp = Blueprint('cookie_mail', __name__)

class CookieMail(db.Model):
    __tablename__ = 'cookie_mail'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cookie = db.Column(db.String)
    expires_at = db.Column(db.DateTime)
    value = db.Column(db.String)
    mail = db.Column(db.String)


@mail_bp.route('/send_mail', methods=['POST'])
# @limiter.limit("1/minute;20/day")
def send_mail():
    delete_expired_cookiemail()
    data = request.get_json()
    cookie_value = data.get('cookie')
    mail = data.get('mail')
    code = send_registration_email(mail)
    if code == 'fail':
        return 'fail to send mail', 400
    expires_at = datetime.now() + timedelta(minutes=5)
    new_cookiemail = CookieMail(cookie=cookie_value, expires_at=expires_at, value=code, mail=mail)
    db.session.add(new_cookiemail)
    db.session.commit()
    return 'send ok', 200


def check_code_available(code, cookie_value):
    delete_expired_cookiemail()
    cookiemail = CookieMail.query.filter(
        CookieMail.value == code,
        CookieMail.cookie == cookie_value
    ).order_by(desc(CookieMail.expires_at)).first()
    return cookiemail


def delete_expired_cookiemail():
    try:
        current = datetime.now()
        db.session.query(CookieMail).filter(CookieMail.expires_at < current).delete()
        db.session.commit()
    except Exception as e:
        print('fail to clear')



def send_registration_email(recipient_email):
    load_dotenv()
    email_server = os.getenv("email_server")
    email_password = os.getenv("email_password")
    # 设置邮件服务器的地址和端口（这里使用Gmail的SMTP服务器）
    smtp_server = os.getenv("smtp_server")
    smtp_port = int(os.getenv("smtp_port"))  # Gmail使用587端口

    # 发件人的邮箱地址和密码
    sender_email = email_server
    sender_password = email_password

    # 邮件主题和正文
    subject = '注册确认邮件'
    code = ''.join(random.choices('0123456789', k=6))
    message = f"""
    <html>
      <body>
        <p>欢迎来到 Sparky327 的个人网页！在5分钟内输入以下验证码确认注册：</p>
        <p style="font-size: 24px;">{code}</p>
      </body>
    </html>
    """

    # 创建邮件内容
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # 将正文添加到邮件中
    msg.attach(MIMEText(message, 'html'))

    try:
        # 连接SMTP服务器并登录
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)

        # 发送邮件
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()

        print('注册确认邮件已发送成功！')
        return code
    except Exception as e:
        print('邮件发送失败:', str(e))
        return "fail"

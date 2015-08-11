# --*coding: utf8*--
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import time
import yaml


def send_verify_mail(username, email, verify_code):
    with open("config.yml", "r") as f:
        doc = yaml.load(f)
        source_email = doc["email"]["source"]
        password = doc["email"]["password"]

    verify_link = "http://iubcoder.com/verify?email=" + \
                  email + \
                  "&code=" + \
                  verify_code
    content = \
        """
        你好 {username}，

        欢迎加入IUB Coder，请通过以下链接完成注册。

        {link}

        ------------------------------------
        IUB Coder
        """.format(username=username, link=verify_link)
    msg = MIMEMultipart()
    msg["Subject"] = Header("IUB Coder账号验证", "utf-8")
    msg["From"] = source_email  # comes from EMAIL_CONFIGURE
    msg["To"] = email
    text = MIMEText(content, _charset="UTF-8")
    msg.attach(text)

    server = smtplib.SMTP("smtp.mail.yahoo.com", 587)
    server.starttls()
    server.login(str(source_email), str(password))
    server.sendmail(source_email, email, msg.as_string())
    server.quit()

# ** coding: utf-8 **
import tornado.web
import re
import hashlib
import uuid
import time
import random

from db_operations import *
from send_mail import *


class IndexHandler(tornado.web.RequestHandler):
    '''
    Show main page
    '''
    def get(self):
        cookie_id = self.get_cookie("CoderID")
        username = get_name(cookie_id)
        self.render("index.html",
                    cookieName=username,
                    notice=False,
                    notice_msg="")


class AboutHandler(tornado.web.RequestHandler):
    '''
    Show about page
    '''
    def get(self):
        cookie_id = self.get_cookie("CoderID")
        username = get_name(cookie_id)
        self.render("about.html",
                    cookieName=username)


class RegisterHandler(tornado.web.RequestHandler):
    '''
    New user sign up
    '''
    def get(self):
        self.render("signup.html", error=False, error_msg="")

    def post(self):
        username = self.get_argument("username")
        error = False
        # if username is empty
        if username == "":
            error_msg = "用户名不得为空"
            self.render("signup.html", error=True, error_msg=error_msg)
            return
        # check if the username is already exists
        if_name = check_username(username)
        if if_name:
            error_msg = "用户名重复"
            self.render("signup.html", error=True, error_msg=error_msg)
            return
        password = self.get_argument("password")
        password_again = self.get_argument("password_again")
        # check if password is empty
        if len(password) == 0:
            error_msg = "密码不得为空"
            self.render("signup.html", error=True, error_msg=error_msg)
            return
        # check if two passwords are the same
        if password != password_again:
            error_msg = "密码前后不一致"
            self.render("signup.html", error=True, error_msg=error_msg)
            return
        email = self.get_argument("email")
        # check if email is empty
        if len(email) == 0:
            error_msg = "邮箱不得为空"
            self.render("signup.html", error=True, error_msg=error_msg)
            return
        # check email format
        email_pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if not re.match(email_pattern, email):
            error_msg = "邮箱格式不正确"
            self.render("signup.html", error=True, error_msg=error_msg)
            return
        # check if email is already registered
        if_mail = check_email(email)
        if if_mail:
            error_msg = "邮箱已被注册"
            self.render("signup.html", error=True, error_msg=error_msg)
            return
        # generate hashed password
        salt = uuid.uuid4().hex
        hashed_password = hashlib.sha512(password + salt).hexdigest()
        new_user = insert_user(username, hashed_password, salt, email)
        self.redirect("/sendMail?email=" + new_user["email"])


class LoginHandler(tornado.web.RequestHandler):
    '''
    User login
    '''
    def get(self):
        self.render("login.html", error=False, error_msg="")

    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")
        user = get_user_given_username(username)
        if not user:
            error_msg = "用户不存在"
            self.render("login.html", error=True, error_msg=error_msg)
            return
        # if password match
        hashed_password = hashlib.sha512(password + user["salt"]).hexdigest()
        if hashed_password != user["password"]:
            error_msg = "密码和用户名不匹配"
            self.render("login.html", error=True, error_msg=error_msg)
            return
        cookie_id = user["cookie"]
        verified = is_verified(cookie_id)  # check if account verified
        self.set_cookie("CoderID", cookie_id)  # set cookie when logging in
        if not verified:
            self.render("index.html",
                        cookieName=None,
                        notice=True,
                        notice_msg="用户未验证")
        else:
            self.redirect("/")


class LogoutHandler(tornado.web.RequestHandler):
    '''
    User logout
    '''
    def get(self):
        self.clear_cookie("CoderID")
        self.render("logout.html",
                    cookieName=None)


class SendMailHandler(tornado.web.RequestHandler):
    '''
    Send verfication email to new user
    '''
    def get(self):
        email = self.get_argument("email")
        user = get_user_given_email(email)
        if user["verified"]:
            cookie_id = user["cookie"]
            self.set_cookie("CoderID", cookie_id)
            self.redirect("/")
        else:
            send_verify_mail(user["username"], email, user["verify_code"])
            self.render("sendMail.html", cookieName=None)


class VerifyHandler(tornado.web.RequestHandler):
    '''
    Verify new user's account
    '''
    def get(self):
        email = self.get_argument("email")
        verify_code = self.get_argument("code")
        verify_res, msg = verify_account(email, verify_code)
        if verify_res:
            self.render("index.html",
                        cookieName=None,
                        notice=True,
                        notice_msg="验证成功")
        else:
            self.render("index.html",
                        cookieName=None,
                        notice=True,
                        notice_msg="验证失败，"+msg)


class NotFoundHandler(tornado.web.RequestHandler):
    '''
    404.html
    '''
    def get(self):
        self.render("404.html", cookieName=False)

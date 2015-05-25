# ** coding: utf-8 **
import tornado.web
import re
import hashlib
import uuid
import time
import random
import math

from db_operations import *
from send_mail import *
import markdown_gen
import send_mail
import time_translate


class MainPageHandler(tornado.web.RequestHandler):
    '''
    Redirect to the first page
    '''
    def get(self):
        self.redirect("/page/1")


class IndexHandler(tornado.web.RequestHandler):
    '''
    Show main page
    '''
    def get(self, cur_page):
        try:
            cur_page = int(cur_page)
        except:
            self.redirect("/error")
            return
        cookie_id = self.get_secure_cookie("CoderID")
        username = get_name_by_cookie(cookie_id)
        posts = fetch_all_posts()
        page_num = int(math.ceil(len(posts) / 20.0))  # 20 posts per page
        if len(posts) and cur_page > page_num:
            self.redirect("/error")
            return
        self.render("index.html",
                    cookieName=username,
                    posts=posts,
                    curPage=cur_page,
                    pageNum=page_num,
                    time_to_now=time_translate.time_to_now)


class AboutHandler(tornado.web.RequestHandler):
    '''
    Show about page
    '''
    def get(self):
        cookie_id = self.get_secure_cookie("CoderID")
        username = get_name_by_cookie(cookie_id)
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
        user = get_user_by_username(username)
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
        # set cookie when logging in, and expires in 15 mins
        self.set_secure_cookie("CoderID", cookie_id, expires=time.time()+900)
        if not verified:
            error_msg = "用户未验证"
            self.render("login.html",
                        error=True,
                        error_msg=error_msg)
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
            # 900 = 60 * 15, 15 minutes
            self.set_secure_cookie("CoderID", cookie_id, expires=time.time()+900)
            self.redirect("/")
        else:
            fail = self.get_argument("fail", False)  # default is False
            send_mail.send_verify_mail(user["username"], email, user["verify_code"])
            if fail:
                msg = "验证失败，已再次发送验证邮件"
            else:
                msg = "验证邮件已发送"
            self.render("sendMail.html",
                        cookieName=None,
                        msg=msg)


class VerifyHandler(tornado.web.RequestHandler):
    '''
    Verify new user's account
    '''
    def get(self):
        email = self.get_argument("email")
        verify_code = self.get_argument("code")
        verify_res, msg = verify_account(email, verify_code)
        print verify_res, msg

        if verify_res:
            user = get_user_given_email(email)
            self.set_secure_cookie("CoderID", user["cookie"], expires=time.time()+900)
            self.redirect("/")
        else:
            # if verification fails, add argument 'fail' and resend email
            self.redirect("/sendMail?email={email}&fail={fail}".format(
                    email=email,
                    fail=True
                ))


class NewPostHandler(tornado.web.RequestHandler):
    '''
    New post
    '''
    def get(self):
        cookie_id = self.get_secure_cookie("CoderID")
        username = get_name_by_cookie(cookie_id)
        self.render("newPost.html",
                    cookieName=username, 
                    notice=None)

    def post(self):
        cookie_id = self.get_secure_cookie("CoderID")
        username = get_name_by_cookie(cookie_id)
        if not username:
            # if there's no user log in
            notice = True
            notice_msg = "先登录，后发帖"
            self.render("newPost.html", 
                        cookieName=username, 
                        notice=notice, 
                        notice_msg=notice_msg)
            return
        title = self.get_argument("title")
        content = self.get_argument("content")
        if len(title) == 0:
            # if there's no title
            notice = True
            notice_msg = "标题不得为空"
            self.render("newPost.html", 
                        cookieName=username, 
                        notice=notice, 
                        notice_msg=notice_msg)
            return
        author = username  # author
        post_time = time.time()  # post time
        insert_post(title, content, author, post_time)
        self.redirect("/")


class ShowPostHandler(tornado.web.RequestHandler):
    '''
    Show post
    '''
    def get(self, post_num):
        cookie_id = self.get_secure_cookie("CoderID")
        username = get_name_by_cookie(cookie_id)
        post = fetch_post_by_num(int(post_num))
        if not post:
            self.redirect("/error")
            return
        content = markdown_gen.md_translate(post["content"])
        self.render("post.html",
                    cookieName=username,
                    notice=False,
                    post=post,
                    content=content,
                    translate=markdown_gen.md_translate,
                    time_to_now=time_translate.time_to_now)

    def post(self, post_num):
        # write comment
        cookie_id = self.get_secure_cookie("CoderID")
        username = get_name_by_cookie(cookie_id)
        post = fetch_post_by_num(post_num)
        if not username:
            # if not login
            self.render("post.html",
                        cookieName=username,
                        notice=True,
                        notice_msg="先登录，后跟帖",
                        post=post,
                        content=markdown_gen.md_translate(post["content"]),
                        translate=markdown_gen.md_translate,
                        time_to_now=time_translate.time_to_now)
            return
        content = self.get_argument("commentContent")
        if len(content) == 0:
            # content is empty
            self.render("post.html",
                        cookieName=username,
                        notice=True,
                        notice_msg="跟帖内容不得为空",
                        post=post,
                        content=markdown_gen.md_translate(post["content"]),
                        translate=markdown_gen.md_translate,
                        time_to_now=time_translate.time_to_now)
            return
        insert_comment(post, username, content)
        self.render("post.html",
                    cookieName=username,
                    notice=False,
                    post=post,
                    content=markdown_gen.md_translate(post["content"]),
                    translate=markdown_gen.md_translate,
                    time_to_now=time_translate.time_to_now)


class EditPostHandler(tornado.web.RequestHandler):
    '''
    Edit post. 
    '''
    def get(self, post_num):
        cookie_id = self.get_secure_cookie("CoderID")
        username = get_name_by_cookie(cookie_id)
        post = fetch_post_by_num(int(post_num))
        self.render("editPost.html",
                    cookieName=username,
                    post=post,
                    notice=None,
                    notice_msg="")

    def post(self, post_num):
        cookie_id = self.get_secure_cookie("CoderID")
        username = get_name_by_cookie(cookie_id)
        post = fetch_post_by_num(post_num)
        title = self.get_argument("title")
        content = self.get_argument("content")
        print "asdf"
        if len(title) == 0:
            # if there's no title
            notice = True
            notice_msg = "标题不得为空"
            self.render("editPost.html",
                    cookieName=username,
                    post=post,
                    notice=notice,
                    notice_msg=notice_msg)
            return
        post["title"] = title
        post["content"] = content
        post["last_modified"] = time.time()
        update_post(post)
        self.redirect("/post/{}".format(post["post_num"]))


class NotFoundHandler(tornado.web.RequestHandler):
    '''
    404.html
    '''
    def get(self):
        cookie_id = self.get_secure_cookie("CoderID")
        username = get_name_by_cookie(cookie_id)
        self.render("404.html", cookieName=username)

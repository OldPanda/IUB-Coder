#--*coding: utf8*--
import pymongo
import hashlib
import uuid
import time
import random
from bson.objectid import ObjectId

'''
client = pymongo.MongoClient('mongodb://localhost:27017/')
conn = client.test_database
'''
MONGODB_URI = "mongodb://OldPanda:19900930@ds031832.mongolab.com:31832/iubcoder"
client = pymongo.MongoClient(MONGODB_URI)  # database connection
conn = client.get_default_database()



def check_username(username):
    '''
    Check if the username has been used
    '''
    user_db = conn["users"]
    user = user_db.find_one({"username": username})
    if user:
        return True
    else:
        return False


def check_email(email):
    '''
    Check if the email has been used
    '''
    user_db = conn["users"]
    user = user_db.find_one({"email": email})
    if user:
        return True
    else:
        return False


def insert_user(username, password, salt, email):
    '''
    Inser a new user into database.
    '''
    user_db = conn["users"]  # user database
    # register time
    reg_time = time.time()
    # generate verify code
    code = username + email + str(reg_time)
    m2 = hashlib.md5(code.encode('utf8'))
    md5code = m2.hexdigest() + '.' + str(random.randint(11111111, 99999999))
    # generate cookie, _id is a ObjectId type, which cannot be used as cookie.
    gen_cookie = username + email
    cookie = hashlib.md5(gen_cookie.encode('utf8')).hexdigest()

    new_user = {
        "reg_time": reg_time,
        "username": username,
        "password": password,
        "email": email,
        "salt": salt,
        "verified": False,
        "verify_code": md5code,
        "cookie": cookie,
        "user_info": {},
        "posts": [],
        "comments": []
        }
    # insert new user
    user_db.insert(new_user)
    return new_user


def is_verified(cookie):
    '''
    Check the given user is verified.
    '''
    user_db = conn["users"]
    user = user_db.find_one( {"cookie": cookie} )
    return user["verified"]


def get_name_by_cookie(cookie):
    '''
    Return user name of the given user_id.
    '''
    if cookie:
        user_db = conn["users"]
        user = user_db.find_one( {"cookie": cookie} )
        if user:
            return user["username"]
        else:
            return None
    else:
        return None


def get_user_by_username(username):
    '''
    Check if user exists
    '''
    user_db = conn["users"]
    user = user_db.find_one( {"username": username} )
    if user:
        return user
    else:
        return None


def get_user_given_email(email):
    '''
    Return user according to the given email
    '''
    user_db = conn["users"]
    user = user_db.find_one( {"email": email} )
    return user

def verify_account(email, verify_code):
    '''
    Verify user account
    '''
    user_db = conn["users"]
    user = user_db.find_one( {"email": email} )
    if user:
        if user["verify_code"] == verify_code:
            user["verified"] = True
            user_db.save(user)
            return True, ""
        else:
            return False, "验证码不正确"
    else:
        return False, "用户不存在"


def insert_post(title, content, author, post_time):
    '''
    Insert a new post, and update user's 'posts'.
    '''
    post_db = conn["posts"]
    user_db = conn["users"]  # also need to update user
    post_num = gen_new_post_num()  # generate a post num(id)
    post_id = post_db.insert({
        "post_num": post_num,
        "title": title,
        "content": content,
        "author": author,
        "post_time": post_time,
        "last_modified": post_time,
        "comments": []
        })
    # update user's post
    user = user_db.find_one( {"username": author} )
    user["posts"].append(ObjectId(post_id))
    user_db.save(user)


def fetch_all_posts():
    '''
    Get all posts from database, in reversed order of last_modified
    '''
    post_db = conn["posts"]
    all_posts = post_db.find().sort( [("last_modified", -1)] )
    return all_posts


def gen_new_post_num():
    '''
    Check the number of latest post in database, then generate a new number 
    by adding one
    '''
    post_db = conn["posts"]
    all_posts = post_db.find()
    if all_posts.count():
        latest_post = max(all_posts, key=lambda item: item["post_time"])
        new_num = latest_post["post_num"] + 1
    else:
        new_num = 0
    return new_num


def fetch_post_by_num(post_num):
    '''
    Return post according to given number
    '''
    post_db = conn["posts"]
    post = post_db.find_one({"post_num": int(post_num)})
    return post


def insert_comment(post, username, content):
    '''
    Insert a comment into a post
    '''
    # update on posts collection
    post_db = conn["posts"]
    comment_time = time.time()
    post["comments"].append({
        "content": content,
        "post_time": comment_time,
        "author": username
        })
    post["last_modified"] = comment_time
    post_db.save(post)
    # update on user collection
    user_db = conn["users"]
    user = get_user_by_username(username)
    user["comments"].append({
        "post_num": post["post_num"],
        "content": content,
        "last_modified": comment_time
        })
    user_db.save(user)


def update_post(post):
    '''
    Save updated post into database
    '''
    post_db = conn["posts"]
    post_db.save(post)


def update_user(user):
    '''
    Save updated user info into database
    '''
    user_db = conn["users"]
    user_db.save(user)


def remove_post_by_num(post_num):
    '''
    Remove post by given post number
    '''
    post_db = conn["posts"]
    post = post_db.find_one( {"post_num": post_num} )
    post_author = post["author"]
    user_db = conn["users"]
    user = user_db.find_one( {"username": post_author} )
    user["posts"].remove(post["_id"])
    update_user(user)
    post_db.remove( {"post_num": post_num} )

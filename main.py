#!/usr/bin/env python
# --*coding: utf8*--
import tornado.httpserver
import tornado.ioloop
import tornado.options

import os.path
import sys
from handlers import *

from tornado.options import define, options
define("port", default=54321, help="run on the given port", type=int)


class Application(tornado.web.Application):
    def __init__(self):
        self.db = conn["iub_test"]
        handlers = [
            (r"/", IndexHandler),
            (r"/about", AboutHandler),
            (r"/signup", RegisterHandler),
            (r"/login", LoginHandler),
            (r"/logout", LogoutHandler),
            (r"/sendMail", SendMailHandler),
            (r"/verify", VerifyHandler),
            (r"/error", NotFoundHandler),
            (r".*", NotFoundHandler)
        ]
        settings = {
            'template_path':
                os.path.join(os.path.dirname(__file__), "templates"),
            'static_path':
                os.path.join(os.path.dirname(__file__), "static"),
            'debug': True
        }
        tornado.web.Application.__init__(self, handlers, **settings)


def main():
    reload(sys)
    sys.setdefaultencoding("utf-8")
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
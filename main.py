#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import jinja2
from constants import *
from google.appengine.ext import db
import os

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


class Handler(webapp2.RequestHandler):
    def write(self, *args, **kwargs):
        self.response.out.write(*args, **kwargs)

    def render_str(self,template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self,template, **kw):
        self.write(self.render_str(template,**kw))

class Blog(db.Model):
    id = db.IntegerProperty()
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    date_created = db.DateProperty(auto_now_add=True)
    created = db.DateTimeProperty(auto_now_add=True)
    url = db.StringProperty()

class MainHandler(Handler):

    def get(self):
       blogs = db.GqlQuery("select * from Blog order by created desc limit 10")
       self.render(front, blogs = blogs)


def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class NewPostHandler(Handler):

    def get(self, subject="", content="", error=""):
        self.render(new_post, subject=subject, content=content, error=error)


    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            p = Blog(parent = blog_key(), subject = subject, content = content)
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = ERROR_STRING
            self.render(new_post, subject=subject, content=content, error=error)

class BlogHandler(Handler):
    def get(self, post_id):
       key = db.Key.from_path('Post', int(post_id), parent=blog_key())
       blog = db.get(key)

       if not blog:
           self.error(404)
           return

       self.render(blog, blog = blog)

class CookieHandler(Handler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        visits = self.request.cookies.get('visits', 0)
        visits = int(visits)
        visits+=1
        self.response.headers.add_header('Set-Cookie', 'visits=%s' % visits)
        self.write("You have been here %s times" % visits)


class id_handler():
    id_count = 1



def get_blog_by_id(id):
    blogs = db.GqlQuery("select * from Blog")
    for blog in blogs:
        if blog.id == id:
            return blog

get_blog_by_id(1)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/cook', CookieHandler),
    ('/newpost', NewPostHandler),
    ('/blogs/([0-9]+)', BlogHandler)
], debug=True)

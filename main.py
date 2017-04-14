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
import os
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class BlogPost(db.Model):
    title = db.StringProperty(required = True)
    postbody = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainHandler(Handler):
    def render_front(self, title="", postbody="", error=""):
        blogposts = db.GqlQuery("SELECT * FROM BlogPost "
                            "ORDER BY created DESC LIMIT 5")

        self.render("front.html", blogposts=blogposts)

    def get(self):
        self.render_front()


class ViewPostHandler(Handler):
    def get(self, id):
        post = BlogPost.get_by_id(int(id), parent=None)
        self.render('viewpost.html', title=post.title, postbody=post.postbody)

class NewPostHandler(Handler):
    def get(self):
        self.render('newpost.html')

    def post(self):
        title = self.request.get("title")
        postbody = self.request.get("postbody")

        if title and postbody:
            a = BlogPost(title = title, postbody = postbody)
            key = a.put()

            self.redirect("/blog/%s" % key.id())
        else:
            error = "We need both a title and some content for the post body!"
            self.render('newpost.html', title=title, postbody=postbody, error=error)

class BaseHandler(Handler):
    def get(self):
        self.response.write("<a href='/blog'>blog</a>")


app = webapp2.WSGIApplication([
    ('/', BaseHandler),
    ('/blog', MainHandler),
    ('/blog/newpost', NewPostHandler),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)

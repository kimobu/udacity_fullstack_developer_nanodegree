from google.appengine.ext import ndb

class User(ndb.Model):
    username = ndb.StringProperty()
    password = ndb.TextProperty()
    
class Comment(ndb.Model):
    """
    Models a comment made on a blog
    """
    user = ndb.KeyProperty(kind='User')
    body = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)
    blog = ndb.KeyProperty(kind='Blog')
    
class Blog(ndb.Model):
    """Models an individual blog entry with subject, body and date."""
    user = ndb.KeyProperty(kind='User')
    subject = ndb.StringProperty()
    body = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)
    comments = ndb.KeyProperty(kind='Comment', repeated=True)
    
class BlogLike(ndb.Model):
    """
    Relates a blog and a user
    """
    user = ndb.KeyProperty(kind='User')
    blog = ndb.KeyProperty(kind='Blog')
from flask import Flask, render_template, request
from flask import redirect, url_for, make_response, jsonify
from functools import wraps


from models import Blog, User, BlogLike, Comment
from google.appengine.ext.ndb import Key
from lib import valid_pw, validate_email, validate_password, validate_username
from lib import make_pw_hash, check_secure_val, make_secure_val


app = Flask(__name__)
app.config['DEBUG'] = True


def login_required(f):
    """
    This function checks to see if a user is logged in
    If they are not logged in, they are redirected to the login page
    If they are logged in, they are sent to the page requested

    Other functions will use the @login_required decorator to call this
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        username = request.cookies.get('name')
        logged_in = check_secure_val(username)
        if logged_in is False:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def render(request, template, **kwargs):
    """
    This is a wrapper function so that every page can be checked for a login
    Additionally, a caller can specify an HTTP status code that will be
    applied to the response object
    """
    username = request.cookies.get('name')
    logged_in = check_secure_val(username)
    code = kwargs.get('code', '200')
    if code:
        return render_template(template, logged_in=logged_in, **kwargs), code
    else:
        return render_template(template, logged_in=logged_in, **kwargs)


def do_login(user):
    """
    This function performs a login by generating the secure value and
    setting a cookie
    """
    name_val = make_secure_val(user.username)
    user_key = user.key.urlsafe()
    response = redirect(url_for('welcome'))
    response.set_cookie('name', name_val)
    response.set_cookie('user_key', user_key)
    return response


def get_user(user_key):
    """
    This is an abstraction of getting a User entity out of the GAE NDB
    """
    key = Key(urlsafe=user_key)
    kind_string = key.kind()
    ident = key.id()
    user = User.get_by_id(ident)
    return user


def get_blog(blog_key):
    """
    This is an abstraction of getting a Blog entity out of the GAE NDB
    """
    key = Key(urlsafe=blog_key)
    kind_string = key.kind()
    ident = key.id()
    blog = Blog.get_by_id(ident)
    return blog

"""
Blog page handlers
"""


@app.route('/')
def home():
    """Display blog messages"""
    blogs = Blog.query()
    return render(request, 'home.html', blogs=blogs)


@app.route('/blog/<blog_id>')
def blog(blog_id):
    """Display a single blog post"""
    blog = Blog.get_by_id(int(blog_id))
    likes = BlogLike.query(BlogLike.blog == blog.key).count()
    comments = Comment.query(Comment.blog == blog.key).order(Comment.date)
    user_key = request.cookies.get('user_key')
    return render(request, 'blog.html', blog=blog, comments=comments,
                  likes=likes, user_key=user_key)


@app.route('/newpost', methods=["POST", "GET"])
@login_required
def new_post():
    if request.method == "POST":
        """Create and save a blog entry"""
        form = request.form
        subject = form['subject']
        body = form['body']
        user_key = request.cookies.get('user_key')
        user = get_user(user_key)
        if subject and body:
            blog = Blog(subject=subject, body=body, user=user.key)
            blog_key = blog.put()
            blog_id = blog_key.id()
            return redirect(url_for('blog', blog_id=blog_id))
        else:
            error = "Please check your subject and body"
            return render(request, 'newpost.html', subject=subject,
                          body=body, error=error)
    else:
        """ Just return the new post page """
        return render(request, 'newpost.html')


@app.route('/delete', methods=["POST"])
@login_required
def delete_blog():
    """
    This function deletes a blog and its key
    """
    form = request.form
    user_key = request.cookies.get('user_key')
    user = get_user(user_key)
    blog = get_blog(form['blog_key'])
    if user.key != blog.user:
        d = {'status': 'failed',
             'reason': 'You can only delete your own posts'}
        return jsonify(**d)
    blog.key.delete()
    d = {'status': 'success'}
    return jsonify(**d)


@app.route('/edit/<blog_id>', methods=["POST", "GET"])
@login_required
def edit_blog(blog_id):
    user_key = request.cookies.get('user_key')
    user = get_user(user_key)
    blog = Blog.get_by_id(int(blog_id))
    if user.key != blog.user:
        return "You are not this blog's owner", 500
    if request.method == "POST":
        """ Try to process a form to edit the subject and body of a blog"""
        form = request.form
        subject = form['subject']
        body = form['body']
        if subject and body:
            blog.subject = subject
            blog.body = body
            blog.put()
            return redirect(url_for('blog', blog_id=blog_id))
        else:
            error = "Please check your subject and body"
            return render(request, 'edit.html', subject=subject, body=body,
                          error=error)
    else:
        """ Just display the blog edit page """
        return render(request, 'edit.html', blog=blog)

"""
Comment page handlers
"""


@app.route('/newcomment', methods=["POST"])
@login_required
def new_comment():
    """
    Creates and saves a blog comment
    """
    form = request.form
    user_key = request.cookies.get('user_key')
    user = get_user(user_key)
    blog = get_blog(form['blog_key'])
    body = form['body']
    comment = Comment(user=user.key, body=body, blog=blog.key)
    comment_key = comment.put()
    blog.comments.append(comment_key)
    blog.put()
    d = {'status': 'ok', 'user': user.username, 'comment_id': comment.key.id()}
    return jsonify(**d)


@app.route('/comment/delete', methods=["POST"])
@login_required
def delete_comment():
    form = request.form
    user_key = request.cookies.get('user_key')
    user = get_user(user_key)
    comment = Comment.get_by_id(int(form['comment_id']))
    if user.key != comment.user:
        d = {'status': 'failed', 'reason': "Can only delete your own comments"}
        return jsonify(**d)
    comment.key.delete()
    d = {'status': 'success'}
    return jsonify(**d)


@app.route('/comment/edit', methods=["POST"])
@login_required
def edit_comment():
    form = request.form
    user_key = request.cookies.get('user_key')
    user = get_user(user_key)
    comment = Comment.get_by_id(int(form['comment_id']))
    if user.key != comment.user:
        d = {'status': 'failed', 'reason': "Can only edit your own comments"}
        return jsonify(**d)
    new_body = form['new_body']
    comment.body = new_body
    comment.put()
    d = {'status': 'success'}
    return jsonify(**d)


@app.route('/likeblog', methods=["POST"])
@login_required
def like_blog():
    """
    Creates and saves a BlogLike
    """
    form = request.form
    user_key = request.cookies.get('user_key')
    user = get_user(user_key)
    blog = get_blog(form['blog_key'])
    if user.key == blog.user:
        d = {'status': 'failed', 'reason': "Can't like your own posts"}
        return jsonify(**d)
    q = BlogLike.query(BlogLike.user == user.key, BlogLike.blog == blog.key)
    like = q.fetch(1)
    if not like:
        like = BlogLike(user=user.key, blog=blog.key)
        like.put()
    else:
        d = {'status': 'failed', 'reason': 'You can only like something once'}
        return jsonify(**d)
    likes = BlogLike.query(BlogLike.blog == blog.key).count()
    d = {'status': 'ok', 'likes': likes}
    return jsonify(**d)


"""
Auth related page handlers
"""


@app.route('/welcome')
def welcome():
    """
    Displays a welcome page after a user is logged in
    """
    user_key = request.cookies.get('user_key')
    user = get_user(user_key)
    username = user.username
    if not username:
        return redirect(url_for('login'))
    response = render(request, 'welcome.html')
    return response


@app.route('/signup', methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        """ Try to create a new user """
        form = request.form
        username = form['username']
        password = form['password']
        verify = form['verify']
        email = form['email']
        valid_username = validate_username(username)
        valid_password = validate_password(password, verify)
        valid_email = validate_email(email)
        error = ""
        if not valid_username:
            error += "Bad username<br />"
        if not valid_password:
            error += "Bad password or passwords don't match <br />"
        if not valid_email:
            error += "Bad email"
        if not (valid_username and valid_password and valid_email):
            return render(request, 'signup.html', username=username,
                          email=email, error=error)

        q = User.query(User.username == username)
        user_taken = q.fetch(1)
        if not user_taken:
            user = User(username=username, password=make_pw_hash(username,
                        password))
            user.put()
        else:
            error += "Username is already taken"
            return render(request, 'signup.html', username=username,
                          email=email, error=error)

        return do_login(user)
    else:
        return render(request, 'signup.html')


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        """ Try to get the user and log them in """
        form = request.form
        username = form['username']
        password = form['password']
        user = User.query(User.username == username).get()
        if user and valid_pw(username, password, user.password):
            return do_login(user)
        else:
            error = "Invalid login"
            return render(request, 'login.html', username=username,
                          password=password, error=error)
    else:
        """ Just display the login page """
        if next:
            """
            The user was redirected here
            Set the HTTP code so that the Javascript can redirect the user
            """
            return render(request, 'login.html', code=302)
        return render(request, 'login.html')


@app.route('/logout')
def logout():
    """
    Unset the cookie to log the user out
    """
    response = redirect(url_for('home'))
    response.set_cookie('name', '')
    response.set_cookie('user_key', '')
    return response


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404

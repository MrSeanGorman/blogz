from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')
       
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username
    
def get_blogs():
    return Blog.query.all()

def get_users():
    return User.query.all()

@app.route('/')
def index():
    print("index")
    return render_template("index.html", title="Blog Users!", users=get_users())

@app.route('/index')

@app.route('/blog')
def blog():
    if request.args.get('id') != None:
        blogpost_id = int(request.args.get('id'))
        blogpost = Blog.query.get(blogpost_id)
        return render_template('blogpost.html', title=blogpost.title, blog_content=blogpost.body)

    elif request.args.get('user') != None:
        user_id = int(request.args.get('user'))
        user = User.query.get(user_id)
        blog_posts = Blog.query.filter_by(owner=user).all()
        return render_template('blog.html',blog_posts=blog_posts)
    else:
        return render_template('blog.html',title="Build A Blog", blog_posts=get_blogs())

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        newpost_title = request.form['blog_title']
        newpost_content = request.form['blog_content']
        owner = User.query.filter_by(username=session['user']).first()
        if newpost_title == '' or newpost_content == '':
            return render_template('newpost.html', title="Add a Blog Entry", newpost_title=newpost_title, newpost_content=newpost_content, error="Fill in all fields")
        newpost = Blog(title=newpost_title, body=newpost_content, owner=owner)
        db.session.add(newpost)
        db.session.commit()
        newpost = Blog.query.order_by(Blog.id.desc()).first()
        newpost_id = newpost.id
        return redirect('/blog?id={0}'.format(newpost_id))
    else:
        return render_template('newpost.html', title="Add a Blog Entry")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        # TODO VERIFY PASSWORD AND USERNAME
        if user and user.password == password:
            session['user'] = user.username
        elif user == None:
            flash('This username does not exist')
            return redirect('/login')
        else:
            flash('Incorrect password')
            return redirect('/login')
        return redirect('/newpost')

    else:
        return render_template('login.html', title = 'Login')
@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        reg_error=False

        if username == '' or password == '' or verify == '':
            flash('Please fill in all fields')
            reg_error=True

        if len(username) < 3:
            flash("Invalid username")
            reg_error=True
            
        if len(password) < 3:
            flash("Invalid password")
            reg_error=True

        if not password == verify:
            flash('Passwords do not match')
            reg_error=True

        if User.query.filter_by(username=username).all():
            flash('This username is already registered')
            reg_error=True

        if reg_error == True:
            return redirect('/signup')

        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        session['user'] = user.username
        return redirect("/newpost")
    else:
        return render_template('signup.html')

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    del session['user']
    return redirect("/blog")

# TODO make this
@app.before_request
def require_login():
    if not ('user' in session or request.endpoint == 'signup' or request.endpoint == 'login' or request.endpoint == 'blog' or request.endpoint == 'index'): 
        return redirect("/login")

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RU'

if __name__ == '__main__':
    app.run()
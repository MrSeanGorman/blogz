from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    print("LINE 15")
    def __init__(self, title, body):
        self.title = title
        self.body = body
    
def get_blogs():
    return Blog.query.all()

@app.route('/')
def index():
    print("index")
    return redirect('/blog')

@app.route('/blog')
def blog():
    print("def blog")
    if request.args.get('id') != None:
        print("/blog if")
        blogpost_id = int(request.args.get('id'))
        blogpost = Blog.query.get(blogpost_id)#.filter_by(id=blogpost_id).all()
        print("blogpost.title =" + blogpost.title +" blopost.body =" + blogpost.body)
        return render_template('blogpost.html', title=blogpost.title, blog_content=blogpost.body)
        
    else:
        print("/blog else")
        blog_posts = get_blogs()
        print("about to print blog_posts")
        print(blog_posts)
        return render_template('blog.html',title="Build A Blog", blog_posts=get_blogs())

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        newpost_title = request.form['blog_title']
        newpost_content = request.form['blog_content']
        if newpost_title == '' or newpost_content == '':
            return render_template('newpost.html', title="Add a Blog Entry", newpost_title=newpost_title, newpost_content=newpost_content, error="Fill in all fields") 
        print("LINE 33")
        newpost = Blog(title=newpost_title, body=newpost_content)
        print("LINE 35")
        db.session.add(newpost)
        db.session.commit()
        newpost = Blog.query.order_by(Blog.id.desc()).first()
        newpost_id = newpost.id
        return redirect('/blog?id={0}'.format(newpost_id)) #title=newpost_title, blog_content=newpost_content)
    else:
        return render_template('newpost.html', title="Add a Blog Entry")
    
if __name__ == '__main__':
    app.run()
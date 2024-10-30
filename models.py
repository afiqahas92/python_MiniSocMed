from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    posts = db.relationship('UserPost', backref='user', lazy=True) 

class UserPost(db.Model):
    __tablename__ = 'user_posts'
    post_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    image = db.Column(db.Text)
    caption = db.Column(db.Text)
    comments = db.relationship('CommentPost', backref='post', lazy=True) 

class CommentPost(db.Model):
    __tablename__ = 'comments'
    comment_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)  # Ensure this line exists
    post_id = db.Column(db.Integer, db.ForeignKey('user_posts.post_id'), nullable=False)
    commentText = db.Column(db.String(255), nullable=False)
    user = db.relationship('Users', backref='comments') 

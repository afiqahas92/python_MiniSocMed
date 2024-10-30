from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from models import db, Users, UserPost, CommentPost
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import base64

app = Flask(__name__)
app.secret_key = "justForTest"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///TestDB.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(hours=1)

db.init_app(app)
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    if "user_id" in session:
        posts = UserPost.query.all()
        
        for post in posts:
            post.comments = CommentPost.query.filter_by(post_id=post.post_id).all()
            post.edit_mode = False  
        
        return render_template("Home.html", posts=posts)
    else:
        flash("Unauthorized!")
        return redirect(url_for("login"))

# User Login and Registration
@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        flash("You are already logged in!")
        return redirect(url_for("home"))
    
    if request.method == "POST":
        action = request.form.get("action")

        if action == "login":
            user_email = request.form["email"]
            user_password = request.form["password"]

            user = Users.query.filter_by(email=user_email).first()
            if user and check_password_hash(user.password, user_password):
                session["user_id"] = user.user_id
                flash("Login successful!")
                return redirect(url_for("home"))  

            flash("Invalid credentials!")
            return redirect(url_for("login"))

        elif action == "signup":
            user_name = request.form["name"]
            user_email = request.form["email"]
            user_password = request.form["password"]
            confirm_password = request.form["confirm_password"]

            if user_password != confirm_password:
                flash("Passwords do not match!")
                return redirect(url_for("login")) 

            existing_user = Users.query.filter_by(email=user_email).first()
            if existing_user:
                flash("Email already registered!")
                return redirect(url_for("login"))

            new_user = Users(name=user_name, email=user_email, password=generate_password_hash(user_password))
            db.session.add(new_user)
            db.session.commit()
            
            flash("User registered successfully! You can now log in.")
            return redirect(url_for("login")) 

    return render_template("login.html")  

@app.route("/create_post", methods=["GET", "POST"])
def create_post():
    if "user_id" not in session:
        flash("Unauthorized!")
        return redirect(url_for("login"))

    if request.method == "POST":
        if "user_id" not in session:
            flash("Unauthorized!")
            return redirect(url_for("login"))

        image_file = request.files["image"]
        caption = request.form["caption"]

        if image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        else:
            image_data = None

        new_post = UserPost(user_id=session["user_id"], image=image_data, caption=caption)
        db.session.add(new_post)
        db.session.commit()

        flash("Post created successfully!")
        return redirect(url_for("home"))
    
    return render_template("create_post.html")

# Create a comment on a post
@app.route("/posts/<int:post_id>/comments", methods=["POST"])
def create_comment(post_id):
    if "user_id" not in session:
        flash("Unauthorized!")
        return redirect(url_for("login"))

    text = request.form["comment_text"]
    
    # Create a new comment with the user_id and post_id
    new_comment = CommentPost(user_id=session["user_id"], post_id=post_id, commentText=text)
    db.session.add(new_comment)
    db.session.commit()

    flash("Comment added successfully!")
    return redirect(url_for("home"))

# Edit a post
@app.route("/posts/<int:post_id>/edit", methods=["POST"])
def edit_post(post_id):
    post = UserPost.query.get_or_404(post_id)
    if post.user_id != session.get("user_id"):
        flash("Unauthorized access.")
        return redirect(url_for("home"))

    post.caption = request.form["caption"]
    if "image" in request.files:
        image_file = request.files["image"]
        if image_file.filename != "":
            post.image = base64.b64encode(image_file.read()).decode("utf-8")
    
    db.session.commit()
    flash("Post updated successfully!")
    return redirect(url_for("home"))

@app.route("/posts/<int:post_id>/delete", methods=["POST"])
def delete_post(post_id):
    post = UserPost.query.get_or_404(post_id)
    if post.user_id != session.get("user_id"):
        flash("Unauthorized access.")
        return redirect(url_for("home"))

    db.session.delete(post)
    db.session.commit()
    flash("Post deleted successfully!")
    return redirect(url_for("home"))

# Edit a comment
@app.route("/posts/<int:post_id>/comments/<int:comment_id>/edit", methods=["POST"])
def edit_comment(post_id, comment_id):
    comment = CommentPost.query.get_or_404(comment_id)
    if comment.user_id != session.get("user_id"):
        flash("Unauthorized access.")
        return redirect(url_for("home"))

    comment.commentText = request.form["comment_text"]
    db.session.commit()
    flash("Comment updated successfully!")
    return redirect(url_for("home"))

# Delete a comment
@app.route("/posts/<int:post_id>/comments/<int:comment_id>/delete", methods=["POST"])
def delete_comment(post_id, comment_id):
    comment = CommentPost.query.get_or_404(comment_id)
    if comment.user_id != session.get("user_id"):
        flash("Unauthorized access.")
        return redirect(url_for("home"))

    db.session.delete(comment)
    db.session.commit()
    flash("Comment deleted successfully!")
    return redirect(url_for("home"))


@app.route("/logout")
def logout():
    if "user_id" in session:
        flash(f"You have been logged out!", "info")

    session.pop("user_id", None)   
    session.pop("email", None) 
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)

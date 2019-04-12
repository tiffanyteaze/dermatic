from flask import Flask, g
from flask import render_template, flash, redirect, url_for, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import check_password_hash
from peewee import fn
from flask_bcrypt import generate_password_hash

from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_wtf import Form
from flask_wtf.file import FileField
from werkzeug import secure_filename

import models
import forms
import os

DEBUG = True
PORT = 8000

template_dir = os.path.abspath('./')
app = Flask(__name__, template_folder=template_dir, instance_relative_config=True)
app.config.from_pyfile('flask.cfg')
app.secret_key = 'adkjfalj.adflja.dfnasdf.asd'

# Sets variable images to uploader
images = UploadSet('images', IMAGES)
configure_uploads(app, images)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None

@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user

@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.db.close()
    return response

@app.route('/')
def index():
    if current_user.is_authenticated:
        from models import Review
        reviews = Review.select()
        print(reviews)
        return render_template('logged_in_landing.html', reviews=reviews)
    elif current_user.is_authenticated == False:
        return render_template('logged_out_landing.html')

@app.route('/register', methods=('GET', 'POST'))
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash('Yay you registered', 'success')
        models.User.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
            )
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("your email or password doesn't match", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                ## creates session
                login_user(user)
                flash("You've been logged in", "success")
                return redirect(url_for('index'))
            else:
                flash("your email or password doesn't match", "error")
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been logged out", "success")
    return redirect(url_for('index'))

@app.route('/product/<productid>', methods=('GET', 'POST'))
@login_required
def product(productid):
    from models import Review, Vote, User
    form = forms.ReviewForm()
    product = int(productid)

    reviews = (Review.select(Review.content, Review.product_id, User.id, User.username, Review.id, Review.buy_again, Review.helpful_votes, Review.not_helpful_votes).join(User).where(
        User.id == Review.user and Review.product_id == productid)).where(fn.length(Review.content) > 0)        

    buy_again_votes_total = reviews.count()
    buy_again_votes_true = 0

    for review in reviews:
        if review.buy_again == 1:
            buy_again_votes_true += 1
    if buy_again_votes_total > 0:
        buy_again_votes_percent = (buy_again_votes_true / buy_again_votes_total) * 100
    elif buy_again_votes_total == 0:
        buy_again_votes_percent = 0

    votes = (Vote.select(Vote.user, Vote.helpful, Review.id).join(Review).where(Vote.review == Review.id and Review.product_id == productid))

    voter_exists = False

    if votes:
        for vote in votes:
            if vote.user.id == current_user.id:
                voter_exists = True
    
    if form.validate_on_submit() and 'POST':
        if form.buy_again.data == True:
            models.Review.create(user=g.user._get_current_object(), 
            buy_again=1,
            content=form.content.data.strip(),
            product_id=product,
            helpful_votes=0,
            not_helpful_votes=0)
            flash("Review posted! Thanks!", "success")
            return redirect(url_for('product', productid=productid))
        else:
            models.Review.create(user=g.user._get_current_object(), 
            buy_again=0,
            content=form.content.data.strip(),
            product_id=product,
            helpful_votes=0,
            not_helpful_votes=0)
            flash("Review posted! Thanks!", "success")
            return redirect(url_for('product', productid=productid))
    elif request.method == 'POST':
        models.List.create_list_item(current_user.id, productid)
        return 'success'
    return render_template('product.html', form=form, product=product, reviews=reviews, currentuser=g.user.id, votes=votes, buy_again_votes_percent=buy_again_votes_percent, voter_exists=voter_exists)

@app.route('/delete/<productid>/user/<userid>', methods=['POST'])
@login_required
def delete_review(productid, userid):
    review = models.Review.select().where(models.Review.user == userid,
                                      models.Review.product_id == productid).get()
    votes = models.Vote.select().where(models.Vote.review == review.id)
    for vote in votes:
        vote.delete_instance()
    review.delete_instance()
    return redirect(url_for('product', productid=productid))

@app.route('/review_vote/<productid>/user/<userid>/review/<reviewid>', methods=['POST'])
@login_required
def review_vote(productid, userid, reviewid):
    review = models.Review.select().where(models.Review.user == userid,
                                      models.Review.product_id == productid).get()
    if request.method == 'POST':
        if request.form.get('helpful'):
            review.helpful_votes = review.helpful_votes + 1
            review.save()
            models.Vote.create(
                user=current_user.id,
                review=reviewid,
                helpful=1
            )
        elif request.form.get('not-helpful'):
            review.not_helpful_votes = review.not_helpful_votes + 1 
            review.save()
            models.Vote.create(
                user=current_user.id,
                review=reviewid,
                helpful=0
            )
    return redirect(url_for('product', productid=productid))

@app.route('/edit_vote/<productid>/user/<userid>/review/<reviewid>', methods=['POST'])
@login_required
def edit_vote(productid, userid, reviewid):
    from models import Review, Vote
    review = models.Review.select().where(models.Review.user == userid,
                                    models.Review.product_id == productid).get()
    vote = models.Vote.select().where(models.Vote.review == reviewid and models.Vote.user == current_user.id).get()

    if request.method == 'POST':
        print(request.form)
        if request.form.get('helpful'):
            review.helpful_votes = review.helpful_votes + 1
            review.save()
            vote.helpful=True
            vote.save()
        elif request.form.get('not-helpful'):
            print("You got to the not helpful condition")
            review.not_helpful_votes = review.not_helpful_votes + 1 
            review.save()
            vote.helpful=False
            print(vote.helpful)
            vote.save()
            print(vote.helpful)
    return redirect(url_for('product', productid=productid))

@app.route('/product/<productid>/comparison_chart')
@login_required
def comparison_chart(productid):
    return render_template('comparison.html', product=productid)

@app.route('/edit/<productid>/user/<userid>', methods=['GET', 'POST'])
@login_required
def edit_review(productid, userid):
    form = forms.ReviewForm()
    user_id = int(userid)
    product_id = int(productid)
    review = models.Review.select().where(models.Review.user == user_id,
                                      models.Review.product_id == product_id).get()
    if form.validate_on_submit():
        if form.buy_again.data == True:
            review.buy_again = 1
        elif form.buy_again.data == False:
            review.buy_again = 0
        review.content = form.content.data
        review.save()
        return redirect(url_for('product', productid=productid))
    return render_template('edit-review.html', form=form, userid=user_id)

@app.route('/user/<username>/edit', methods=['GET', 'POST'])
@login_required
def update_user(username):
    form = forms.UserForm()
    user = models.User.select().where(models.User.username == username).get()
    if form.validate_on_submit():
        filename = images.save(request.files['profile_image'])
        url = images.url(filename)
        user.username = form.username.data
        user.email = form.email.data
        user.password = generate_password_hash(form.password.data)
        user.first_name = form.first_name.data
        user.avatar = filename
        user.image_url = url
        user.save(only=user.dirty_fields)
        return redirect(url_for('user', userid=current_user.id))
    return render_template('edit_user.html', user=user, form=form)

@app.route('/user/<userid>')
@login_required
def user(userid):
    user = models.User.select().where(models.User.id == current_user.id).get()
    list = current_user.get_list().limit(100)
    return render_template('user_profile.html', user=user, list=list)

@app.route('/delete_fav/<productid>/user/<userid>', methods=['POST'])
@login_required
def delete_fav(productid, userid):
    list = models.List.select().where(models.List.user == userid,
                                      models.List.product_id == productid).get()
    list.delete_instance()
    return redirect(url_for('user', userid=current_user.id))

if __name__ == '__main__':
    models.initialize()
    app.run(debug=DEBUG, port=PORT)
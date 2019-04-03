from flask import Flask, g
from flask import render_template, flash, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import check_password_hash
from peewee import fn

import models
import forms

DEBUG = True
PORT = 8000

app = Flask(__name__)
app.secret_key = 'adkjfalj.adflja.dfnasdf.asd'

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
    return render_template('layout.html')

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
    from models import Review, User
    form = forms.ReviewForm()
    product = int(productid)
    print(current_user.username)
    reviews = (Review.select(Review.content, Review.product_id, User.id, User.username).join(User).where(
        User.id == Review.user and Review.product_id == productid)).where(fn.length(Review.content) > 0)
    if form.validate_on_submit():
        models.Review.create(user=g.user._get_current_object(),
                           content=form.content.data.strip(),
                           product_id=product)
        flash("Review posted! Thanks!", "success")
        return redirect(url_for('product', productid=productid))
    return render_template('product.html', form=form, product=product, reviews=reviews, currentuser=g.user.id)

@app.route('/delete/<productid>/user/<userid>', methods=['POST'])
@login_required
def delete_review(productid, userid):
    review = models.Review.select().where(models.Review.user == userid,
                                      models.Review.product_id == productid).get()
    review.delete_instance()
    return redirect(url_for('product', productid=productid))

@app.route('/edit/<productid>/user/<userid>', methods=['GET', 'POST'])
@login_required
def edit_review(productid, userid):
    form = forms.ReviewForm()
    user_id = int(userid)
    product_id = int(productid)
    review = models.Review.select().where(models.Review.user == user_id,
                                      models.Review.product_id == product_id).get()
    if form.validate_on_submit():
        print(form.content.data)
        print(review)
        review.content = form.content.data
        review.save()
        return redirect(url_for('product', productid=productid))
    return render_template('edit-review.html', form=form, userid=user_id)

if __name__ == '__main__':
    models.initialize()
    try:
        models.User.create_user(
            username='tiffany',
            email="tteaze@gmail.com",
            password='password',
            admin=True
            )
    except ValueError:
        pass

    app.run(debug=DEBUG, port=PORT)
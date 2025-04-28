from app import app
from flask import render_template, flash, redirect, url_for, request, session
from urllib.parse import urlsplit
from app.forms import LoginForm, RegistraionForm
from flask_login import login_user, current_user, logout_user, login_required
from app.models import User
from app import db
import sqlalchemy as sa

# decorator to expire regular session
# @app.before_request
# def make_session_permanent():
#     session.permanent = True


@app.route("/")
@app.route("/index")
@login_required
def index():
    # return render_template('index.html', title="Home Page", posts=posts)
    return render_template('index.html', title="Home Page")


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistraionForm()

    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations! You are now a registered user.')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        query = sa.select(User).where(User.username == form.username.data)
        user = db.session.scalar(query)

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get('next')

        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('login.html', title="Login Page", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

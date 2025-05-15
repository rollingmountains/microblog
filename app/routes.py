from app import app, db, email
from flask import render_template, flash, redirect, url_for, request, session
from urllib.parse import urlsplit
from app.forms import LoginForm, RegistraionForm, EditProfileForm, EmptyForm, PostForm, ResetPasswordRequestForm, ResetPasswordForm
from flask_login import login_user, current_user, logout_user, login_required
from app.models import User, Post
import sqlalchemy as sa
from datetime import datetime, timezone
from langdetect import detect, LangDetectException


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@app.route("/",  methods=['POST', 'GET'])
@app.route("/index", methods=['POST', 'GET'])
@login_required
def index():
    # instantiate and validate the PostForm
    form = PostForm()

    if form.validate_on_submit():
        try:
            language = detect(form.post.data)
        except LangDetectException:
            language = ''
        post = Post(body=form.post.data,
                    author=current_user, language=language)
        db.session.add(post)
        db.session.commit()
        flash(f'You have successfully posted a message')
        return redirect(url_for('index'))

        # pull current users own and follwing user's post list using pagination
    query = current_user.following_posts()
    page = request.args.get('page', 1, type=int)
    per_page = int(app.config['ITEMS_PER_PAGE'])
    posts = db.paginate(
        query, page=page, per_page=per_page, error_out=True)

    # construct next page url and prev page url using paginate object attributes
    next_url = url_for(
        'index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for(
        'index', page=posts.prev_num) if posts.has_prev else None

    return render_template('index.html', title="Home Page", form=form, posts=posts.items, next_url=next_url, prev_url=prev_url)


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


@app.route("/user/<username>")
@login_required
def user(username):
    # check user in db and throw error if not found
    user = db.first_or_404(sa.select(User).where(User.username == username))

    # build query using paginate to pull all posts by the user
    query = sa.select(Post).where(Post.user_id == user.id)
    page = request.args.get('page', 1, type=int)
    per_page = int(app.config['ITEMS_PER_PAGE'])
    posts = db.paginate(query, page=page, per_page=per_page, error_out=True)

    # construct next_url and prev_url for page navigation
    next_url = url_for(
        'user', username=user.username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for(
        'user', username=user.username, page=posts.prev_num) if posts.has_prev else None

    # instantiate follow or unfollow button in user page
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts.items, form=form,  next_url=next_url, prev_url=prev_url)


@app.route("/edit_profile", methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template('edit_profile.html', title='Edit Profile',  form=form)


@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()

    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username))

        if user is None:
            flash(f'Sorry the user with {username} does not exist.')
            return redirect(url_for('index'))

        if user == current_user:
            flash(f'Sorry, you cannot follow yourself!')
            return redirect(url_for('user', username=username))

        current_user.follow(user)
        db.session.commit()
        flash(f'You are now following the user {username}')
        return redirect(url_for('user', username=username))

    else:
        return redirect(url_for('index'))


@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()

    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username))

        if user is None:
            flash(f'No user {user.username} exists!')
            return redirect(url_for('index'))

        if user == current_user:
            flash(f'Sorry! You cannot unfollow yourself!')
            return redirect(url_for('user', username=username))

        current_user.unfollow(user)
        db.session.commit()
        flash(f'You have unfollowed {username}')
        return redirect(url_for('user', username=username))

    else:
        return redirect(url_for('index'))


@app.route('/explore')
@login_required
def explore():
    query = sa.select(Post).order_by(Post.timestamp.desc())
    page = request.args.get('page', 1, type=int)
    per_page = int(app.config['ITEMS_PER_PAGE'])
    posts = db.paginate(query, page=page, per_page=per_page, error_out=True
                        )
    next_url = url_for(
        'explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for(
        'explore', page=posts.prev_num) if posts.has_prev else None

    return render_template('index.html', title='Explore', posts=posts.items,  next_url=next_url, prev_url=prev_url)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = ResetPasswordRequestForm()

    if form.validate_on_submit():
        query = sa.select(User).where(User.email == form.email.data)
        user = db.session.scalar(query)

        if user:
            email.send_password_reset_email(user)
        flash(f'Check your email for instructions to reset your password')
        return redirect(url_for('login'))

    return render_template('reset_password_request.html', title='Password Reset', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    user = User.verify_reset_password_token(token)

    if not user:
        return redirect(url_for('index'))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        if user.verify_reset_password(form.password.data):
            user.set_password(form.password.data)
            db.session.commit()
            flash('You have successfully reset your password.')
            return redirect(url_for('login'))
        else:
            flash(
                'Sorry, new password cannot be same as last 3 passwords. Enter another one')
            return redirect(url_for('reset_password', token=token))

    return render_template('reset_password.html', form=form)

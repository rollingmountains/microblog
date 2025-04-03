from app import app
from flask import render_template, flash, redirect, url_for
from app.forms import LoginForm

# mock data
user = {'username': 'bond'}
posts = [{
    'title': 'Experience',
    'author': 'John Doe',
    'body': 'Good day in Kathmandu',
    'date_published': '22, April 2024',
},
    {
    'title': 'Movie time',
    'author': 'Jane Smith',
    'body': 'That was a wonderful movie.',
    'date_published': '21, April 2024',
}]


@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html', title="Home Page", posts=posts)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash(
            f'Login requested for {form.username.data}. Remember Me = {form.remember_me.data}')
        return redirect(url_for('index'))
    return render_template('login.html', title="Login Page", form=form)

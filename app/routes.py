from app import app
from flask import render_template

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

    return render_template('index.html', title="Home Page", user=user, posts=posts)

from flask import Flask, render_template, redirect, request, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_user import login_required, UserManager, UserMixin, SQLAlchemyAdapter, current_user
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField

import os

app = Flask(__name__)
Bootstrap(app)

app.config['SECRET_KEY'] = 'supersecretkeygoeshere'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['CSRF_ENABLED'] = True
app.config['USER_ENABLE_EMAIL'] = False
app.config['USER_APP_NAME'] = "Flask App"
app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd() + '/static/tmp'

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)  # set maximum file size, default is 16MB

db = SQLAlchemy(app)


class UploadForm(FlaskForm):
    photo = FileField(validators=[FileAllowed(photos, u'Image only!'), FileRequired(u'File was empty!')])
    submit = SubmitField(u'Upload')


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')
    active = db.Column(db.Boolean(), nullable=False, server_default='0')


db_adapter = SQLAlchemyAdapter(db, User)
user_manager = UserManager(db_adapter, app)


@app.route('/profile')
@login_required
def profile():
    return render_template('pages/user_profile.html')


@app.route('/')
@app.route('/home')
def home():
    return render_template('pages/home.html', active='home')

@app.route('/about')
def about():
    return render_template('pages/about.html', active='about')

@app.route('/contact')
def contact():
    return render_template('pages/contact.html', active='contact')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        filename = photos.save(form.photo.data, folder=current_user.username, name="tmp.")
        file_url = photos.url(filename)
    else:
        file_url = None
    return render_template('pages/upload.html', active='upload', form=form, file_url=file_url)


if __name__ == '__main__':
    app.run()

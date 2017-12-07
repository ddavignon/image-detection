from flask import Flask, render_template, redirect, request, url_for, flash, jsonify, session
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_user import login_required, UserManager, UserMixin, SQLAlchemyAdapter, current_user
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
# from flask_wtf import FlaskForm
from flask_dropzone import Dropzone
# from flask_wtf.file import FileField, FileRequired, FileAllowed
# from wtforms import SubmitField
from face_detection import check_image_for_minors
import uuid


import os

app = Flask(__name__)
Bootstrap(app)
dropzone = Dropzone(app)


app.config['SECRET_KEY'] = 'supersecretkeygoeshere'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CSRF_ENABLED'] = True
app.config['USER_ENABLE_EMAIL'] = False
app.config['USER_APP_NAME'] = "Flask App"

# Dropzone setting
app.config['DROPZONE_UPLOAD_MULTIPLE'] = True
app.config['DROPZONE_ALLOWED_FILE_CUSTOM'] = True
app.config['DROPZONE_ALLOWED_FILE_TYPE'] = 'image/*'
app.config['DROPZONE_REDIRECT_VIEW'] = 'results'

# Uploads settings
app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd() + '/static/tmp/uploads'

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)  # set maximum file size, default is 16MB

db = SQLAlchemy(app)


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

    
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    # set session for image results
    if "file_urls" not in session:
        session['file_urls'] = []
    file_urls = session['file_urls']
    
    # handle image upload from Dropszone
    if request.method == 'POST':
        directory_name=os.getcwd()+"/static/tmp/uploads"
        raw_files = request.files
        for raw_file in raw_files:
            file = request.files.get(raw_file) 
            
            ext = os.path.splitext(file.filename)[1]
            unique_name = uuid.uuid4().hex + ext
            # initial save of photo to test    
            filename = photos.save(
                file,
                name=unique_name    
            )
            # check image for minors / sanitize image
            check_image_for_minors(directory_name + "/" + unique_name)
            
            # append image urls
            file_urls.append(photos.url(filename))
            
        session['file_urls'] = file_urls
    
    # return dropzone template on GET request    
    return render_template('pages/upload.html', active='upload', file_urls=file_urls)


@app.route('/results')
@login_required
def results():
    if "file_urls" not in session or session['file_urls'] == []:
        return redirect(url_for('upload'))
    file_urls = session['file_urls']
    session.pop('file_urls', None)
    return render_template("pages/files.html", file_urls=file_urls)


if __name__ == '__main__':
    db.create_all()
    app.run(
        host=os.getenv('IP', '0.0.0.0'),
        port=int(os.getenv('PORT', 8080)),
        debug=True
    )

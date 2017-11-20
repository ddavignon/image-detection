from flask import Flask, render_template, redirect, request, url_for, flash
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_user import login_required, UserManager, UserMixin, SQLAlchemyAdapter, current_user
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
from PIL import Image, ImageFilter
import uuid

from sightengine.client import SightengineClient

import os

app = Flask(__name__)
Bootstrap(app)


app.config['SECRET_KEY'] = 'supersecretkeygoeshere'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['CSRF_ENABLED'] = True
app.config['USER_ENABLE_EMAIL'] = False
app.config['USER_APP_NAME'] = "Flask App"


app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd() + '/static/tmp/uploads'

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)  # set maximum file size, default is 16MB

db = SQLAlchemy(app)


class UploadForm(FlaskForm):
    photo = FileField(validators=[FileAllowed(['jpeg','jpg', 'png'], u'Image only!'), FileRequired(u'File was empty!')])
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


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        file_urls = []
        files = request.files.getlist('photo')
        # file_names = []
        directory_name=os.getcwd()+"/static/tmp/uploads"
        
        for file in files:
            # create unique identifier for image
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
        
        flash(u'Photos saved successfully!', 'success')
        return render_template("pages/files.html", file_urls=file_urls)
    else:
        file_urls = []
    return render_template('pages/upload.html', active='upload', form=form, file_urls=file_urls)


client = SightengineClient('1815250773', 'oGKFfnDkDkcoKcH3x2hw')
def check_image_for_minors(image):
    # output = client.check('face-attributes').set_url(image_url)
    output = client.check('face-attributes').set_file(image)
    
    for face in output['faces']:
        if 'attributes' in face:
            if face['attributes']['minor'] > 0.85:
                print("child image found")
                imgpil = Image.open(image)
                imgwidth = imgpil.size[0]
                imgheight = imgpil.size[1]
    
                x1 = face['x1']
                y1 = face['y1']
                x2 = face['x2']
                y2 = face['y2']
    
                xx1 = int(round(float(x1 * imgwidth)))
                yy1 = int(round(float(y1 * imgheight)))
                xx2 = int(round(float(x2 * imgwidth)))
                yy2 = int(round(float(y2 * imgheight)))
    
                baby = imgpil.copy()
                blurredbaby = baby.crop((xx1, yy1, xx2, yy2))
    
                blurredbaby = blurredbaby.filter(ImageFilter.GaussianBlur(3))
                baby.paste(blurredbaby, (xx1, yy1))
                baby.save(image)
                
    print("done!")
    

if __name__ == '__main__':
    db.create_all()
    app.run(
        host=os.getenv('IP', '0.0.0.0'),
        port=int(os.getenv('PORT', 8080)),
        debug=True
    )

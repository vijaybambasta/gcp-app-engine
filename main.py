
import imghdr
from multiprocessing import context
from google.cloud import storage
import os
from flask import Flask, render_template, request, redirect, url_for, abort, \
    send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image



app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5000
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['MAX_WIDTH'] = 400
app.config['MAX_LENGTH'] = 300

app.config['UPLOAD_PATH'] = r'C:\shelf\projects\photoholic\gcp\uploadhere'
CLOUD_STORAGE_BUCKET = "mystorefilesbucket"

def validate_image(stream):
    header = stream.read(512)  # 512 bytes should be enough for a header check
    stream.seek(0)  # reset stream pointer
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')

@app.route('/')
def index():    
    return render_template('index.html', content="first")

@app.route('/success')
def uploaded_success():    
    return render_template('success.html', data="firssdfst")


@app.route('/', methods=['POST'])
def upload_files():
    uploaded_file = request.files['file']

    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS'] or \
                file_ext != validate_image(uploaded_file.stream):
            # Place holder for error message    
            return render_template('error.html', error="File externsion supporte are png and jpeg only")

        # OK to upload
        uploaded_file.seek(0, os.SEEK_END)
        file_size = uploaded_file.tell()


        # Do validation 
        if file_size > app.config["MAX_CONTENT_LENGTH"]:
            return render_template('error.html', error="File size limit upto in byte: {max_length}, current file size is {actual_size}".format(max_length=app.config["MAX_CONTENT_LENGTH"], actual_size=file_size))

       
        im = Image.open(uploaded_file)
        width, height = im.size

        if width > app.config["MAX_WIDTH"] or height > app.config["MAX_LENGTH"]:
            return render_template('error.html', error="File Resolution must be {width} x {length}, your current file resolution is: {a_width} x {a_height}".format(
                width = app.config["MAX_WIDTH"], length=app.config["MAX_LENGTH"], a_width=width, a_height=height))

        try:

            storage_client = storage.Client()
            bucket = storage_client.get_bucket(CLOUD_STORAGE_BUCKET)
            blob = bucket.blob(uploaded_file.filename)

            blob.upload_from_string(
                    uploaded_file.read(),
                    content_type = uploaded_file.content_type
                    )
            blob.make_public()
            blob_url = blob.public_url
        except Exception as e:
            return render_template('error.html', error="uknown error, try after some time" )

    # If all goes well

    return render_template('success.html',  file_size=file_size,  width=width, height=height)
    
@app.route('/display/<filename>')
def display_image(filename):
	#print('display_image filename: ' + filename)
	return redirect(url_for('static', filename='uploads/' + filename), code=301)



@app.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)




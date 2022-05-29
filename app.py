from flask import Flask, render_template, send_file, flash
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os
from wtforms.validators import InputRequired
from Melody_Generator import initialize_generator
app = Flask(__name__)


app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'static/files'
ALLOWED_EXTENSIONS = {'mid'}
# app.config['DOWNLOAD_FOLDER']='static/output'

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")
    #call the function melody generator

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET',"POST"])
@app.route('/home', methods=['GET',"POST"])
def home():

    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data # First grab the file
        print("Input File is",file)
        if allowed_file(file.filename):
            file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename)))
            initialize_generator()
            return render_template('index.html', form=form, response='Done')
        else:
            flash("Only MIDI files are allowed(.mid files)")# Then save the file
        # print("Calling generator")




    return render_template('index.html', form=form,response='')

@app.route("/download/",methods=['POST'])
def return_files_tut():
    DOWNLOAD_FOLDER = 'static/output/mel.mid'
    file_path=DOWNLOAD_FOLDER

    return send_file(file_path, as_attachment=True, attachment_filename='result.midi')

if __name__ == '__main__':
    app.run(debug=True)





































# from flask import Flask
#
# app = Flask(__name__)
#
# @app.route("/")
# def hello_world():
#     return "<p>Hello, World!</p>"


# from flask import Flask, render_template, request
# from werkzeug.utils import secure_filename
#
# app = Flask(__name__)
#
#
# @app.route('/upload')
# def upload_file():
#     return render_template('upload.html')
#
#
# @app.route('/uploader', methods=['GET', 'POST'])
# def upload_files():
#     if request.method == 'POST':
#         f = request.files['file']
#         f.save(secure_filename(f.filename))
#         return 'file uploaded successfully'
#
#
# if __name__ == '__main__':
#     app.run(debug=True)
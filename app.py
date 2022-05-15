from flask import Flask, render_template,send_file
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os
from wtforms.validators import InputRequired
from Melody_Generator import initialize_generator

app = Flask(__name__)

DOWNLOAD_FOLDER='static/output/mel.mid'
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'static/files'
# app.config['DOWNLOAD_FOLDER']='static/output'

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")
    #call the function melody generator

@app.route('/', methods=['GET',"POST"])
@app.route('/home', methods=['GET',"POST"])
def home():
    response=''
    recieved_input=''
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data # First grab the file
        print("Input FIle is",file)
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename))) # Then save the file
        print("Calling generator")
        initialize_generator()
        return render_template('index.html',form=form, response='Done')
    #recieved_input=file

    return render_template('index.html', form=form,response='')

# @app.route('/download')
# def downloadFile ():
#     #For windows you need to use drive name [ex: F:/Example.pdf]
#     path = "/mel.mid"
#     return send_file(path, as_attachment=True)
# Download API
# @app.route("/downloadfile/file", methods = ['GET'])
# def download_file(file):
#     return render_template('index.html',value=file)
#
# @app.route('/file')
# def return_files_tut(filename):
#     file_path = DOWNLOAD_FOLDER + filename
#     return send_file(file_path, as_attachment=True, attachment_filename='')
@app.route("/download/",methods=['POST'])
def return_files_tut():
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
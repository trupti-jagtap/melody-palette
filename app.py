from flask import Flask , request, render_template
app = Flask(__name__)

@app.route("/")
def index():

    return render_template('index.html')

@app.route("/predict", methods = ['GET','POST'])
def predict():
    
    if request.method == 'POST':
        
        file = request.files['file']
        filename = file.filename
        file_path = os.path.join(r'D:/Music Project/', filename) #slashes should be handeled properly
        file.save(file_path)
        print(filename)
        product = prediction(file_path)
        print(product)
        
    return render_template('index.html')

if __name__ == "__main__":
    app.run()
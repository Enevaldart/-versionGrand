import time
from flask import Flask, render_template,  request
from werkzeug.utils import secure_filename
import os
from flask import send_file
import io
import PyPDF2
import pyttsx3
import pdfplumber


app = Flask(__name__)

engine = pyttsx3.init()
ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
   return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
#@cross_origin()
def index():
        return render_template('index.html')


@app.route('/Behind_the_making', methods=['GET', 'POST'])
def behind_the_making():
    return render_template('Profile.html')


@app.route('/Terms_of_service', methods=['GET', 'POST'])
def Terms_of_service():
    return render_template('terms.html')

#Analyse the target file to produce audio
@app.route("/convert_pdf", methods=['GET', 'POST'])
def convert_pdf():
    #request file through post method
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            #convert the pdf file into audio
            try:
                pdfReader = PyPDF2.PdfFileReader(file)
                pages = pdfReader.numPages
                finalText = ""
                with pdfplumber.open(file) as pdf:
                    for i in range(0, pages):
                        page = pdf.pages[i]
                        text = page.extract_text()
                        finalText += text
                        finalText = ' '.join(finalText.splitlines())

                engine = pyttsx3.init()
                voices = engine.getProperty('voices')
                engine.setProperty('voice', voices[1].id)
                engine.setProperty('rate', 170)

                # synthesizing the text as audio using pyttsx3
                audio_file = io.BytesIO()
                engine.save_to_file(finalText, audio_file)
                audio_file.seek(0)

                engine.runAndWait()
                timestr = time.strftime("%Y%m%d_%H%M%S")
                download_file="ListenToPdf"+timestr+filename
                base, ext = os.path.splitext(download_file)
                download_file = base + '.' + 'mp3'
                return send_file(audio_file, as_attachment=True, attachment_filename=download_file)

            #finally if everything goes well and by chance the execution is terminated
            finally:
                print('Everything went smooth!')

    #return notification if the file type is wrong
        return render_template('wrongfile.html')


if __name__ == "__main__":
    app.run()

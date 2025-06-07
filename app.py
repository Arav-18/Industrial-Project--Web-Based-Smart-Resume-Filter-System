import os
from flask import Flask, request, redirect, flash, url_for, render_template_string
from resume_parser import extract_text_from_resume, extract_text_from_jd, match_score

app = Flask(__name__)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Resume Upload</title>
            <style>
                body {
                    font-family: 'Segoe UI', sans-serif;
                    background: linear-gradient(135deg, #141e30, #243b55);
                    color: white;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    height: 100vh;
                    margin: 0;
                }
                form {
                    background: #1c1c1c;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 0 20px rgba(0,255,255,0.2);
                    text-align: center;
                }
                h1 {
                    margin-bottom: 20px;
                }
                input[type="file"] {
                    padding: 10px;
                    margin: 20px 0;
                    background: #fff;
                    color: #000;
                    border: none;
                    border-radius: 5px;
                }
                input[type="submit"] {
                    padding: 10px 25px;
                    font-size: 16px;
                    background-color: #00ffff;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    font-weight: bold;
                }
                input[type="submit"]:hover {
                    background: #00cccc;
                }
                ul {
                    color: red;
                }
            </style>
        </head>
        <body>
            <form method="POST" action="/upload" enctype="multipart/form-data">
                <h1>Upload Your Resume</h1>
                <input type="file" name="resume" required><br>
                <input type="submit" value="Upload">
                {% with messages = get_flashed_messages() %}
                {% if messages %}
                    <ul>
                    {% for msg in messages %}
                        <li>{{ msg }}</li>
                    {% endfor %}
                    </ul>
                {% endif %}
                {% endwith %}
            </form>
        </body>
        </html>
    ''')

@app.route('/upload', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        flash("No file part")
        return redirect(url_for('index'))

    file = request.files['resume']
    if file.filename == '':
        flash("No file selected")
        return redirect(url_for('index'))

    if file and allowed_file(file.filename):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        jd_file = os.path.join('jd', 'software_engineer.txt')
        if not os.path.exists(jd_file):
            return "<h2>❗JD file not found at jd/software_engineer.txt</h2>"

        resume_text = extract_text_from_resume(filepath)
        jd_text = extract_text_from_jd(jd_file)
        score = match_score(resume_text, jd_text)

        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Resume Match Result</title>
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
                    height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-family: 'Segoe UI', sans-serif;
                    color: white;
                }}
                .card {{
                    background: #1a1a2e;
                    padding: 40px 60px;
                    border-radius: 20px;
                    box-shadow: 0 0 30px rgba(0, 255, 255, 0.2);
                    text-align: center;
                    max-width: 600px;
                    animation: fadeIn 1s ease-out;
                }}
                .glow-title {{
                    font-size: 36px;
                    margin-bottom: 20px;
                    color: #fff;
                    text-shadow: 0 0 5px #fff, 0 0 10px #0ff, 0 0 20px #0ff;
                }}
                .score {{
                    font-size: 70px;
                    font-weight: bold;
                    background: linear-gradient(90deg, #ff00cc, #3333ff, #00ffff);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    text-shadow: 0 0 20px #0ff;
                    animation: pulse 2s infinite ease-in-out;
                }}
                .info {{
                    margin-top: 20px;
                    font-size: 18px;
                    color: #ccc;
                }}
                a {{
                    display: inline-block;
                    margin-top: 30px;
                    padding: 12px 25px;
                    background: #00ffff;
                    color: #000;
                    font-weight: bold;
                    border-radius: 8px;
                    text-decoration: none;
                    box-shadow: 0 0 10px #0ff;
                    transition: 0.3s;
                }}
                a:hover {{
                    background: #00cccc;
                    box-shadow: 0 0 20px #0ff;
                }}
                @keyframes pulse {{
                    0% {{ text-shadow: 0 0 10px #0ff; }}
                    50% {{ text-shadow: 0 0 30px #0ff; }}
                    100% {{ text-shadow: 0 0 10px #0ff; }}
                }}
                @keyframes fadeIn {{
                    from {{ opacity: 0; transform: scale(0.9); }}
                    to {{ opacity: 1; transform: scale(1); }}
                }}
            </style>
        </head>
        <body>
            <div class="card">
                <div class="glow-title">✅ Resume Uploaded Successfully</div>
                <div class="score">{score}%</div>
                <div class="info">Match Score based on your resume and job description</div>
                <a href="/">Upload Another Resume</a>
            </div>
        </body>
        </html>
        """

    else:
        return "<h2>❌ Invalid file format. Please upload PDF or DOCX only.</h2><br><a href='/'>Try Again</a>"

if __name__ == '__main__':
    app.run(debug=True)

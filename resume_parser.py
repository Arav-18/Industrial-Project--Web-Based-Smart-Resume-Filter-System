import os
import docx2txt
import PyPDF2

def extract_text_from_resume(filepath):
    text = ''
    ext = filepath.split('.')[-1].lower()

    if ext == 'pdf':
        with open(filepath, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                text += page.extract_text()
    elif ext == 'docx':
        text = docx2txt.process(filepath)
    else:
        text = ''
    
    return text.lower()

def extract_text_from_jd(jd_file):
    with open(jd_file, 'r', encoding='utf-8') as f:
        return f.read().lower()

def match_score(resume_text, jd_text):
    resume_words = set(resume_text.split())
    jd_words = set(jd_text.split())
    match = resume_words.intersection(jd_words)
    if not jd_words:
        return 0
    score = (len(match) / len(jd_words)) * 100
    return round(score, 2)

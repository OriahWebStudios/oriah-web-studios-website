import uuid
from flask import url_for, render_template
from app import mail
from flask_mail import Message
import os

def generate_meeting_link():
    meeting_id = uuid.uuid4().hex
    meeting_url = url_for('main.video_confrence', meeting_id=meeting_id, _external=True)
    return meeting_url

def send_email(to, subject, template, **kwargs):
    msg = Message(subject, recipients=[to])
    msg.sender = os.environ.get('MAIL_DEFAULT_SENDER')
    msg.html = render_template(template, **kwargs)
    mail.send(msg)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'docx', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
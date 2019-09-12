import tempfile 
import os
import time
import subprocess
import parsedatetime
import smtplib
import configparser


from googlevoice import Voice
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders


ed  = os.environ.get('EDITOR', 'vim')
cal = parsedatetime.Calendar();
config = configparser.ConfigParser();
config.read('/home/dominic/src/butterfly/butterfly.cfg');



def email(address, subject, body, attach):

    gmail_user = config['mail']['email']
    gmail_password = config['mail']['password']
    from_addr  = gmail_user

    msg = MIMEMultipart();
    msg['From'] = gmail_user;
    msg['To']   = address;
    mimebody = MIMEText(body, 'html');
    msg.attach(mimebody);

    if attach == "": attach = None;

    if attach:
       part = MIMEBase('application', "octet-stream")
       part.set_payload(open(attach, "rb").read())
       Encoders.encode_base64(part)
       part.add_header('Content-Disposition', 'attachment; filename="'+filename+'"')
       msg.attach(part)

    if True:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(from_addr, address, msg.as_string())
        server.close()


def text_login():
    voice = Voice();
    voice.login(
                config['text']['username'], 
                config['text']['password']
    );
    return voice;


def text(number, msg, voice=None):
    if not voice: voice = text_login();
    voice.send_sms(number, msg);


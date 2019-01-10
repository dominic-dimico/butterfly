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
textconfig = configparser.ConfigParser();
textconfig.read('text.cfg');
mailconfig = configparser.ConfigParser();
mailconfig.read('mail.cfg');



def vim(note):
    if not note: note = ""
    tf = tempfile.NamedTemporaryFile(suffix=".tmp", delete=False);
    tf.write(note)
    tf.flush()
    name = tf.name
    tf.close()
    tf = open(name, 'rw')
    subprocess.call([ed, tf.name])
    tf.flush()
    note = tf.read()
    os.unlink(tf.name)
    return note



def str2dt(string):
      parsed = cal.parse(string)[0]
      dt = time.strftime('%Y-%m-%d %H:%M:%S', parsed)
      return dt;



def email(address, subject, body, attach):
    gmail_user = mailconfig['main']['email']
    gmail_password = mailconfig['main']['password']
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



def text(number, msg):
    voice = Voice();
    voice.login(
                textconfig['main']['username'], 
                textconfig['main']['password']
    );
    voice.send_sms(number, msg);


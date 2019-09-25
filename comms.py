import tempfile 
import os
import time
import subprocess
import parsedatetime
import smtplib
import configparser
import code

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from googlevoice import Voice
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders


ed  = os.environ.get('EDITOR', 'vim')


class Comms():


    def __init__(self):
        self.cal = parsedatetime.Calendar();
        self.config = configparser.ConfigParser();
        self.config.read('/home/dominic/src/butterfly/butterfly.cfg');



    def email(self, address, subject, body, attach):

        gmail_user     = self.config['mail']['email']
        gmail_password = self.config['mail']['password']
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



    def text_login(self):
        voice = Voice();
        voice.login(
                    self.config['text']['username'], 
                    self.config['text']['password']
        );
        return voice;



    def text(self, number, msg, voice=None):
        if not voice: voice = text_login();
        voice.send_sms(number, msg);



    def voice_login(self):

        chrome_options = webdriver.ChromeOptions()
        #chrome_options.add_argument("headless");
        prefs = {"profile.default_content_setting_values.notifications" : 2}
        chrome_options.add_experimental_option("prefs",prefs)
        driver = webdriver.Chrome(chrome_options=chrome_options, executable_path='/usr/lib/chromium-browser/chromedriver');
        driver.get("http://voice.google.com");

        loginbutton = driver.find_element_by_class_name("signUpLink")
        loginbutton.click();

        username = driver.find_element_by_id("identifierId");
        username.send_keys("dominic.dimico@gmail.com");
        username.send_keys(Keys.ENTER);
        time.sleep(3);

        password = driver.find_element_by_id("password");
        passwordbox = password.find_element_by_tag_name("input");
        passwordbox.send_keys("***REMOVED***");
        passwordbox.send_keys(Keys.ENTER);
        time.sleep(7);

        #code.interact(local=locals());

        navitems = driver.find_elements_by_css_selector("a.navListItem.mat-list-item.gmat-nav-list-item");
        labels = map(lambda x: x.get_attribute("aria-label"), navitems)
        msgindexes = []
        for index in range(len(labels)):
            if labels[index] == "Messages":
               msgindexes.append(index);
        for msgindex in msgindexes:
            try: navitems[msgindex].click();
            except: pass;
        time.sleep(2);

        self.driver = driver;
        return driver;

        



    def voice_text(self, number, msg):

        try:
            messagebutton = self.driver.find_element_by_css_selector("div.gmat-subhead-2.grey-900")
            time.sleep(1); 
            messagebutton.click();
            time.sleep(1); 
            numberbox = self.driver.find_elements_by_tag_name("input")[1]
            time.sleep(1); 
            numberbox.send_keys(number);
            time.sleep(1); 
            numberbox.send_keys(Keys.ENTER);
            time.sleep(1); 
            numberbox.send_keys(Keys.ESCAPE);
            time.sleep(1); 
            textarea = self.driver.find_element_by_tag_name("textarea");
            time.sleep(1); 
            textarea.click();
            time.sleep(1); 
            textarea.send_keys(msg);
            time.sleep(1); 
            textarea.send_keys(Keys.ENTER);
            time.sleep(1); 
        except:
            code.interact(local=locals());

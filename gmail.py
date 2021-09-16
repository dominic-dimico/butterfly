import base64
import configparser
import os
import webbrowser

from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText
from email.mime.audio     import MIMEAudio
from email.mime.image     import MIMEImage
from email.mime.base      import MIMEBase

from googleapiclient.discovery import build;
from google.oauth2.credentials import Credentials;
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class GMailAgent():


    def __init__(self, credpath='/home/dominic/.credentials/gmail/'):
        self.authenticate(credpath);


    def authenticate(self, credpath='/home/dominic/.credentials/gmail/'):
      self.scopes = ['https://mail.google.com/']
      creds = None;
      if os.path.exists(credpath+'token.json'):
         creds = Credentials.from_authorized_user_file(credpath+'token.json', self.scopes)
      if not creds or not creds.valid:
         if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request());
         else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credpath+'credentials.json', 
                self.scopes
            )
            creds = flow.run_local_server(port=0)
         with open(credpath+'token.json', 'w') as token:
               token.write(creds.to_json())
      self.gmailer = build('gmail', 'v1', credentials=creds);


    def search_messageids(self, query):
          result = self.gmailer.users().messages().list(userId='me',q=query).execute()
          messageids = [ ]
          if 'messages' in result:
              messageids.extend(result['messages'])
          while 'nextPageToken' in result:
                page_token = result['nextPageToken']
                result = self.gmailer.users().messages().list(userId='me',q=query, pageToken=page_token).execute()
                if 'messages' in result:
                    messageids.extend(result['messages'])
          return messageids;


    def search_messages(self, query):
          messages = [];
          messageids = self.search_messageids(query);
          for messageid in messageids:
              messages.append(
                 self.get_message(messageid)
              );
          return messages;



    # Adds the attachment with the given filename to the given message
    def add_attachment(self, message, filename):
        content_type, encoding = guess_mime_type(filename)
        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'
        main_type, sub_type = content_type.split('/', 1)
        if main_type == 'text':
            fp = open(filename, 'rb')
            msg = MIMEText(fp.read().decode(), _subtype=sub_type)
            fp.close()
        elif main_type == 'image':
            fp = open(filename, 'rb')
            msg = MIMEImage(fp.read(), _subtype=sub_type)
            fp.close()
        elif main_type == 'audio':
            fp = open(filename, 'rb')
            msg = MIMEAudio(fp.read(), _subtype=sub_type)
            fp.close()
        else:
            fp = open(filename, 'rb')
            msg = MIMEBase(main_type, sub_type)
            msg.set_payload(fp.read())
            fp.close()
        filename = os.path.basename(filename)
        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        message.attach(msg)


    def build_message(self, args):

        origin      = args['from'];
        destination = args['to'];
        subject     = args['subject'];
        body        = args['body'];

        attachments = None;
        if 'attachments' in args:
            attachments = args['attachments'];

        if not attachments: # no attachments given
            message = MIMEText(body)
            message['to'] = destination
            message['from'] = origin
            message['subject'] = subject
        else:
            message = MIMEMultipart()
            message['to'] = destination
            message['from'] = origin
            message['subject'] = subject 
            message.attach(MIMEText(body))
            for filename in attachments:
                add_attachment(message, filename)
        return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}


    def send_message(self, args):
        return self.gmailer.users().messages().send(
          userId="me",
          body=self.build_message(args)
        ).execute()


    def parse_parts(self, args):
         parts   = args['parts'];
         message = args['message'];
         text = "";
         if parts:
            for part in parts:
                filename  = part.get("filename")
                mimeType  = part.get("mimeType")
                body      = part.get("body")
                data      = body.get("data")
                file_size = body.get("size")
                part_headers = part.get("headers")
                if part.get("parts"):
                   return self.parse_parts({
                       'parts'   : part.get("parts"),
                       'message' : args['message']
                   });
                if mimeType == "text/plain":
                    if data:
                        text += base64.urlsafe_b64decode(data).decode()
                elif mimeType == "text/html":
                     pass
         return text;


    def get_message(self, message):
        return self.gmailer.users().messages().get(userId='me', id=message['id'], format='full').execute()


    def parse_message(self, msg):
        result = {};
        payload = msg['payload']
        headers = payload.get("headers")
        parts   = payload.get("parts")
        if headers:
            for header in headers:
                name = header.get("name")
                value = header.get("value")
                if name.lower() == 'from':    result['from']    = value;
                if name.lower() == "to":      result['to']      = value;
                if name.lower() == "subject": result['subject'] = value;
                if name.lower() == "date":    result['date']    = value;
        result['body'] = self.parse_parts({
         'parts'   : parts, 
         'message' : msg, 
        });
        return result;



    def mark_as_read_by_ids(self, ids):
        return self.gmailer.users().messages().batchModify(
          userId='me',
          body={
              'ids': ids,
              'removeLabelIds': ['UNREAD']
          }
        ).execute()



    # Probably have to revert to using IDs to blacklist locally
    # We don't want to mark messages as read
    def auto_reply(self, args):
        import time;
        if not 'naptime' in args:
           args['naptime'] = 60;
        blacklist = [];
        while True:
            if not args: args = {
               'subject' : 'Away',
               'body'    : "Hey dude!  I'm out of the office right now."
            }
            messageids = self.search_messageids("in:inbox label:unread category:personal");
            newmessageids = list(set(messageids) - set(blacklist));
            for messageid in newmessageids:
                message = self.get_message(messageid); 
                m = parse_message(message);
                reply = {
                   'from'    : 'the.dominicator@gmail.com',
                   'to'      : m['from'],
                   'subject' : args['subject'],
                   'body'    : args['body'],
                }
                self.send_message(reply);
                break; # Don't go too fast
            time.sleep(args['naptime']);



    def mark_as_read(self, query):
        messages_to_mark = search_messages(self.gmailer, query)
        return self.gmailer.users().messages().batchModify(
          userId='me',
          body={
              'ids': [ msg['id'] for msg in messages_to_mark ],
              'removeLabelIds': ['UNREAD']
          }
        ).execute()


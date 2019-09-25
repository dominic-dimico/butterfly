
import toolbelt;
from googleapiclient.discovery import build
from oauth2client import file, client, tools
from httplib2 import Http

SCOPES = 'https://www.googleapis.com/auth/calendar'


def correct_sleep():

    return True;


def busy():

    store = file.Storage('/home/dominic/.credentials/token.json')
    creds = store.get()
    if not creds or creds.invalid:
             flow = client.flow_from_clientsecrets('/home/dominic/.credentials/credentials.json', SCOPES)
             creds = tools.run_flow(flow, store)
    service = build('calendar', 'v3', http=creds.authorize(Http()))
    current_time = toolbelt.converters.datedt("now");
    current_time = toolbelt.converters.datestr(current_time);
    page_token = None
    while True:
      events = service.events().list(calendarId='primary', pageToken=page_token).execute()
      for event in events['items']:
        if 'start' in event: 
           if 'dateTime' in event['start']:
              start = event['start']['dateTime'] 
           else: continue;
        else: continue;
        if 'end' in event: 
           if 'dateTime' in event['end']:
              end = event['end']['dateTime']
           else: continue;
        else: continue;
        if current_time > start and current_time < end:
           return True;
      page_token = events.get('nextPageToken')
      if not page_token:
        break
    return False;



def schedule_client(when,duration,service,email):

     where = "2790 Saint Johns Ave Apt A1, Jacksonville FL, 32205"

     description = "";
     if service == "workout":
       title = "Workout Session"
       color = 3;
       description += ""


     elif service == "pt":
       title = "Personal Training Session"
       color = 3;
       description += ""


     elif service == "massage":
       title = "Massage Session"
       color = 11;
       description += """
For massage, please be sure to shower beforehand. I have a shower available.  Cash is preferred.  There is a 2.5% fee for debit processing.
"""

     elif service == "hypnosis":
       title = "Sports Hypnosis Session"
       color = 9;
       description += """
For your hypnosis appointment, please be sure you have not taken any psychoactive medications 24 hours prior.
"""

     else:
       color = 3;
       title = service;


     schedule(when, where, duration, title, color, description, email);
     return;



def schedule(when,where,duration,title,color,description,email):


     begin  = toolbelt.converters.datedt(when);
     length = toolbelt.converters.datedt(duration);
     now    = toolbelt.converters.datedt("now");

     delta = length - now;
     end   = begin + delta;

     start_str = toolbelt.converters.datestr(begin);
     end_str   = toolbelt.converters.datestr(end);

     store = file.Storage('/home/dominic/.credentials/token.json')
     creds = store.get()
     if not creds or creds.invalid:
         flow = client.flow_from_clientsecrets('/home/dominic/.credentials/credentials.json', SCOPES)
         creds = tools.run_flow(flow, store)
     tag = build('calendar', 'v3', http=creds.authorize(Http()))
 

     obj = { 
             "creator": { 
               "self": True,
               "displayName": "Dominic",
               "email": "the.dominicator@gmail.com",
             },
             "organizer": { 
               "self": True,
               "displayName": "Dominic",
               "email": "the.dominicator@gmail.com",
             },
             "summary": title,
             "location": where,
             "attendees": [ 
               {
                 "email": email,
               },
             ],
             "start": {
               "timeZone": "America/New_York",
               "dateTime": start_str,
             },
             "end": {
               "timeZone": "America/New_York",
               "dateTime": end_str,
             },
             "colorId": color,
             "reminders": {
               "overrides": [
                 { "minutes": 75,   "method": "email", },
                 { "minutes": 240,  "method": "email", },
                 { "minutes": 600,  "method": "email", },
                 { "minutes": 1440, "method": "email", },
                 { "minutes": 4320, "method": "email", },
               ],
               "useDefault": False,
             },
             "description": description,
           }


     if email == None: 
        obj["attendees"] = [];

     sendnotice = True;
     if begin < now:
        obj["reminders"] = [];
        sendnotice = False;

     schedule_req = tag.events().insert(calendarId='primary', body=obj,sendNotifications=sendnotice);
     if schedule_req:
        result = schedule_req.execute();

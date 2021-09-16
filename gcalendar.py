import toolbelt;
import smartlog;
from googleapiclient.discovery import build
from oauth2client import file, client, tools
from httplib2 import Http

SCOPES = 'https://www.googleapis.com/auth/calendar'


# Calendar object has "notes"< which could be used to store who the event is for
# Could store calendar event id in database, then use it to fix the session
class GoogleCalendarAgent():

    log = smartlog.Smartlog();


    def __init__(self):
        self.authenticate();


    def authenticate(self):
        self.store = file.Storage('/home/dominic/.credentials/gcalendar/token.json')
        self.creds = self.store.get()
        if not self.creds or self.creds.invalid:
           self.flow = client.flow_from_clientsecrets('/home/dominic/.credentials/gcalendar/credentials.json', SCOPES)
           self.creds = tools.run_flow(self.flow, self.store)
        self.calendar = build('calendar', 'v3', http=self.creds.authorize(Http()))


    def is_busy(self):
        nowqd = toolbelt.quickdate.QuickDate("now");
        now = nowqd.dt
        page_token = None
        while True:
          events = self.calendar.events().list(calendarId='primary', pageToken=page_token).execute()
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
            if now > start and now < end:
               return True;
          page_token = events.get('nextPageToken')
          if not page_token:
            break
        return False;


    def get_event(self, args=None):
        eventid = args['eventid'];
        req =  self.calendar.events().get(calendarId='primary', eventId=eventid)
        try: 
              return req.execute();
        except Exception as e:
              import code;
              code.interact(local=locals());


    def update_event(self, args=None):
        ev   = self.get_event(args);
        args = prepare_client_event(args);
        req = self.calendar.events().insert(calendarId='primary', body=obj);
        try: 
              return req.execute();
        except Exception as e:
              import code;
              code.interact(local=locals());


    def list_events(self, args=None):
        if not args: args = {
           'min' : 'one week ago',
           'max' : 'one week from now',
        }
        mint = toolbelt.quickdate.QuickDate(args['min']);
        maxt = toolbelt.quickdate.QuickDate(args['max']);
        page_token = None;
        while True:
            events = self.calendar.events().list(
              calendarId='primary', 
              maxResults=20, 
              pageToken=page_token,
              timeMin=mint.iso,
              timeMax=maxt.iso,
              orderBy="startTime",
              singleEvents=True,
            ).execute()
            evs = [];
            for item in events['items']:
                if 'summary' in item: summary = item['summary'];
                else: summary = '';
                if summary == "Rest":
                   continue;
                if 'start' in item and 'dateTime' in item['start']: 
                   start = item['start']['dateTime'];
                else: 
                   start = '';
                if 'end' in item and 'dateTime' in item['end']: 
                   end = item['end']['dateTime'];
                else: 
                   end = '';
                evs.append({
                  'title' : summary,
                  'start' : start,
                  'end'   : end,
                })
            keys = ['title', 'start', 'end']
            self.log.tabulate(keys, evs, {
               'colwidth': 21,
               'colspace': 2,
            });
            page_token = events.get('nextPageToken')
            if not page_token: break
            input();
        return args;


    # args:
    #   - who
    #   - service
    #   - duration (quick) or end   (date)
    #   - when     (quick) or start (date)
    #
    # optional:
    #   - where
    def prepare_client_event(self,args):

         service  = args['service'];

         if not 'where' in args:
            args['where'] = "1826 Bayard Pl, Apt 12, Jacksonville, FL 32205"

         description = "";
         if service == "workout":
           title = "Workout Session"
           color = 10;
           description += ""

         elif service == "training":
           title = "Personal Training Session"
           color = 10;
           description += ""

         elif service == "massage":
           title = "Massage Session"
           color = 11;
           description += "For massage, please be sure to shower beforehand. I have a shower available.  Cash is preferred."

         elif service == "hypnosis":
           title = "Hypnosis Session"
           color = 9;
           description += ""

         else:
           color = 5;
           title = service;

         if 'who' in args and args['who']:
            title += " - %s" % args['who'];

         postdescription = "\n";

         if 'email' in args and args['email']:
            description     += "\nE-mail: <%s>" % args['email'];
            postdescription += "\nE-mail: <the.dominicator@gmail.com>"

         if 'phone' in args and args['phone']:
            description     += "\nPhone: (%s)"  % args['phone'];
            postdescription += "\nPhone: (%s)"  % "904-748-9785";

         if 'skype' in args and args['skype']:
            description     += "\nSkype: %s"  % args['skype'];
            postdescription += "\nSkype: %s"  % "live:the.dominicator";

         args['title'] = title;
         args['color'] = color;
         args['description'] = description+postdescription;

         return self.prepare_event(args);




    def prepare_event(self, args): 

         when     = args['when'];
         where    = args['where'];
         email    = args['email'];
         title    = args['title'];
         color    = args['color'];
         description = args['description'];
         
         if 'start' in args:
             start = args['start'];
             start = toolbelt.quickdate.QuickDate(start);
         elif 'when' in args:
             when = args['when'];
             start = toolbelt.quickdate.QuickDate(when);

         if 'end' in args:
             end = args['end'];
             end = toolbelt.quickdate.QuickDate(end);
         elif 'duration' in args:
             duration = args['duration'];
             length   = toolbelt.quickdate.QuickDate(duration);
             now      = toolbelt.quickdate.QuickDate("now");
             delta    = length.dt - now.dt;
             end      = toolbelt.quickdate.QuickDate();
             end.setbydt(start.dt + delta);

         # Calendar object
         # JSON representing the calendar event
         obj = { 
                 "summary": title,
                 "location": where,
                 "attendees": [ 
                   {
                     "email": email,
                   },
                 ],
                 "start": {
                   "timeZone": "America/New_York",
                   "dateTime": start.iso,
                 },
                 "end": {
                   "timeZone": "America/New_York",
                   "dateTime": end.iso,
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
         if start.dt < now.dt:
            obj["reminders"] = [];
            sendnotice = False;

         args['obj'] = obj;
         return args;


    def insert_event(self, args):
 
         obj = args['obj'];
         schedule_req = self.calendar.events().insert(calendarId='primary', body=obj);

         if schedule_req:
            try:
              result = schedule_req.execute();
            except Exception as e:
              import traceback;
              traceback.print_exc();
              import code;
              code.interact(local=locals());

         return result['id'];


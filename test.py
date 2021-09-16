#import gcalendar;
#gc = gcalendar.GoogleCalendarAgent();

#id = gc.schedule_client({
# 'who'      : "Dominic",
# 'when'     : "1 hour", 
# 'duration' : "1 hour", 
# 'service'  : "massage", 
# 'email'    : None
#});
#gc.list_events();

#import skype;
#s = skype.SkypeAgent();
#s.list_contacts();
#s.print_messages({
#  'id' : 'live:tomas.leoric'
#});
#s.list_contacts();
#s.send_message({
#  'id' : 'live:tomas.leoric',
#  'msg' : 'Good boy... bow down to my superior will',
#})

import gmail;
g = gmail.GMailAgent();

msgs = g.search_messages("is:unread in:inbox category:personal");
g.parse_message(msgs[0]);
import code
code.interact(local=locals());


#g.send_message({
# 'from'    : 'the.dominicator@gmail.com',
# 'to'      : 'dominic.dimico@gmail.com',
# 'subject' : 'Sup?',
# 'body'    : 'Test'
#});

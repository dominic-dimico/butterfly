from skpy import Skype, SkypeTypingEvent
from getpass import getpass
import os;
import smartlog;
import configparser


class SkypeAgent():

  log = smartlog.Smartlog()


  def __init__(self):
    configs = {};
    configs = configparser.ConfigParser()
    configs.read(os.path.expanduser('~')+'/.config/butterfly/skype.cfg')
    config = configs['main']
    username = config['username']
    password = config['password']
    self.sk = Skype(username, password);


  def login(self):
    self.sk = None;
    while not self.sk:
        x = self.log.gather({
            'keys'   : ['login'],
            'method' : 'linear',
            'data'   : { 
              'login' : 'the.dominicator@gmail.com',
            },
            'overwrite' : True,
        });
        self.sk = Skype(x['data']['login'], getpass());


  def messages_since(self, when='yesterday'):
      msgs = [];
      from toolbelt.quickdate import quickdate
      for c in self.sk.contacts:
           try:
             ch  = c.chat.__dict__['raw'];
             lmt = ch['lastMessage']['originalarrivaltime'];
             if lmt > quickdate(when, 'iso'):
                msgs += [ch['lastMessage']];
           except Exception as e: 
             print(e);
             if e.message == 'originalarrivaltime':
                print(ch['lastMessage']);
      return msgs;


  def print_messages(self, args):
      if not 'id'  in args: return;
      ch = self.sk.contacts[args['id']].chat
      if not ch: return;
      msgs = ch.getMsgs();
      import code;
      code.interact(local=locals());


  def send_message(self, args):
      if not 'msg' in args: return;
      if not 'id'  in args: return;
      ch = None;
      for c in self.sk.contacts:
          if c.id == args['id']:
             ch = c.chat;
      if not ch:
         ch = self.sk.chats.create(args['id']);
      ch.sendMsg(args['msg'])
      if 'file' in args:
         ch.sendFile(open(args['file'], "rb"), args['file']);


  def print_contacts(self):
      import pprint
      d = {}
      for c in self.sk.contacts:
          #self.log.log(c);
          name = ""
          if c.name:
             if c.name.first: name += c.name.first + " ";
             if c.name.last:  name += c.name.last;
          d[c.id] = c;
      self.log.logdata({'data': d});
      return d;


  def auto_reply(self, args={
      'msg' : "What's up, dude?  I'm away right now..."
  }):
      if 'msg' not in args: return;
      msg = args['msg'];
      blacklist = [];
      while True:
         evs = sk.getEvents();
         if evs:
            for ev in evs:
                if isinstance(ev, SkypeTypingEvent):
                   if ev.userId not in blacklist:
                      ch = sk.chats[ev.chatId];
                      ch.sendMsg(msg);
                blacklist.append(ev.userId); 

<<<<<<< HEAD
##!/usr/bin/python
=======
#!/usr/bin/python

# Usage example:
# python comments.py --videoid='<video_id>' --text='<text>'

>>>>>>> 98f41506cbcd03a8dfe9c2c5775a3905a0fa492f

import httplib
import random
import httplib2
import os
import code
import MySQLdb.cursors

from sys import argv, stdin, stdout

import google.oauth2.credentials
import google_auth_oauthlib.flow
from apiclient.discovery import build_from_document
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow


CLIENT_SECRETS_FILE = "config/client_secret.json"
MISSING_CLIENT_SECRETS_MESSAGE = ""
YOUTUBE_READ_WRITE_SSL_SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, httplib.NotConnected,
  httplib.IncompleteRead,    httplib.ImproperConnectionState,
  httplib.CannotSendRequest, httplib.CannotSendHeader,
  httplib.ResponseNotReady,  httplib.BadStatusLine)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
VALID_PRIVACY_STATUSES = ('public', 'private', 'unlisted')



# Authorize the request and store authorization credentials.
def get_authenticated_service():
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_READ_WRITE_SSL_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)
  storage = Storage("config/%s-oauth2.json" % argv[0])
  credentials = storage.get()
  with open("config/youtube-v3-discoverydocument.json", "r") as f:
    doc = f.read()
    return build_from_document(doc, http=credentials.authorize(httplib2.Http()))



# Call the API's commentThreads.list method to list the existing comment threads.
def get_comment_threads(youtube, video_id):
  results = youtube.commentThreads().list(
    part="snippet",
    videoId=video_id,
    maxResults=100,
    textFormat="plainText"
  ).execute()

  for item in results["items"]:
    comment = item["snippet"]["topLevelComment"]
    when = comment["snippet"]["publishedAt"]
    author = comment["snippet"]["authorDisplayName"]
    text = comment["snippet"]["textDisplay"]
    print "Comment published %s by %s:\n  %s\n" % (when, author, text)

  return results["items"]




# Call the API's comments.list method to list the existing comment replies.
def get_comments(youtube, parent_id):
  results = youtube.comments().list(
    part="snippet",
    parentId=parent_id,
    textFormat="plainText"
  ).execute()

  for item in results["items"]:
    author = item["snippet"]["authorDisplayName"]
    text   = item["snippet"]["textDisplay"]
    print "Comment by %s: %s" % (author, text)

  return results["items"]



# Call the API's comments.insert method to reply to a comment.
def insert_comment(youtube, parent_id, text):
  insert_result = youtube.comments().insert(
    part="snippet",
    body=dict(
      snippet=dict(
        parentId=parent_id,
        textOriginal=text
      )
    )
  ).execute()
  author = insert_result["snippet"]["authorDisplayName"]
  text = insert_result["snippet"]["textDisplay"]
  print "Replied to a comment for %s: %s" % (author, text)



# Call the API's comments.update method to update an existing comment.
def update_comment(youtube, comment):
  comment["snippet"]["textOriginal"] = 'updated'
  update_result = youtube.comments().update(
    part="snippet",
    body=comment
  ).execute()
  author = update_result["snippet"]["authorDisplayName"]
  text = update_result["snippet"]["textDisplay"]
  print "Updated comment for %s: %s" % (author, text)





# Call the API's comments.markAsSpam method to mark an existing comment as spam.
def mark_as_spam(youtube, comment):
  youtube.comments().markAsSpam(
    id=comment["id"]
  ).execute()
  print "%s marked as spam succesfully" % (comment["id"])




# Call the API's comments.delete method to delete an existing comment.
def delete_comment(youtube, comment):
  youtube.comments().delete(
    id=comment["id"]
  ).execute()
  print "%s deleted succesfully" % (comment["id"])




# Call the API's commentThreads.list method to list the existing comment threads.
def get_last_comments(youtube, number):
  results = youtube.commentThreads().list(
    part="snippet",
    #videoId=video_id,
    maxResults=int(number),
    order="time",
    textFormat="plainText",
    allThreadsRelatedToChannelId="UC43s0LhDWNPxXkQwp_mLO7w"
  ).execute()
  print
  for item in results["items"]:
    comment = item["snippet"]["topLevelComment"]
    videoid = item["snippet"]["videoId"]
    vid = get_video(youtube, videoid);
    title = vid["snippet"]["title"]
    when = comment["snippet"]["publishedAt"]
    author = comment["snippet"]["authorDisplayName"]
    text = comment["snippet"]["textDisplay"]
    print u"{} ({}):\n{:<24}  {}\n".format(when, title, author[:25], text)
  return results["items"]



def get_video(youtube, video_id):
  results = youtube.videos().list(
    part="snippet",
    id=video_id,
  ).execute()
  return results["items"][0];



if __name__ == "__main__":


  youtube = get_authenticated_service()
  #code.interact(local=locals());

  while True:

    if len(argv) < 2:
      stdout.write("soc> ")
      cmd = stdin.readline().split();
    else: cmd = argv[1:]
  
    if len(cmd) < 1:
       stdout.write("Require argument!");

    elif cmd[0] == "comments":
         if len(cmd) < 2:
            stdout.write("number>  ")
            number = stdin.readline().rstrip('\n')
         else: number = cmd[1];
         get_last_comments(youtube, number); 

    argv=[];


#      try:
#        video_comment_threads = get_all_comment_threads(youtube, args.videoid)
#        #parent_id = video_comment_threads[0]["id"]
#      except HttpError, e:
#        print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)


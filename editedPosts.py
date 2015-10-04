# Name: editedPosts (/u/editedPosts)
# Author: Saroekin (/u/Saroekin)
# Version: Python 2.7.6

#Files or importations that are used elsewhere in program.
import os
import praw
import time
import traceback
import requests
import sqlite3

print ("\n\nOpening database . . . \n\n")
#Variables for sqlite3.
sqliteFile = "editedPosts.sqlite" #Name of the sqlite database file.
tableName_1 = "commentPosts" #Name of the table to be created.
tableName_2 = "submissionPosts" #Name of the table to be created.
idColumn = "ID" #Name of the column.
fieldType = "TEXT" #Column data type.

#SQL database setup/ignition.
conn = sqlite3.connect("sqliteFile")
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS {tn} ({idf} {ft})'\
        .format(tn=tableName_1, idf=idColumn, ft=fieldType))
c.execute('CREATE TABLE IF NOT EXISTS {tn} ({idf} {ft})'\
        .format(tn=tableName_2, idf=idColumn, ft=fieldType))
conn.commit()

#User"s username and password.
Username = <Username>
Password = <Password>

#What reddit sees from the bot's requests.
user_agent = <User Agent>
r = praw.Reddit(user_agent = user_agent)
print("\n\nLogging in . . . \n\n")
r.login(Username, Password)

#Various variables.
editedContentLink = "http://www.reddit.com/r/mod/about/edited/"
subredditPostTo = r.get_subreddit("edited")
userName = "editedPosts"
privateMessageLink = "http://www.reddit.com/message/compose/?to=Saroekin&subject=/u/editedPosts."
wikiPage = "http://www.reddit.com/r/Saroekin_redditBots/wiki/-/u/editedPosts"
sourceCode = "http://github.com/Saroekin/editedPosts"

#Templates for messages and comments (and variables).
Title_For_Submissions_Template = """
Subreddit = /r/%s | ID = %s
""".format()

titleForSubmissions = Title_For_Submissions_Template

#A definition pertaining to accepting moderating invites.
def modInvites():
    for message in r.get_unread():
        messageSubject = message.subject
        if messageSubject in ["username mention", "comment reply"] and type(message) == praw.objects.Comment:
            message.mark_as_read()
            continue
        if "invitation to moderate" in messageSubject:
            subredditNameRetrieval = messageSubject.split()
            try: 
                subredditName = str(subredditNameRetrieval[3])
                subredditName = subredditName.replace("/r/", "")
            except IndexError:
                message.mark_as_read()
                continue
            try:
                subreddit = r.get_subreddit(subredditName)
                subreddit.accept_moderator_invite()
            except praw.errors.InvalidInvite:
                message.mark_as_read()
                continue
            subreddit = r.get_subreddit(subredditName)
            subreddit.accept_moderator_invite()
            message.mark_as_read()

def retrieveEditedPosts():
    edited = r.get_content(editedContentLink, limit=100)
    for post in edited:
        if type(post) == praw.objects.Comment:
            postCommentID = post.id
            c.execute('SELECT * FROM {tn} WHERE {idf}=?'.format(tn=tableName_1, idf=idColumn), [postCommentID])
            if c.fetchone():
                continue
            else:
                postSubreddit = post.subreddit
                postPermalink = post.permalink
                submission = subredditPostTo.submit((titleForSubmissions % (postSubreddit, postCommentID)), url=postPermalink)
                c.execute("INSERT INTO {tn} ({idf}) VALUES(?)".format(tn=tableName_1, idf=idColumn), [postCommentID])
                conn.commit()
                submission.set_flair(flair_text="Comment")
        else:
            postSubmissionID = post.id
            c.execute('SELECT * FROM {tn} WHERE {idf}=?'.format(tn=tableName_2, idf=idColumn), [postSubmissionID])
            if c.fetchone():
                continue
            else:
                postSubreddit = post.subreddit
                postPermalink = post.permalink
                submission = subredditPostTo.submit((titleForSubmissions % (postSubreddit, postSubmissionID)), url=postPermalink)
                c.execute("INSERT INTO {tn} ({idf}) VALUES(?)".format(tn=tableName_2, idf=idColumn), [postSubmissionID])
                conn.commit()
                submission.set_flair(flair_text="Submission")

#Describes the running process of the bot.
print("\n\nRunning . . . \n\n")            
while True:
    try:
        modInvites()
        retrieveEditedPosts()
    except Exception as e:
        traceback.print_exc()
        if e.response.status_code == 503:
            time.sleep(10)
        else:
            time.sleep(5)

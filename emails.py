import ssl, smtplib
from random import choice
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
port = 587
smtp_server = "smtp.office365.com"
sender_email = "schedulegenie@outlook.com"
password = "SchedGen"

msg=MIMEMultipart()
msg["From"]=sender_email

quotes=['“Things may come to those who wait, but only the things left by those who hustle.” Abraham Lincoln',
        '“A year from now you may wish you had started today.” Karen Lamb',
        '“Don’t wait. The time will never be just right.” Napoleon Hill',
        '“Procrastination is opportunity’s natural assassin.” Victor Kiam',
        '“It is not because things are difficult that we do not dare, it is because we do not dare that they are difficult.” Seneca',
        '“You may delay, but time will not, and lost time is never found again.” Benjamin Franklin',
        '“Productivity is never an accident, it’s the result of a commitment to excellence, intelligent planning & focused effort.” – Paul Meyer',
        '“What you do today can improve all of your tomorrows.” – Ralph Marston',
        '“Good things happen when you set your priorities straight” – Scott Caan',
        '“Be the person who decided to go for it!”',
        '“Be stronger than your excuses.” – Jeremy Chin',
        '“When you’re out there partying, horsing around, someone out there at the same time is working hard. Someone is getting smarter and someone is winning. Remember that.” – Arnold Schwarzenegger',
        '“Do something instead of killing time because time is killing you.” – Paulo Coelho',
        '“Success is the sum of small efforts, repeated day in and day out.” – Maya Angelou',
        '“If it doesn’t challenge you, it doesn’t change you.” – Fred Devito',
        '“You will never always be motivated, so you must learn to be disciplined.”',
        '“When you feel like quitting, think about why you started.”',
        '“Done is better than perfect.”',
        '“Believe you can and you’re halfway there.” – Theodore Roosevelt',
        '“Strong people look a challenge in the eye and give it a wink.” – Gina Carey',
        '“Great things never came from comfort zones.”',
        '“If at first you don’t succeed, try, try again.” – Thomas H. Palmer',
        '“Obstacles are those frightful things you see when you take your eyes off your goal.” – Henry Ford.',
        '“Success is a journey, not a destination.” – Ben Sweetland',
        '“A DREAM written down with a date becomes a GOAL. A goal broken down into steps becomes a PLAN. A plan backed by ACTION becomes REALITY.” – Greg Reid',
        '“It does not matter how slowly you go, so long as you do not stop.” – Confucius',
        '“A river cuts through rock, not because of its power, but because of its persistence.” – James N. Watkins',
        '"Continuous improvement is better than delayed perfection." - Mark Twain']

def reminder(activity, user_email, username, deadline):
    string="Hey "+username+"!\n\nYou have a pending item on your to do list that should be done by "+deadline+":\n\t"+activity+"\n\nIf you've already done it, update your to do list here: http://127.0.0.1:5000/mytodo\n\n\n"+"If you haven't, then here's a quote to motivate you:\n"+choice(quotes)
    msg["To"]=user_email
    msg["Subject"]="Pending Item on Your To Do List: "+activity
    msg.attach(MIMEText(string))
    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()  
        server.starttls(context=context)
        server.ehlo()  
        server.login(sender_email, password)
        server.sendmail(sender_email, user_email, msg.as_string())

def misseddeadline(activity, user_email, username, deadline):
    string="Hey "+username+"!\n\nYou missed the deadline for the task:\n\t"+activity+"\n\nThis was supposed to be done by "+deadline+". If you've already done it, update your to do list here: http://127.0.0.1:5000/mytodo\n\n\n"+"If you haven't, then it's not too late to catch up. Here's a quote to motivate you:\n"+choice(quotes)
    msg["To"]=user_email
    msg["Subject"]="Missed Deadline: "+activity
    msg.attach(MIMEText(string))
    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()  
        server.starttls(context=context)
        server.ehlo()  
        server.login(sender_email, password)
        server.sendmail(sender_email, user_email, msg.as_string())

def verification(email,code):
    string="To reset your password, enter the following code on the website.\n"
    msg["To"]=email
    msg["Subject"]="Verification"
    msg.attach(MIMEText(string))
    msg.attach(MIMEText(code))
    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()  
        server.starttls(context=context)
        server.ehlo()  
        server.login(sender_email, password)
        server.sendmail(sender_email, email, msg.as_string())
        return code
    #####

def resetpassword(email,):
    string="To reset your password, click on the following link.\n"
    link=f"http://127.0.0.1:5000/resetpassword/{email}"
    msg["To"]=email
    msg["Subject"]="Reset Password"
    msg.attach(MIMEText(string))
    msg.attach(MIMEText(link))
    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()  
        server.starttls(context=context)
        server.ehlo()  
        server.login(sender_email, password)
        server.sendmail(sender_email, email, msg.as_string())
    
#print(resetpassword("mohi.kunwar05@gmail.com",1))
#print(resetpassword("swetha.murali17@gmail.com",2))
#print(resetpassword("sindhura.valluru4002@gmail.com",3))


















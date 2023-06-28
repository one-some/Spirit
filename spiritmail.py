import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def sendEmail(message, recipient):
    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)

    # start TLS for security
    s.starttls()
    # llrhscgwxbsazwxt

    # Authentication
    s.login("noreply.spiritfbla@gmail.com", "llrhscgwxbsazwxt") # vtozamnwrhgfdzot

    # message to be sent

    # sending the mail
    s.sendmail("noreply.spiritfbla@gmail.com", recipient, message)

    # terminating the session
    s.quit()



def sendPassword(recipient, username, password):
    message_cont = \
        f'''Your administrator has registered you with Spirit.

Your username is {username} and your password is {password}.

Welcome to Spirit!'''

    message = MIMEMultipart()

    message["From"] = "noreply.spiritfbla@gmail.com"
    message["To"] = recipient
    message["Subject"] = "Spirit - Your new account password."

    message.attach(MIMEText(message_cont, 'plain'))

    message = message.as_string()

    sendEmail(message=message, recipient=recipient)


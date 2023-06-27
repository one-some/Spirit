import smtplib

# creates SMTP session
s = smtplib.SMTP('smtp.gmail.com', 587)

# start TLS for security
s.starttls()
# llrhscgwxbsazwxt

# Authentication
s.login("noreply.spiritfbla@gmail.com", "llrhscgwxbsazwxt") # vtozamnwrhgfdzot

# message to be sent
message = "Message_you_need_to_send"

# sending the mail
s.sendmail("noreply.spiritfbla@gmail.com", "wasiuddin2007@gmail.com", message)

# terminating the session
s.quit()

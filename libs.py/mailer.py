import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
import os

def mail(smtp_addr, smtp_port, user, pwd, to, subject, text, 
		 attach=None):
   msg = MIMEMultipart()

   msg['From'] = user
   msg['To'] = to
   msg['Subject'] = subject

   msg.attach(MIMEText(text))

   if attach != None:
      part = MIMEBase('application', 'octet-stream')
      part.set_payload(open(attach, 'rb').read())
      Encoders.encode_base64(part)
      part.add_header('Content-Disposition',
              'attachment; filename="%s"' % os.path.basename(attach))
      msg.attach(part)

   mailServer = smtplib.SMTP(smtp_addr, smtp_port)
   mailServer.ehlo()
   if pwd:
       mailServer.starttls()
       mailServer.ehlo()
       mailServer.login(user, pwd)

   mailServer.sendmail(user, to, msg.as_string())
   # Should be mailServer.quit(), but that crashes...
   mailServer.close()


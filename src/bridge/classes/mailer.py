# vim: tabstop=4 shiftwidth=4 softtabstop=4
import smtplib

from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes


############
#Send a simple plain text email
############
#import mailer

#message = mailer.Message()
#message.From = "me@example.com"
#message.To = "you@example.com"
#message.Subject = "My Subject"
#message.Body = open("letter.txt", "rb").read()

#mailer = mailer.Mailer('mail.example.com')
#mailer.send(message)

############
#Send an email with an attachment
############
#message = mailer.Message()
#message.From = "me@example.com"
#message.To = "you@example.com"
#message.Subject = "My Subject"
#message.Body = open("letter.txt", "rb").read()
#message.attach("picture.jpg")

#mailer = mailer.Mailer('mail.example.com')
#mailer.send(message)

############
#Send an HTML email
############
#message = mailer.Message()
#message.From = "me@example.com"
#message.To = "you@example.com"
#message.Subject = "My Subject"
#message.Body = open("letter.txt", "rb").read()
#message.Html = """This email is in <b>HTML</b>.
#<a href="http://example.com">Here's a link.</a>"""

#mailer = mailer.Mailer('mail.example.com')
#mailer.send(message)


from os import path
class Mailer(object):
    """

    """

    def __init__(self, host="localhost"):
        self.host = host
        self._usr = None
        self._pwd = None
    
    def login(self, usr, pwd):
        self._usr = usr
        self._pwd = pwd

    def send(self, msg):
        server = smtplib.SMTP(self.host)

        if self._usr and self._pwd:
            server.login(self._usr, self._pwd)

        try:
            for m in msg:
                self._send(server, m)
        except TypeError:
            self._send(server, msg)

        server.quit()
    
    def _send(self, server, msg):

        me = msg.From
        you = [x.split() for x in msg.To.split(",")]
        server.sendmail(me, you, msg.as_string())

class Message(object):

    def __init__(self):
        self.attachments = []
        self._to = None
        self.From = None
        self.Subject = None
        self.Body = None
        self.Html = None

    def _get_to(self):
        addrs = self._to
        return ", ".join([x.strip()
                          for x in addrs])
    def _set_to(self, to):
        self._to = to
    
    To = property(_get_to, _set_to,
                  doc="""The recipient(s) of the email.
                  Separate multiple recipients with commas or semicolons""")

    def as_string(self):

        if not self.attachments:
            return self._plaintext()
        else:
            return self._multipart()
    
    def _plaintext(self):

        if not self.Html:
            msg = MIMEText(self.Body)
        else:
            msg  = self._with_html()

        self._set_info(msg)
        return msg.as_string()
            
    def _with_html(self):

        outer = MIMEMultipart('alternative')
        
        part1 = MIMEText(self.Body, 'plain')
        part2 = MIMEText(self.Html, 'html')

        outer.attach(part1)
        outer.attach(part2)
        
        return outer

    def _set_info(self, msg):
        msg['Subject'] = self.Subject
        msg['From'] = self.From
        msg['To'] = self.To

    def _multipart(self):

        msg = MIMEMultipart()
        
        msg.attach(MIMEText(self.Body, 'plain'))

        self._set_info(msg)
        msg.preamble = self.Subject

        for filename in self.attachments:
            self._add_attachment(msg, filename)
        return msg.as_string()

    def _add_attachment(self, outer, filename):
        ctype, encoding = mimetypes.guess_type(filename)
        if ctype is None or encoding is not None:
            # No guess could be made, or the file is encoded (compressed), so
            # use a generic bag-of-bits type.
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        fp = open(filename, 'rb')
        if maintype == 'text':
            # Note: we should handle calculating the charset
            msg = MIMEText(fp.read(), _subtype=subtype)
        elif maintype == 'image':
            msg = MIMEImage(fp.read(), _subtype=subtype)
        elif maintype == 'audio':
            msg = MIMEAudio(fp.read(), _subtype=subtype)
        else:
            msg = MIMEBase(maintype, subtype)
            msg.set_payload(fp.read())
            # Encode the payload using Base64
            encoders.encode_base64(msg)
        fp.close()
        # Set the filename parameter
        msg.add_header('Content-Disposition', 'attachment', filename=path.basename(filename))
        outer.attach(msg)

    def attach(self, filename):
        """
        Attach a file to the email. Specify the name of the file;
        Message will figure out the MIME type and load the file.
        """
        
        self.attachments.append(filename)

if __name__ == '__main__':
    message = Message()
    message.From = "charles.sibbald@fsa.gov.uk"
    message.To = ['andrew.boothroyd@fsa.gov.uk',
                      'Gary.Khaw@fsa.gov.uk',
                      'yasser.nabi@fsa.gov.uk',
                      'Jayachandra.Vangara@fsa.gov.uk',
                      'Mark.Turner@fsa.gov.uk',
                      'charles.sibbald@fsa.gov.uk',
                      'dan.clark@fsa.gov.uk',
                      'Harinder.Rakhra@fsa.gov.uk',
                      'stuart.thorn@fsa.gov.uk',
                      'michael.penrose@fsa.gov.uk',
                      'Faraz.Furniturewala@fsa.gov.uk',
                      'mark.wilson5@fsa.gov.uk',
                      'Vinh.Tuong@fsa.gov.uk',
                      'daniel.watkins@fsa.gov.uk']
    message.Subject = "Scenario Manager Release 2012.8.0.A1"
    #message.attach("test.gif")
    message.Body = """ """
    message.Html = """ """
    mailer = Mailer('sd1appsdl05.fsa.gov.uk')
    mailer.send(message)
    
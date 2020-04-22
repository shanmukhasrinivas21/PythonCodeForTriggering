import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def sendemail(from_address, to, subject, body):
        
    msg = f"""From: {from_address} 
To: {to} 
Subject: {subject}
Content-Type: text/html

<p><span style="font-family: Arial, Helvetica, sans-serif">
{body}
</span></p>
        """
    sent = False
    try:
        with smtplib.SMTP("itxf2aln09.vfc.com") as server:
            server.sendmail(from_address, to, msg)
        print("Email sent Successfully.")
        sent = True
    except smtplib.SMTPException:
        print("Error: unable to send email.")
    return sent

if __name__ == "__main__":
    sendemail("test@vfc.com","veeragandham_krishna@vfc.com", "Hello", "sample")

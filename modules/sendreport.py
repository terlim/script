import sys
import smtplib
from pathlib import Path
import mimetypes
from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase


def send_report(filebody: Path, mail_settings: dict):
    fileToBody = filebody
    msg = MIMEMultipart()
    msg["From"] = mail_settings["mailfrom"]
    msg["To"] = mail_settings["mailto"]
    msg["Subject"] = f"BackUp report from {mail_settings['company']} for {mail_settings['today']}"

    try:
        with open(filebody, "r") as fh:
            emailText = fh.read()
    except IOError as err:
        logging.getLogger("app.sendReport").error(err)
        sys.exit(1)
    msg.attach(MIMEText(emailText))
    attachFile = Path("logs.zip")
    FILENAME = attachFile.name
    with open(attachFile, "rb") as f:
        attachFile = MIMEBase('application', "octet-stream")
        attachFile.set_payload(f.read())
        encoders.encode_base64(attachFile)

    attachFile.add_header('content-disposition', 'attachment', filename=FILENAME)
    msg.attach(attachFile)

    server = smtplib.SMTP(mail_settings["smtpserver"], int(mail_settings["smtpport"]))
    server.starttls()
    server.login(mail_settings["mailfrom"], mail_settings["mailpassword"])
    server.sendmail(mail_settings["mailfrom"], mail_settings["mailto"], msg.as_string())

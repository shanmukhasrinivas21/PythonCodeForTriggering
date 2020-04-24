import win32com.client, json, uuid, configparser, queu, os, triggerbot, smtplib, requests, mail
from pathlib import Path
from bs4 import BeautifulSoup
from APIBot import APIBot
from exchangelib import Credentials, Account, Configuration, DELEGATE, FileAttachment
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import logging


def add_to_queue(bot, msg_tobe_moved, inbox):
    # This function collect the data to be added Queue
      # Get data from bot.Json
      # Get data from Mail
    logger = logging.getLogger(__name__)
    bot_name = bot["bot-name"]
    folder_name = bot["folder-name"]
    attachment_loc=bot["attachments_location"]
    sender_email = msg_tobe_moved.sender.email_address
    body = BeautifulSoup(msg_tobe_moved.body)     # BeautifulSoup converts html to text
    inp_str = {"mailbody": body.get_text(), "mailsender": sender_email, "mailsubject":msg_tobe_moved.subject, "mail_receivedtime":msg_tobe_moved.datetime_received.strftime('%m/%d/%Y %H:%M %p')}
    # Attachments need to be stored in specified path
    ''' if(attachment_loc):
        for attachment in msg_tobe_moved.attachments:
            if isinstance(attachment, FileAttachment):
                print(attachment.name)
                local_path=os.path.join(attachment_loc, attachment.name)
                with open(local_path, 'wb') as f:
                    f.write(attachment.content)'''
                
   #The data collected is passed to add_queue_item in queu
    queu.add_queue_item(bot_name, values=inp_str)
    # check message if it read move to respective folder
    msg_tobe_moved.is_read = True
    msg_tobe_moved.save()
    for each_folder in inbox.children:
        if(folder_name.lower() in each_folder.name.lower()):
            msg_tobe_moved.move(each_folder)
    

## Execution Starts here ##


def run():
    try:
        # Get data from config and Json
          # Get Mails from outlook
          # Compare Mail data with Json
        logger = logging.getLogger(__name__)
        logger.info("Execution Started")
        bot_data = {}
        config = configparser.ConfigParser() 
        config.read('config.INI')
        #env = (config.get("Emailconfig", "environment"))
        with open("bot.json") as file:
            bot_data = json.load(file)
        # Initialising a connection with outlook
        logger.info("Checking mails from outlook")
        credentials = Credentials((config.get("cred","username")),(config.get("cred","password")))
        exchange_config = Configuration(server='outlook.office365.com', credentials=credentials)
        account = Account('rpa_gen@vfc.com',  config=exchange_config, autodiscover=False, access_type=DELEGATE)
        inbox = account.inbox
        messages = inbox.all().order_by('-datetime_received')[:5]
        for message in messages:
            if(message.is_read==False):
                for each_bot in bot_data:
                    if (bot_data[each_bot]["active"] == "1"):  
                        triggered = 0
                        bot_subject = (bot_data[each_bot]["subject"]).lower()
                        if(bot_subject):
                            # comparing the bot subjects with inbox mail subjects,
                              # add the data to queue
                              # Trigger the Bot from Queue data
                            if(bot_subject in message.subject.lower()):
                                print(message.subject)
                                # Here collecting the data and adding to queue is executed
                                add_to_queue(
                                    bot_data[each_bot], message, inbox)
                                triggered = 1  # checkpoint
                            else:
                                triggered = 0

                            '''if(triggered == 0):
                            Moving the email to 'others' folder, if it doesn't match with any of the subjects
                            defined in bot.json
                            for each_folder in inbox.children:
                            This mail move is not recorded in database.
                            if("others" in str(each_folder).lower()):
                            message.move(each_folder)'''
        
        triggerbot.trigger()
    except Exception as e:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(e).__name__, e.args)
        mail.sendemail("test@vfc.com","Garimalla_shanmukhasrinivas@vfc.com","Exception",message)
          
if __name__ == "__main__":
    logging.basicConfig(filename = "R:\\testing\\TriggerScript\\EmailScript.log", format="%(asctime)s -  %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p", filemode="w", level="INFO")
    run()

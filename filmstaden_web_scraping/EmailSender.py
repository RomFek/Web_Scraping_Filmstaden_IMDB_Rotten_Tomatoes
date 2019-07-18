from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import smtplib
from Scraper import Scraper
import xml.etree.cElementTree as ET
from pathlib import Path

host = "smtp.gmail.com"
port = 587

class EmailSender():

    def __init__(self, email):
        self._email = email
        self._file_name = 'email_params.xml'

    def set_login_params(self, username, pwd):
        self._username = username
        self._pwd = pwd

    #Get password
    @property
    def pwd(self):
        return self._pwd
    
    #Get username
    @property
    def username(self):
        return self._username
    
    @property
    def file_name(self):
        return self._file_name
    
    @property
    def email(self):
        return self._email
    
    #Compile the email structure
    def compile_email(self, table):
        message_details = {}
        message_details['body'] = str(table)
        message_details['to'] = self.email
        message_details['subject'] = "Scraped data"
        message_details['from'] = 'no_reply@sfscraper.com'
        if self.email != None:
            print("Compiling email with scraped data...")
        return message_details    
    
    #Check if the email paramters are stored locally. 
    def get_stored_email_params(self):
        details = {}
        stored_params_file = Path(self.file_name)
        if stored_params_file.is_file():    
            print("Exists")
            root = ET.parse(self.file_name).getroot()
            #_last_storage_update_date = root.get('storage_date')
            for param in root.iter():
                if param.tag != root.tag:
                    details[param.tag] = param.text
            return details
        else:
            return None
           
    #Store the provided credentials for the sender email
    def store_sender_email_params(self, username, pwd):
        print("Storing the sender account credentials.")
        try:
            root = ET.Element("params")
            #Create a node for each film detail
            ET.SubElement(root, "username").text = str(username)
            ET.SubElement(root, "pwd").text = str(pwd)
    
            #Append the child nodes/params to the root
            tree = ET.ElementTree(root)
            tree.write(self.file_name)
            return True
        except:
            print("[ERROR] An error occurred while storing the sender account credentials.")
            return False    
            
    #Send email with compiled details along with the necessary images
    def send_email(self, details, images):
        print("Preparing to send an email...")
        message_details = details
        toEmail = message_details['to']
        if toEmail != None:
            fromEmail = message_details['from']
            emailBody = message_details['body']
            emailSubject = message_details['subject']
            #run email
            try:
                #set up connection
                email_conn = smtplib.SMTP(host, port)
                email_conn.ehlo() #Say hello to the server
                email_conn.starttls()
                email_conn.login(self.username, self.pwd)
                self.store_sender_email_params(self.username, self.pwd)#If the login is successful, store the login credentials locally. 
                the_msg = MIMEMultipart("alternative")
                the_msg['Subject'] = emailSubject
                the_msg['From'] = fromEmail
                the_msg['To'] = toEmail
                plain_text_email = MIMEText(emailBody, 'plain') #The actual body of the email (plain)
                the_msg.attach(plain_text_email)
                html_email = MIMEText(emailBody, 'html') #The actual body of the email (html)
                the_msg.attach(html_email)
                
                #Attach all of the necessary images
                try:
                    for image in images:
                        fp = open('resources/images/{image_name}.png'.format(image_name=image), 'rb')
                        msg_image = MIMEImage(fp.read())
                        fp.close()
                        
                        # Define the image's ID
                        msg_image.add_header('Content-ID', '<{image_name}>'.format(image_name=image))
                        the_msg.attach(msg_image)
                except Exception as e:
                    print("[ERROR] Error occurred while attaching images to the email:")
                    print(e)
                email_conn.sendmail(fromEmail, toEmail, the_msg.as_string()) #Send our html formatted message
                email_conn.quit() #quit connection/log out
                print("Email sent successfully.")
                return True
            except smtplib.SMTPException:
                print("[ERROR] Error sending message. Make sure you enter valid login credentials.")
                return False 

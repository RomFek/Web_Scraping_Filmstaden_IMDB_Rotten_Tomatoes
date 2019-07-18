# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
import regex
from PyInquirer import style_from_dict, Token, prompt
from PyInquirer import Validator, ValidationError
from Scraper import Scraper
from EmailSender import EmailSender


#Email format validator
class EmailValidator(Validator):
    def validate(self, document):
        ok = regex.match("[\w'+-]+(\.[\w'+-]+)*@\w+([-.]\w+)*\.\w{2,24}", document.text)
        if not ok:
            raise ValidationError(
                message='Please enter a valid email address',
                cursor_position=len(document.text))  # Move cursor to end

class LauncherCLI():
    
    #Define styles for the command line interface
    def define_cli_styles(self):
        #Define styles for the CLI
        style = style_from_dict({
            Token.QuestionMark: '#fac731 bold',
            Token.Answer: '#82adf2 bold',
            Token.Instruction: '',  # default
            Token.Separator: '#cc5454',
            Token.Selected: '#0abf5b',  # default
            Token.Pointer: '#ff6c46 bold',
            Token.Question: ''
        })
        return style
    
    #Ask for the city for which the Filmstaden data should be scraped and offer to print the data in the console or have it emailed. 
    def ask_main_details(self, city_list, style):
        questions = [
            {
                'type': 'list',
                'name': 'city',
                'message': 'What is your city?',
                'choices': city_list,
                'filter': lambda val: val.lower()
            },
            {
                'type': 'confirm',
                'name': 'toBePrinted',
                'message': 'Print the scraped data in the console?',
                'default': False
            },
            {
                'type': 'confirm',
                'name': 'toBeEmailed',
                'message': 'Would you like the scraped data to be sent to your email?',
                'default': False
            }
        ]
        #Assign style to elements
        answers = prompt(questions, style=style)
        return answers
    
    #Ask for the destination email address
    def ask_reciever_email_address(self, style):
        questions = [
            {
                'type': 'input',
                'name': 'email',
                'validate': EmailValidator,
                'message': 'Please provide a valid email address where the data should be sent?'
            }
        ]
        answers= prompt(questions, style=style)
        return answers
    
    #Ask for login credentials for the account that will be used to send the scraped data
    def ask_sender_email_details(self, style):
        questions = [
            {
                'type': 'input',
                'name': 'senderEmail',
                'validate': EmailValidator,
                'message': 'What Gmail account should be used to send scraped data?'  
            },
            {
                'type': 'input',
                'name': 'senderPassword',
                'message': 'Enter the password'    
            }   
        ]
        answers= prompt(questions, style=style)
        return answers
    
    def main(self):
        print('Hi, welcome to Filmstaden/IMDb/Rotten Tomatoes data aligner')
        scr = Scraper()#Initialize the scraper
        city_list = scr.get_locale_param_list()#Retrieve the list of cities/locales from the target website
        style = self.define_cli_styles()
        main_details = self.ask_main_details(city_list, style) #Ask for the main details (i.e. city, email results)
        #If the user chose to have the scraped results emailed, then ask to provide the destination email address
        if main_details['toBeEmailed']:
            to_email_address = self.ask_reciever_email_address(style)['email']
            sender = EmailSender(to_email_address)
            stored_login_details = sender.get_stored_email_params()
            #If the local storage does not have login credentials then ask user to provide them
            if stored_login_details == None:
                login_details = self.ask_sender_email_details(style)#The provided login details will be stored upon successful login
                username = login_details['senderEmail']
                pwd = login_details['senderPassword']
                sender.set_login_params(username, pwd)
            #If login credentials available in the local storage then use those credentials
            else:
                username = stored_login_details['username']
                pwd = stored_login_details['pwd']
                sender.set_login_params(username, pwd)
                
        city = main_details['city']
        scr.set_locale(city)
        data = scr.get_data()
    
        #If the results were chosen to be emailed then send those results to the provided address
        if main_details['toBeEmailed']:   
            data_to_send = scr.compile_html_table(data)
            table = data_to_send['table'] #HTML table to send to the user
            images = data_to_send['image_names'] #Images to be attached to the email
            sender.send_email(sender.compile_email(table), images)
        if main_details['toBePrinted']:
            scr.print_data(data)

if __name__ == '__main__':
    cli = LauncherCLI()
    cli.main()



# Web_Scraping_Filmstaden_IMDB_Rotten_Tomatoes
Web scraping tool written in Python using BeautifulSoup and Selenium.

The tool scrapes data from Filmstaden.se about films currently showing in cinemas in Sweden along with the corresponding ratings data that is scraped from IMDb and Rotten Tomatoes.  

## Installation
You will need to install the following packages:

```python
pip install selenium
pip install bs4
pip install PyInquirer
```
To launch the tool, just run LauncherCLI.py
NOTE: For Selenium to run you need to have Chrome webdriver installed on your machine.

## Tool overview
Tomatoes and IMDb, which can help to facilitate faster decision making regarding films that are worth a watch without needing to search those films' ratings one by one on IMDb, Metacritic, Rotten Tomatoes. 
Filmstaden.se data scraped with Selenium to work around gradually loading contents on Ajax-enabled pages and set up locale parameters on the website to allow location-relevant film data to be scraped . 
IMDb and Rotten Tomatoes (RT) data was scraped with BeautifulSoap, which was enough to overcome the need for the no longer available public APIs from those websites. Note: data about some films is not available on RT and therefore no RT ratings will be displayed. Sometimes ratings about certain films are not available yet and therefore no ratings will be shown in that case either. 

The data is scraped and stored in the local storage in XML format. Before the next attempt to perform scraping, the tool checks if the data for the requested locale is available in storage and if it's up-to-date (i.e. not older than 4 hours, but can be changed in the parameter file). If the stored data meets the criteria, the data is taken from the storage and displayed/emailed to the user. Otherwise, the scraping gets initiated and the local storage is updated with the current data. 

The current version of the tool is offered as a CLI-version only, where the interface was written using PyInquirer. In the CLI, you will be asked to choose the city for which the film data should be retrieved. Afterwards, you will be asked whether you would like to print the scraped data in the console. 

![CLI](https://user-images.githubusercontent.com/43314129/61377248-1d867f00-a8a3-11e9-8827-41cafe18aa12.png)

Additionally, in the CLI you will be asked whether you would like the scraped data to be sent to your email. The sent email will include image attachments that denote ratings from Rotten Tomatoes. This is done due to the majority of email clients blocking embedded images, therefore this tool sends images as attachments which are then embedded.

In the emailed table, you will see the name of each film with a direct link to its page on Filmstaden's website, IMDb score, Metascore and Rotten Tomatoes ratings along with their visual representation in the form of icons. 

![EMAIL](https://user-images.githubusercontent.com/43314129/61377267-2b3c0480-a8a3-11e9-9220-54fa0c50c92b.png)

**Note:** you need to have a Gmail account, as the current version of the tool has been tested on and supports only Gmail SMTP. You need to provide a valid account credentials in the tool, in order for the tool to use that account to email scraped data. You will be prompted for valid credentials if in CLI you will request to have the scraped data emailed to you. 

The next version of the tool is planned to have GUI, which will be done using Kivy. 

**The date of the last successfull scraping:** 07.20.2019

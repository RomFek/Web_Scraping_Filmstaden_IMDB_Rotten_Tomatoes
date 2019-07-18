#-*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import xml.etree.cElementTree as ET
import time
import ast
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from builtins import property
from datetime import datetime, timedelta
from prettytable import PrettyTable
from pathlib import Path

class Scraper():
    
    def __init__(self):   
        self._file_name = 'film_list.xml'
        self._filmstaden_url = "https://www.filmstaden.se/biljetter/" #URL of the tickets page on Filmstaden website
        self._rotten_tomatoes_url = "https://www.rottentomatoes.com/"
        self._locale = None
        self._refresh_freq = 0
    
    #Set the number of hours the local storage should be valid for.
    def set_refresh_freq(self, freq):
        self._refresh_freq = freq
    
    @property
    def refres_freq(self):
        return self._refresh_freq
    
    @property
    def locale(self):
        return self._locale
    
    def set_locale(self, locale):
        #Make sure that only the first letter of the provided locale is capitalized
        self._locale = locale.lower().capitalize()
        
    @property
    def file_name(self):
        return self._file_name
    
    @file_name.setter
    def file_name(self, file_name):
        self._file_name = file_name
    
    @property 
    def filmstaden_url(self):
        return self._filmstaden_url
    
    @filmstaden_url.setter
    def filmstaden_url(self, filmstaden_url):
        self._filmstaden_url = filmstaden_url
    
    @property 
    def rt_url(self):
        return self._rotten_tomatoes_url
    
    @rt_url.setter
    def rt_url(self, rt_url):
        self._rotten_tomatoes_url = rt_url
        
    #Check connectivity to Filmstaden website using the provided URL
    def check_cinema_connection(self):
        error_message = "[ERROR] Could not establish connection to Filmstaden with the provided URL."
        success_message = "Connection to Filmstaden established successfully."
        try:
            print("Checking connection to Filmstaden...")    
            requests.get(self.filmstaden_url)
            if requests.get(self.filmstaden_url).status_code == 200:
                print(success_message)
                return True
            else:
                print(error_message)
                return False
        except:
            print(error_message)
            return False

    #Retrieve the list of cities used as a locale parameter by Filmstaden
    def get_locale_param_list(self):
        try:
            requests.get(self.filmstaden_url)
            sf_request = requests.get(self.filmstaden_url)
            sf_soup = BeautifulSoup(sf_request.text, 'html.parser')
            city_list = sf_soup.findAll('div', {'id':'AureliaCityConfiguration'})
            
            cities = city_list[0].get("data-configuration") #Retrieve a string representation of a dictionary that contains a "cities" key and a value that is a list of dictionaries containing city names and alias
            cities_dict = ast.literal_eval(cities) #Convert the string representation of a dictionary to a dictionary
            city_list = []
            for city in cities_dict.get("cities"):
                city_name = city.get('name')
                city_list.append(city_name)
            return city_list
        except:
            print("[ERROR] An error occurred while retrieving the list of cities from the locale drop-down menu")
            return None

    #Get the list of films that are currently showing in Filmstaden cinemas in the specific city.
    def get_films_now_in_cinemas(self):
        try:
            #Prior to that we downloaded geckodriver from google and placed it in "geckodriver" folder under workspace and added the path from inside that folder to envrionment variable "Path" in system settings. (Restart Eclipse after adding variable) 
            #Set the option for invoking Firefox browser headlessly (e.g. use Selenium to collect data without starting the browser)
            print("Initiating the storage update...\nConnecting to: {website}".format(website=self._filmstaden_url))
            options = Options()
            options.headless = True
            #Initialize the driver with the specified "headless" option enabled
            driver = webdriver.Firefox(options=options)
            #Send the GET request to the target URL
            driver.get(self.filmstaden_url)
            print("Preparing to collect data...") 
            #After we send the get request, wait 5 seconds for the page to load and the pop to appear
            time.sleep(5)
            #Close the pop up by send the escape command to the browser
            webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            time.sleep(0.5)
            
            ##### Choose the locale on the website (i.e. required parameter) -> the city for which the data should be shown
            #Click on the city selection button to show the drop down list of cities
            print("Collecting the data about films available in Filmstaden cinemas in {city}...".format(city=self.locale))
            driver.find_element_by_css_selector('div.au-target.drop-down-radio-btn.drop-down-radio-btn--vertical-list').click() 
            time.sleep(0.5)
            #To select the city from the drop down list, find the clickable element 
            driver.find_element_by_xpath("//*[contains(text(), '{city}')]".format(city=self.locale)).find_element_by_xpath('..').click() #Parent element of an element containing the value that corresponds to the name of the chosen local
            time.sleep(0.5)
            webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform() #For the sake of being sure that after changing the locale pop-up window is closed
            #####
            
            #Scroll to the bottom of the page as long as more content is loaded
            SCROLL_PAUSE_TIME = 0.5
            # Get scroll height
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                # Scroll down to the bottom of the page
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                # Wait while the page contents are loading
                time.sleep(SCROLL_PAUSE_TIME)
                # Calculate new scroll height and compare with last scroll height
                new_height = driver.execute_script("return document.body.scrollHeight")
                #If after the last scroll the page height remained the same (i.e. no more content loaded), then break out of the loop
                if new_height == last_height:
                    break
                last_height = new_height
                
            #Find a tag where a film data is
            cinemaFilmList=driver.find_elements_by_class_name("thumbnail-movie-list__title") 
            #Extract film names and film URLs and store them as dictionaries in a list
            film_list = []
            for film in cinemaFilmList:
                film_data = {}
                #Get the URL from the href attribute,  where the tag text is equal to the film name
                film_link = driver.find_element_by_link_text(film.text).get_attribute("href")
                film_data['film_name'] = film.text
                film_data['film_url'] = film_link
                film_data['film_year'] = None
                film_data['imdb_rating'] = None
                film_data['metascore'] = None
                film_data['original_title'] = None
                film_data['rt_tomatometer_score'] = None
                film_data['rt_tomatometer_votes'] = None
                film_data['rt_audience_score'] = None
                film_data['rt_audience_votes'] = None
                film_data['rt_tomatometer_icon'] = None
                film_data['rt_audience_icon'] = None
                
                film_list.append(film_data)
            driver.close()
            print("The film list successfully retrieved")
            return film_list
        except:
            print("[ERROR] An unexpected error occurred while getting the data from the following URL: {website}".format(website=self.filmstaden_url))
            return None
        
    #Get the film url on IMDB
    def get_film_url(self, film_name):
        base_url = "http://www.imdb.com"
        search_url_seg = "/find?s=tt&q="
        url = base_url + search_url_seg + film_name.replace('#', '%23') #Decode the hashtag in the film name if such exists
        imdb_request = requests.get(url)
        
        #Get the requested HTML and feed it to BeautifulSoap
        imdb_soup = BeautifulSoup(imdb_request.text, 'html.parser')
        #Retrieve all "tr" tag elements that have a class "findResult odd" from the hmtl
        imdb_search_results = imdb_soup.findAll('tr', {'class': 'findResult odd'}) 
        
        #In order to retrieve the links, feed the retrieved tr elements to BeautifulSoap and get all "a" tags
        imdb_links_soup = BeautifulSoup(str(imdb_search_results), 'html.parser')
        imdb_search_links = imdb_links_soup.findAll('a')
        
        #Here we rely on the search engine used by IMDB and assume that the first returned search result is the film that we searched for. 
        #We get the link segment for that movie and add it to the base IMDB link to construct the movie specific link that takes us to the movie page
        #Check if the movie is found on IMDb. If not then return a blank
        try:
            target_url = imdb_search_links[0].get("href")
            #print(target_url)
            film_url = base_url + target_url
            return film_url
        except:
            print("[WARN] Failed to retrieve the IMDB URL for {film}".format(film=film_name))
            return None
    
    #Get a film rating from IMDb and original film title if such exists (i.e. if on cinema's website the film's title is in Swedish)
    def get_imdb_data(self, film_name):
        url = self.get_film_url(film_name) #Get the film URL
        if url != None:
            try:
                imdb_request = requests.get(url) #Get the page html
                imdb_soup = BeautifulSoup(imdb_request.text, 'html.parser') #Feed the html to BeautifulSoap
                imdb_data = {}
            
                #Get IMDb rating
                imdb_rating_raw = imdb_soup.findAll('span', {'itemprop':'ratingValue'}) #Get the html element that hold the film rating
                #Check if the film is rated. If not, return None
                if len(imdb_rating_raw) > 0: 
                    imdb_rating = imdb_rating_raw[0].text #Extract the rating
                    imdb_data['imdb_rating'] = imdb_rating
                else:
                    imdb_data['imdb_rating'] = None
                
                #Get the section containing film title and year
                imdb_title_sec = imdb_soup.findAll('div', {'class':'title_wrapper'}) 
                imdb_title_sec_soup = BeautifulSoup(str(imdb_title_sec), 'html.parser') #Feed the html to BeautifulSoap
                
                #Get film year from IMDb
                imdb_film_year = imdb_title_sec_soup.find('span', {'id':'titleYear'}).text.replace('(', '').replace(')', '')
                imdb_data['imdb_film_year'] = imdb_film_year
                
                #If a movie has a Swedish title, then retrieve original title from IMDb, otherwise use the initial film title (Note: Filmstaden film titles sometimes are in Swedish)
                imdb_film_original_title = imdb_title_sec_soup.find('div', {'class':'originalTitle'})
                imdb_film_title = imdb_title_sec_soup.find('h1')
                imdb_film_title.find('span').decompose() #Discard child elements of h1. We need only film title text
                if imdb_film_original_title != None:
                    imdb_name = imdb_film_original_title.text.replace('(original title)','').strip()
                    imdb_data['imdb_name'] = imdb_name
                else:
                    imdb_name = imdb_film_title.text.replace('\xa0', '').strip()
                    imdb_data['imdb_name'] = imdb_name
                return imdb_data
            except:
                return None
        else:
            return None
    
    #Get metascore rating from IMDb
    def get_metascore(self, film_name):
        url = self.get_film_url(film_name) #Get the film URL
        if url != None:
            try:
                imdb_request = requests.get(url) #Get the page html
                imdb_metascore_raw_soup = BeautifulSoup(imdb_request.text, 'html.parser') #Feed the html to BeautifulSoap
                imdb_metascore_rating_raw = imdb_metascore_raw_soup.findAll('div', {'class':'titleReviewBarItem'}) #Get the html element that hold the metascore rating
                imdb_metascore_soup = BeautifulSoup(str(imdb_metascore_rating_raw), 'html.parser') #Feed the html to BeautifulSoap
                imdb_metascore_rating = imdb_metascore_soup.findAll('span', {'class':''})
                if len(imdb_metascore_rating) > 0: 
                    return imdb_metascore_rating[0].text #Extract metascore rating if such exists
                else:
                    return None 
            except:
                return None
        else:
            return None
    
    #Function to be used to replace characters in keywords/film_title to adapt it for search engine on Rotten Tomatoes
    def convert_to_rt_search_key(self, film_title):
        replacement_values = {
            "&":"and",
            " ":"_",
            ":":"",
            "'":"",
            "!":"",
            ",":"",
            ".":"",
            "(":"",
            ")":"",
            "#":"",
            "%":"",
            "-":"_",
            "é":"e"
        }
        for elem in film_title:
            if elem in replacement_values:
                film_title = film_title.replace(elem, replacement_values[elem])
        film_title = film_title.replace("____", "_").replace("___", "_").replace("__", "_") #replace multiple (up to 4) consecutive underscores with a single underscore
        return film_title
    
    #Check if the film release year and film year from IMDb match. 
    #This is a way to check if we are getting the data from the correct url.
    def film_years_match(self, html, film_year):
        #Sometimes the film URL on RT has film year appended to it and sometimes not. 
        #Run a scan of film page with URL without a year, and if the film year from IMDb is the same as the film year on RT film page, then use scores from that page
        #Alternatively, append the year to URL and take a score from there, if such exists. 
        #Get film release date element
        try:
            rt_film_release_element = html.findAll('time')[0]['datetime']
            #Extract year from the scraped film release date
            if rt_film_release_element != None:
                release_year = str(rt_film_release_element)[:4:]
                if release_year == film_year: 
                    #print("Years match")
                    return True
                else:
                    #print("Years DONT match")
                    return False
            else:
                return False   
        except:
            return False
    
    #Get tomatometer and audience score from Rotten Tomatoes for a specific film
    def get_rt_scores(self, film_title, film_year):
        base_url = "https://www.rottentomatoes.com/"
        film_title = self.convert_to_rt_search_key(film_title)
        url_without_year = base_url + 'm/'+film_title
        url_with_year = base_url + 'm/'+film_title + '_' + film_year

        rt_request = requests.get(url_without_year) #Get the Rotten Tomatoes film page html from URL without an appended year
        rt_soup = BeautifulSoup(rt_request.text, 'html.parser')
        
        if rt_request.status_code == 200 and self.film_years_match(rt_soup, film_year):
            #If years from film release years from IMDb and RT match, then the URL is correct and continue scraping data
            pass
        else:
            #If years don't match then use URL with the release year appended to it
            rt_request = requests.get(url_with_year)
            rt_soup = BeautifulSoup(rt_request.text, 'html.parser')   
        rt_score_section = rt_soup.findAll('section', {'class':'mop-ratings-wrap__row js-scoreboard-container'}) #Get scoreboard section
        rt_score_section_soup = BeautifulSoup(str(rt_score_section), 'html.parser')
        rt_scores = rt_score_section_soup.findAll('div', {'class':'mop-ratings-wrap__half'}) #Get sections with tomatometer and audience score as separate elements
        
        scores = {} #Initialize a dictionary to hold RT data
        
        #Get the info about the type of icon used on RT to denote the rating (e.g. rotte, fresh etc.)
        rt_icons_elements = rt_soup.findAll('span', {'class':'mop-ratings-wrap__icon'}) 
        tomatometer_levels = ['certified_fresh', 'rotten', 'fresh'] #List all possible icon types for tomatometer rating
        audience_levels = ['upright', 'spilled'] #List all possible icon types for audience rating
        scores['tomatometer_score_icon'] = None
        scores['audience_score_icon'] = None
        if len(rt_icons_elements) > 0:     
            for rt_icon in rt_icons_elements:
                ls = rt_icon.get("class")
                tom_lev = set(ls) & set(tomatometer_levels) #Items that are present in both list of tomatometer levels and the scraped levels (the result should be one item (icon name) as a film on RT has only one Tomatometer score)
                aud_lev = set(ls) & set(audience_levels) #As above, but for audience score
                
                #If there is no tomatometer score, and if the score value in the dict is None then don't do anything
                if len(tom_lev) == 0:
                    if scores['tomatometer_score_icon'] == None:
                        pass
                else:
                    scores['tomatometer_score_icon'] = list(tom_lev)[0]
                #If there is no audience score, and if the score value in the dict is None then don't do anything
                if len(aud_lev) == 0:
                    if scores['audience_score_icon'] == None: 
                        pass
                else:
                    scores['audience_score_icon'] = list(aud_lev)[0]
     
        #Extract tomatometer score and votes count if those scores exist on Ronnet Tomatoes website
        try:
            rt_tomatometer_score = rt_scores[0].find_all('span', {'class':'mop-ratings-wrap__percentage'})[0].text.replace(" ", "").replace("\n", "") #Tomatometer score
            rt_tomatometer_votes = rt_scores[0].find_all('small', {'class':'mop-ratings-wrap__text--small'})[0].text.replace(" ", "").replace("\n", "") #Votes count
            

            scores['tomatometer_score'] = rt_tomatometer_score
            scores['tomatometer_votes'] = rt_tomatometer_votes
        except:
            #IF there are no scores on Roten Tomatoes website for the processed film
            scores['tomatometer_score'] = None
            scores['tomatometer_votes'] = None
        
        #Extract audience score and votes count from Rotten Tomatoes website
        try:
            rt_audience_score = rt_scores[1].find_all('span', {'class':'mop-ratings-wrap__percentage'})[0].text.replace(" ", "").replace("\n", "") #Audience score
            rt_audience_votes = rt_scores[1].find_all('strong', {'class':'mop-ratings-wrap__text--small'})[0].text.replace(" ", "").replace("\n", "") #Votes count
            scores['audience_score'] = rt_audience_score
            
            #Use ternary operator to determine the first index of the substring. If -1 is returned then start is 0 
            #Otherwise we start at the index where semicolon is with the added 1 to exclude that semicolon
            start_index = 0 if rt_audience_votes.find(":") == -1 else rt_audience_votes.index(":") + 1 
            scores['audience_votes'] = rt_audience_votes[start_index::] #If there is a text before the actual vote count, exclude it.
        except:
            scores['audience_score'] = None
            scores['audience_votes'] = None
            
        return scores
    
    #Generate root for XML file
    def generate_xml_root(self):
        root = ET.Element("films")
        #The date and time when the root node was generated (i.e. the data was last retrieved since the root node is created when data is stored after scraping)
        root.attrib["storage_date"] = str(datetime.now()) 
        root.attrib["locale"] = self.locale
        print("Storing data in XML...\nXML root node generated...")
        return root
    
    #Add film data as a node to the XML
    def add_to_xml(self, xml_root, film_name, imdb_rating, metascore, cinema_film_url, original_title, film_year, rt_tomat_score, rt_tomat_votes, rt_aud_score, rt_aud_votes, rt_tomat_icon, rt_aud_icon):
        try:
            #Create xml segment that will hold film data
            film = ET.SubElement(xml_root, "film")
            #Create a node for each film detail
            ET.SubElement(film, "film_name").text = str(film_name)
            ET.SubElement(film, "imdb_rating").text = str(imdb_rating)
            ET.SubElement(film, "metascore").text = str(metascore)
            ET.SubElement(film, "film_url").text = str(cinema_film_url)
            ET.SubElement(film, "original_title").text = str(original_title)
            ET.SubElement(film, "film_year").text = str(film_year)
            
            ET.SubElement(film, "rt_tomatometer_score").text = str(rt_tomat_score)
            ET.SubElement(film, "rt_tomatometer_votes").text = str(rt_tomat_votes)
            ET.SubElement(film, "rt_audience_score").text = str(rt_aud_score)
            ET.SubElement(film, "rt_audience_votes").text = str(rt_aud_votes)
            ET.SubElement(film, "rt_tomatometer_icon").text = str(rt_tomat_icon)
            ET.SubElement(film, "rt_audience_icon").text = str(rt_aud_icon)

            #Append the film data to the root
            tree = ET.ElementTree(xml_root)
            tree.write(self.file_name)
            return True
        except:
            print("[ERROR] An error occurred while adding data to XML")
            return False    
    
    #Assign the IMDb and Metascore ratings to films currently showing in Filmstaden cinemas. Store the data as XML
    def update_local_storage(self, film_list):
        #generate the root node for our XML. Have to be done outside of the iteration. Nodes for each film will be appended to it
        root = self.generate_xml_root() 
        #Iterate through films retrieved from Filmstaden official website and store data in dicitonaries containing respective film's details
        print("Updating local storage...")
        x = 0 #Initialize the dividend -> Number of added films throughout the iteration.
        progress = 0 #Progress that shows the % of films processed and stored 
        #Iterate through dictionaries stored in our list
        for film in film_list: 
            
            #Update IMDb data
            #film_name and film_url keys already have values specified in the dictionary of the currently processed film
            rating_and_orig_title = self.get_imdb_data(film['film_name'])
            if rating_and_orig_title != None:
                film["imdb_rating"] = rating_and_orig_title['imdb_rating']
                metascore = self.get_metascore(film['film_name'])
                film['metascore'] = metascore
                film['original_title'] = rating_and_orig_title['imdb_name']
                film['film_year'] = rating_and_orig_title['imdb_film_year']
                
                #Update data from Rotten Tomatoes website
                rotten_tomatoes_data = self.get_rt_scores(rating_and_orig_title['imdb_name'], rating_and_orig_title['imdb_film_year'])
                film['rt_tomatometer_score'] = rotten_tomatoes_data['tomatometer_score']
                film['rt_tomatometer_votes'] = rotten_tomatoes_data['tomatometer_votes']
                film['rt_audience_score'] = rotten_tomatoes_data['audience_score']
                film['rt_audience_votes'] = rotten_tomatoes_data['audience_votes']
                film['rt_tomatometer_icon'] = rotten_tomatoes_data['tomatometer_score_icon']
                film['rt_audience_icon'] = rotten_tomatoes_data['audience_score_icon']
            #print(film)
            self.add_to_xml(root, film["film_name"], film["imdb_rating"], film['metascore'], film['film_url'], film['original_title'], film['film_year'], film['rt_tomatometer_score'], film['rt_tomatometer_votes'], film['rt_audience_score'], film['rt_audience_votes'], film['rt_tomatometer_icon'], film['rt_audience_icon']) #Store film data in the xml
            x += 1
            progress = round((x / len(film_list) * 100), 1) #Calculate the update progress
            print(str(progress) + "%")
        print("Locally stored film list updated -> XML with film data scraped from filmstaden.se generated...")
    
    #Get the locale for which the stored data is associated with
    @property
    def stored_data_locale(self):
        try:
            root = ET.parse('film_list.xml').getroot()
            _stored_data_locale = root.get('locale')
            return _stored_data_locale
        except:
            return None
    
    #Check if the requested locale is the same as the one in storage
    def data_for_locale_already_stored(self):
        stored_locale = self.stored_data_locale
        if stored_locale != None:
            if stored_locale == self.locale:
                print("Data for the requested locale is available in the local storage.\nChecking the status of the stored data...")
                return True
            else:
                print("The stored data is outdated or not relevant for the requested locale.")
                return False
            
    @property
    def last_storage_update_date(self):
        try:
            root = ET.parse('film_list.xml').getroot()
            _last_storage_update_date = root.get('storage_date')
            return _last_storage_update_date
        except:
            print("[INFO] Could not retrieve the date of the last update from the locally stored file.")
            return None
        
    #Check the time of the last storage update
    def is_stored_data_up_to_date(self):
        self.set_refresh_freq(4) #Set the refresh frequency for the local storage
        storage_file = Path(self.file_name)
        #Check if the local storage exists
        if storage_file.is_file():
            stored_date = datetime.strptime(self.last_storage_update_date, '%Y-%m-%d %H:%M:%S.%f') #Get the date from storage and convert it to a date format
            #If the stored file has the date of the last update (i.e. file is present) and that date is not more than 2 hours older than current date, then the stored data is up to date
            if stored_date != None and stored_date + timedelta(hours=self.refres_freq) > datetime.now():
                return True
            else: 
                return False
        else:
            return False
    
    #Get data from the local storage.
    def get_local_storage_data(self):
        stored_films_list = []
        tree = ET.parse(self.file_name) #parse an xml file by name
        root = tree.getroot()
        #Retrieve the list of the locally stored films, by iterating through nodes in the XML
        print("Getting the data from the local storage...")
        for film in root:
            stored_film_dict = {} #Re-initialize the dictionary for each film node (i.e. each film record)
            for detail in film.iter():
                if detail.tag != film.tag: #Print child elements of "film" node, without printing the value of the node itself
                    stored_film_dict[str(detail.tag)] = detail.text
                    #if detail.tag = 'filmName':
                        #print(detail.tag + " " + detail.text)
            stored_films_list.append(stored_film_dict)
            #stored_films_list.append(film.text)
        print("The data is ready.")
        return stored_films_list
    
    #Get data about films currently showing in Filmstaden cinemas
    def get_data(self):
        if self.locale != None:
            #If the data in storage is outdated, then perform data scraping, otherwise return data from storage
            if self.data_for_locale_already_stored() and self.is_stored_data_up_to_date():
                print("The stored data is up-to-date.")
                film_list = self.get_local_storage_data()
                return film_list
            else:
                print("The stored data is outdated or does not exist")
                new_film_list = self.get_films_now_in_cinemas()
                self.update_local_storage(new_film_list)
                film_list = self.get_local_storage_data()
                return film_list
        else:
            print("Locale was not specified. The film data from cinemas was not retrieved")
            return None
    
    #Get column headers to be used in the data table
    def get_table_headers(self):
        headers = ['Film Name', 'Original Title', 'IMDb Rating', 'Metascore', 'Tomatometer Score', 'Tomatometer Votes', 'Freshness', 'Audience Score', 'Audience Votes']
        return headers
    
    def print_data(self, film_list):
        if film_list != None:
            t = PrettyTable(self.get_table_headers())
            for film in film_list:
                t.add_row([
                    film['film_name'],
                    film['original_title'],
                    film['imdb_rating'],
                    film['metascore'],
                    film['rt_tomatometer_score'],
                    film['rt_tomatometer_votes'],
                    film['rt_tomatometer_icon'],
                    film['rt_audience_score'],
                    film['rt_audience_votes']
                    ]
                )
            print(t)
            print("* None - denotes ratings that were not retrieved for that specific film")
        else:
            print("No data to print.")


    #Get the HTML ready element for the icon that denotes the ranking on Rotten Tomatoes (both tomatometer and audience score)
    #Most email clients block embedded images. Therefore, we send those images as attachments and then embedding them.
    def get_rt_score_image(self, icon_level):
        #Convert the input image to base64 and return the prepared HTML tag
        if icon_level == 'fresh':
            img_tag = '<img src="cid:fresh" title="Fresh">'
        elif icon_level == 'certified_fresh':
            img_tag = '<img src="cid:certified_fresh" title="Certified Fresh">'
        elif icon_level == 'rotten':
            img_tag = '<img src="cid:rotten" title="Rotten">'
        elif icon_level == 'upright':
            img_tag = '<img src="cid:upright" title="Upright">'
        elif icon_level == 'spilled':
            img_tag = '<img src="cid:spilled" title="Spilled">'
        else:
            img_tag = '<img src="cid:none" title="">'
        return img_tag

       
    #Create html table that can be send to users via email
    def compile_html_table(self, film_data):
        headers = self.get_table_headers() #Get table headers/column names
        column_headers = "<tr><th>{film_name}</th><th>{imdb_rating}</th><th>{metascore}</th><th>{rt_score}</th><th>{audience_score}</th></tr>".format(film_name=headers[0], imdb_rating=headers[2], metascore=headers[3], rt_score=headers[4], audience_score=headers[7])
        row_list = []
        row_list.append(column_headers)#Append HTML table headers to the list
        images = [] #List of images to attach to email
        data = {} #Dict to hold HTML tanle of data and the list of images to be attached to the email
        #Create a HTML row for each film record and append to the list
        for film in film_data:
            row = "<tr><td><a href='{film_url}'>{film_name}</a></td><td>{imdb_rating}</td><td>{metascore}</td><td>{tom_icon}{rt_score}</td><td>{aud_icon}{audience_score}</td></tr>".format(film_name=film['film_name'], imdb_rating=film['imdb_rating'], metascore=film['metascore'], rt_score=film['rt_tomatometer_score'], audience_score=film['rt_audience_score'], film_url=film['film_url'], tom_icon=self.get_rt_score_image(film['rt_tomatometer_icon']), aud_icon=self.get_rt_score_image(film['rt_audience_icon']))
            row_list.append(row)
            images.append(film['rt_tomatometer_icon'])
            images.append(film['rt_audience_icon'])
        rows = "".join(str(row) for row in row_list) #Concatenate all list elements
        #Get contents of our CSS file in "resources/css" folder
        with open('resources/css/main.css', 'r') as f:
            css_style = f.read()
        table = "<html><head><style>{style}</style></head><body><table class='film_table'>{table_content}</table></body></html>".format(style=css_style, table_content=rows) #Insert rows into a table
        data['table'] = table.replace("None", "n/a") #Replace None with N/A in the table to be used in the email
        data['image_names'] = images
        return data
        
'''
storage_file = Path('film_list.xml')
if storage_file.is_file():    
    print("Exists")
else:
    print("Does not exist")
'''
'''
url = 'https://www.rottentomatoes.com/m/yesterday'
request = requests.get(url)
soup = BeautifulSoup(request.text, 'html.parser')
rt_film_release_element = soup.findAll('time')[0]['datetime']
print(rt_film_release_element)  
'''
        
#t = Scraper()
#print(t.get_rt_score_image('fresh'))
#t.set_locale("Borås")
#t.set_locale("Borås")
#print(t.get_data())
#t.print_data(t.get_data())
#print(t.get_imdb_data('Yesterday'))
#t.set_locale("Borlänge")

#print(t.compile_html_table())
#data = t.get_data()
#headers = t.get_table_headers()
'''

#print(t.get_films_now_in_cinemas())
#print(t.get_films_now_in_cinemas())
rint(t.get_rt_scores("Tell it to the bees", "2019"))
#print(t.get_rt_scores("Missing Link", "2019"))

#t.compile_html_table(t.get_data())
#Change the IMDB year scraping to release date (e.g. On the Basis of Sex should be 2019 and not 2018)
#Issue with replacement of - in a astring (e.g. John Wick: Chapter 3 - Parabellum). Add a function that removes consequtive spaces word__word -> word_word
'''
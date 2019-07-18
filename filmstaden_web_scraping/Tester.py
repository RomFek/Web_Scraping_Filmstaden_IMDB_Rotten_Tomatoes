import requests
from bs4 import BeautifulSoup

def get_rt_scores(film_title, film_year):
    base_url = "https://www.rottentomatoes.com/"
    #film_title = convert_to_rt_search_key(film_title)
    url_without_year = base_url + 'm/'+film_title
    url_with_year = base_url + 'm/'+film_title + '_' + film_year

    rt_request = requests.get(url_without_year) #Get the Rotten Tomatoes film page html from URL without an appended year
    rt_soup = BeautifulSoup(rt_request.text, 'html.parser')

    if rt_request.status_code == 200:
        #If years from film release years from IMDb and RT match, then the URL is correct and continue scraping data
        pass
    else:
        #If years don't match then use URL with the release year appended to it
        rt_request = requests.get(url_with_year)
        rt_soup = BeautifulSoup(rt_request.text, 'html.parser')   
    rt_score_section = rt_soup.findAll('section', {'class':'mop-ratings-wrap__row js-scoreboard-container'}) #Get scoreboard section
    rt_score_section_soup = BeautifulSoup(str(rt_score_section), 'html.parser')
    rt_scores = rt_score_section_soup.findAll('div', {'class':'mop-ratings-wrap__half'}) #Get sections with tomatometer and audience score as separate elements
     
    scores = {}
         
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

#print(get_rt_scores("THE_SECRET_LIFE_OF_PETS_2", "2019"))




base_url = "https://www.rottentomatoes.com/"
#film_title = "spider_man_far_from_home"
film_title = "maleficent_mistress_of_evil"

film_year = "2019"
url_without_year = base_url + 'm/'+film_title
url_with_year = base_url + 'm/'+film_title + '_' + film_year

rt_request = requests.get(url_without_year) #Get the Rotten Tomatoes film page html from URL without an appended year
rt_soup = BeautifulSoup(rt_request.text, 'html.parser')
rt_score_section = rt_soup.findAll('section', {'class':'mop-ratings-wrap__row js-scoreboard-container'}) 

rt_icons_soup = BeautifulSoup(str(rt_score_section), 'html.parser')
rt_icons_elements = rt_soup.findAll('span', {'class':'mop-ratings-wrap__icon'}) 
tomatometer_levels = ['certified_fresh', 'rotten', 'fresh']
audience_levels = ['upright', 'spilled']

levels = ['certified_fresh', 'rotten', 'fresh', 'upright', 'spilled']
scores = {}
if len(rt_icons_elements) > 0:
    scores['tomatometer_score_icon'] = None
    scores['audience_score_icon'] = None
    
    for rt_icon in rt_icons_elements:
        ls = rt_icon.get("class")
        tom_lev = set(ls) & set(tomatometer_levels)
        aud_lev = set(ls) & set(audience_levels)
        
       
        if len(tom_lev) == 0:
            if scores['tomatometer_score_icon'] == None:
                pass
        else:
            scores['tomatometer_score_icon'] = list(tom_lev)[0]
        if len(aud_lev) == 0:
            if scores['audience_score_icon'] == None: 
                pass
        else:
            scores['audience_score_icon'] = list(aud_lev)[0]
print(scores)
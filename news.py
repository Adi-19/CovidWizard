import requests
import country_converter as coco
import numpy as np

cc = coco.CountryConverter()
def country2code(country):
    return coco.convert(names=country, to='ISO2')


class Wendor:
    """
        Data Wendor for News
    """
    def __init__(self, api=None):
        self.baseurl = 'https://newsdata.io/api/1/news?apikey='
        if api:
            self.api = api
        else:
            self.api = 'pub_631b7b66088d67ab749d3ffc641e6bb5f60'
        self.category = 'category=health&q=coronavirus%20OR%20covid'
        self.language = '&language=en'

    def get_top_k(self, response, k=3):
        results = np.array(response['results'])
        #print(results)
        clean = []
        for i in range(k):
            url = '#' if results[i]['image_url']==None else results[i]['image_url']
            pub = 'Earlier' if results[i]['pubDate']==None else results[i]['pubDate']
            title = results[i]['title']
            desc = 'None' if results[i]['description']==None else results[i]['description'][:60]+'...'
            link = '#' if results[i]['link']==None else results[i]['link']
            if title == None:
                # Can't do much really
                pass
            else:
                clean.append([url, pub, title, desc, link])

        return clean

    def get_news(self, country, k=5, dummy=False):
        if dummy:
            return [['#', '2021-04-25 05:14:05', 'Coronavirus dummy updates', 
                     'Coronavirus dummy Live Updates: Dummy records x lakh new Covid cases, 2,767 deaths', '#']*5]
        if (country=='Global'):
            url = self.baseurl + self.api + '&' + self.category + self.language
        else:
            url = self.baseurl + self.api + '&country=' + country2code(country) + '&' + self.category + self.language
        request = requests.get(url)
        if ((request.status_code!=200) or (request.json()['totalResults']<k)):
            url = self.baseurl + self.api + '&' + self.category + self.language     # Go Global
            request = requests.get(url)

        response = request.json()

        news = self.get_top_k(response, k)
        return news



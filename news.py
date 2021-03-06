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
            self.api1 = 'pub_645e4b5c7cf5563649ba4ded1aaf8661e0b'
            self.api2 = 'pub_6462a0b64d41ed8a506e7f8e8350325010d'
            self.api3 = 'pub_6474201ff02c6762ebec18a4f7103d8e34f'
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
        if (country=='World'):
            url = self.baseurl + self.api1 + '&' + self.category + self.language
        else:
            url = self.baseurl + self.api1 + '&country=' + country2code(country) + '&' + self.category + self.language
        request = requests.get(url)
        if request.status_code==429:
            if (country=='World'):
                url = self.baseurl + self.api2 + '&' + self.category + self.language
            else:
                url = self.baseurl + self.api2 + '&country=' + country2code(country) + '&' + self.category + self.language
            request = requests.get(url)
        if request.status_code==429:
            if (country=='World'):
                url = self.baseurl + self.api3 + '&' + self.category + self.language
            else:
                url = self.baseurl + self.api3 + '&country=' + country2code(country) + '&' + self.category + self.language
            request = requests.get(url)

        if ((request.status_code!=200) or (request.json()['totalResults']<k)):
            url = self.baseurl + self.api1 + '&' + self.category + self.language     # Go Global
            request = requests.get(url)
            if request.status_code==429:
                url = self.baseurl + self.api2 + '&country=' + country2code(country) + '&' + self.category + self.language
                request = requests.get(url)
            if request.status_code==429:
                url = self.baseurl + self.api3 + '&country=' + country2code(country) + '&' + self.category + self.language
                request = requests.get(url)         

        response = request.json()

        news = self.get_top_k(response, k)
        return news

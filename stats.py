import os
import numpy as np
import pandas as pd
from datetime import date, timedelta

class Stat:
    def __init__(self, ):
        self.baseurl = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/'
        self.vaxurl = 'https://covid.ourworldindata.org/data/latest/owid-covid-latest.csv'
        self.vaxdata = pd.read_csv(self.vaxurl)
        prevday = (date.today()-timedelta(days=1)).strftime('%m-%d-%Y')
        url = self.baseurl + prevday + '.csv'
        try:
            self.data = pd.read_csv(url)
        except:
            prevday = (date.today()-timedelta(days=2)).strftime('%m-%d-%Y')
            url = self.baseurl + prevday + '.csv'
            self.data = pd.read_csv(url)
            self.data.Province_State = self.data.Province_State.fillna('All').copy()

    def get_vax(self, country):
        if country=='US':
            country = 'United States'
        df = self.vaxdata[self.vaxdata['location']==country][['people_vaccinated', 'people_fully_vaccinated', 'population']]
        per_fvax = df['people_vaccinated'].values/df['population'].values
        per_svax = df['people_fully_vaccinated'].values/df['population'].values

        return round(100*(per_fvax[0]), 1), round(100*(per_svax[0]), 1)

    def get_stat(self, country, region='All'):
        if country=='World':
            if country in self.data['Country_Region'].tolist():
                df = self.data[self.data['Country_Region']==region]
            else:
                self.data.loc[len(self.data), :] = self.data.sum(axis=0)
                self.data['Province_State'].loc[len(self.data)-1] = region
                self.data['Country_Region'].loc[len(self.data)-1] = country
                df = self.data.loc[len(self.data)-1]

        df = self.data[self.data['Country_Region']==country]
        if region=='All':
            if region in df['Province_State'].tolist():
                df = df[df['Province_State']==region]
            else:
                self.data.loc[len(self.data), :] = self.data[self.data['Country_Region']==country].sum(axis=0)
                self.data['Province_State'].loc[len(self.data)-1] = region
                self.data['Country_Region'].loc[len(self.data)-1] = country
                df = self.data.loc[len(self.data)-1]
                return (df['Confirmed'], df['Active'], df['Recovered'], df['Deaths'])

                
        else:
            df = df[df['Province_State']==region]
            if (len(df)==0):
                self.get_stat(country)
        
        return (df['Confirmed'].values[0], df['Active'].values[0], df['Recovered'].values[0], df['Deaths'].values[0])

if __name__ == '__main__':
    stats = Stat()
    print(stats.get_vax('India'))
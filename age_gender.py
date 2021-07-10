import os
import json
import numpy as np
import pandas as pd
import plotly.express as px
import plotly
import requests
import zipfile


class AgeGender:
    def __init__(self, fetch=False):
        if fetch:
            zip_file = requests.get('https://osf.io/43ucn/download')
            open('zip_file.zip', 'wb').write(zip_file.content)      # Save File
            with zipfile.ZipFile('zip_file', 'r') as zip_ref:       # Unzip
                zip_ref.extractall('data/')
            self.data = pd.read_csv(os.path.join('data', 'Data', 'Output_10.csv'), encoding='GBK', skiprows=3)
        else:
            self.data = pd.read_csv(os.path.join('data', 'Output_10.csv'), encoding='GBK')
            self.age2grp()

    def age2grp(self, age_col='Age', age_grp=None):
        if age_grp:
            self.age_grp = age_grp
        else:
            self.age_grp = {0: '0-10',
                      10: '10-20',
                      20: '20-30',
                      30: '30-40',
                      40: '40-50',
                      50: '50-60',
                      60: '60-70',
                      70: '70-80',
                      80: '80-90',
                      90: '90-100',
                      100: '100+'}
        self.data[age_col] = self.data[age_col].map(self.age_grp)

    def split_data(self, COUNTRY, REGION):
        self.df_b = {}
        self.df_m = {}
        self.df_f = {}

        for key, val in self.age_grp.items():
            self.df_b[val] = self.data[(self.data.Country==COUNTRY)
                         & (self.data.Age == val)
                         & (self.data.Region==REGION)
                         & (self.data.Sex=='b')].sort_values('Date', axis=0)
    
            self.df_m[val] = self.data[(self.data.Country==COUNTRY)
                         & (self.data.Age == val)
                         & (self.data.Region==REGION)
                         & (self.data.Sex=='m')].sort_values('Date', axis=0)
    
            self.df_f[val] = self.data[(self.data.Country==COUNTRY)
                         & (self.data.Age == val)
                         & (self.data.Region==REGION)
                         & (self.data.Sex=='f')].sort_values('Date', axis=0)
    
            ## ----------New Cases-----------------
            self.df_b[val].Cases = self.df_b[val].Cases.ffill().copy()
            self.df_b[val]['New Cases'] = self.df_b[val]['Cases'] - self.df_b[val]['Cases'].shift(1)
    
            self.df_m[val].Cases = self.df_m[val].Cases.ffill().copy()
            self.df_m[val]['New Cases'] = self.df_m[val].Cases - self.df_m[val].Cases.shift(1)
    
            self.df_f[val].Cases = self.df_f[val].Cases.ffill().copy()
            self.df_f[val]['New Cases'] = self.df_f[val].Cases - self.df_f[val].Cases.shift(1)

    def get_agegrp(self, AGE_GRP='20-30', convert2json=True):
        fig = px.pie(pd.concat([self.df_m[AGE_GRP][-7:], self.df_f[AGE_GRP][-7:]], axis=0), 
                     values='New Cases', names='Sex', 
                     title='Age, Gender and New Cases Plot',
                     hole=.6)
        if convert2json:
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            return graphJSON

        return fig

    def get_ageplot(self, convert2json=True):
        all_age = pd.DataFrame(columns=['Country', 'Region', 'Code', 
                                        'Date', 'Sex', 'Age', 
                                        'AgeInt', 'Cases', 'Deaths', 
                                        'Tests', 'New Cases'])
        for key, val in self.age_grp.items():
            all_age = pd.concat([all_age, self.df_m[val][-7:], self.df_f[val][-7:]], axis=0)
    
        fig = px.pie(all_age, 
                     values='New Cases', names='Age', 
                     title='Age and New Cases Plot',
                     hole=.6)
        if convert2json:
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            return graphJSON

        return fig

if __name__ == '__main__':
    ag = AgeGender()
    ag.split_data('USA', 'Michigan')
    agegrpplt = ag.get_agegrp(AGE_GRP='20-30', convert2json=False)
    agegrpplt.show()
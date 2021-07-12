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
            with zipfile.ZipFile('zip_file.zip', 'r') as zip_ref:       # Unzip
                zip_ref.extractall('data/')
                
        path = os.path.join('data', 'Data', 'Output_10.csv')
        

        self.data = pd.read_csv(path, encoding='GBK', skiprows=3)
        self.data = self.data.dropna(subset=['Country'])
        self.data.Date = pd.to_datetime(self.data.Date, format='%d.%m.%Y', errors = 'coerce')
        self.age2grp()

        self.g5050 = 'https://api.globalhealth5050.org/api/v1/agesex'
        r = requests.get(self.g5050)
        self.j = r.json()

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
        self._country = COUNTRY
        self.df_b = {}
        self.df_m = {}
        self.df_f = {}

        if REGION in self.data[self.data.Country==COUNTRY].Region.unique():
            pass
        else:
            region_selected = 'All'

        for key, val in self.age_grp.items():
            self.df_b[val] = self.data[(self.data.Country==COUNTRY)
                         & (self.data.Age == val)
                         & (self.data.Region==REGION)
                         & (self.data.Sex=='b')].sort_values('Date', axis=0)[-8:]

            self.df_m[val] = self.data[(self.data.Country==COUNTRY)
                         & (self.data.Age == val)
                         & (self.data.Region==REGION)
                         & (self.data.Sex=='m')].sort_values('Date', axis=0)[-8:]

            self.df_f[val] = self.data[(self.data.Country==COUNTRY)
                         & (self.data.Age == val)
                         & (self.data.Region==REGION)
                         & (self.data.Sex=='f')].sort_values('Date', axis=0)[-8:]

            ## ----------New Cases-----------------
            self.df_b[val].Cases = round(self.df_b[val].Cases.ffill().copy())
            self.df_b[val]['New Cases'] = self.df_b[val]['Cases'] - self.df_b[val]['Cases'].shift(1)
            self.df_b[val]['New Cases'] = self.df_b[val]['New Cases'].where(self.df_b[val]['New Cases']>0, 0)

            self.df_m[val].Cases = round(self.df_m[val].Cases.ffill().copy())
            self.df_m[val]['New Cases'] = self.df_m[val].Cases - self.df_m[val].Cases.shift(1)
            self.df_m[val]['New Cases'] = self.df_m[val]['New Cases'].where(self.df_m[val]['New Cases']>0, 0)

            self.df_f[val].Cases = round(self.df_f[val].Cases.ffill().copy())
            self.df_f[val]['New Cases'] = self.df_f[val].Cases - self.df_f[val].Cases.shift(1)
            self.df_f[val]['New Cases'] = self.df_f[val]['New Cases'].where(self.df_f[val]['New Cases']>0, 0)

            ## ----------New Deaths-----------------
            self.df_b[val].Deaths = round(self.df_b[val].Deaths.ffill().copy())
            self.df_b[val]['New Deaths'] = self.df_b[val]['Deaths'] - self.df_b[val]['Deaths'].shift(1)
            self.df_b[val]['New Deaths'] = self.df_b[val]['New Deaths'].where(self.df_b[val]['New Deaths']>0, 0)

            self.df_m[val].Deaths = round(self.df_m[val].Deaths.ffill().copy())
            self.df_m[val]['New Deaths'] = self.df_m[val].Deaths - self.df_m[val].Deaths.shift(1)
            self.df_m[val]['New Deaths'] = self.df_m[val]['New Deaths'].where(self.df_m[val]['New Deaths']>0, 0)

            self.df_f[val].Deaths = round(self.df_f[val].Deaths.ffill().copy())
            self.df_f[val]['New Deaths'] = self.df_f[val].Deaths - self.df_f[val].Deaths.shift(1)
            self.df_f[val]['New Deaths'] = self.df_f[val]['New Deaths'].where(self.df_f[val]['New Deaths']>0, 0)

    def get_agegrp(self, AGE_GRP='20-30', title='Age, Gender and New Cases Plot', values='New Cases', convert2json=True):
        if ((self.df_m[AGE_GRP][-7:]['New Cases'].sum()==0) and
          (self.df_m[AGE_GRP][-7:]['New Deaths'].sum()==0)):
            # Change Title to No data found
            title = "No Data Available!"
        elif (self.df_m[AGE_GRP][-7:]['New Cases'].sum()==0):
            # Switch to Deaths
            title = 'Age, Gender and New Deaths Plot'
            values = 'New Deaths'
        else:
            # Keep New Cases
            values = 'New Cases'

        if (title == "No Data Available!"):
            try:
                t = pd.DataFrame(self.j['data'][self._country]['CasebyAgeSex'])
                t.age_begin = t.age_begin.astype(int).map(self.age_grp)
                df_tt = t[t['age_begin']==AGE_GRP][['casesF', 'casesM']].T.reset_index()
                df_tt.columns = ['Sex', 'Cases']

                fig = px.pie(df_tt,
                         values='Cases', names='Sex', 
                         title='Data Not Found! Country Data from another source',
                         hole=.6)
            except:
                # Can't do anything more
                fig = px.pie(pd.concat([self.df_m[AGE_GRP][-7:], self.df_f[AGE_GRP][-7:]], axis=0), 
                         values=values, names='Sex', 
                         title=title,
                         hole=.6)
        else:
            fig = px.pie(pd.concat([self.df_m[AGE_GRP][-7:], self.df_f[AGE_GRP][-7:]], axis=0), 
                         values=values, names='Sex', 
                         title=title,
                         hole=.6)
        if convert2json:
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            return graphJSON

        return fig

    def get_ageplot(self, title='Age and New Cases Plot', values='New Cases', convert2json=True):
        all_age = pd.DataFrame(columns=['Country', 'Region', 'Code', 
                                        'Date', 'Sex', 'Age', 
                                        'AgeInt', 'Cases', 'Deaths', 
                                        'Tests', 'New Cases', 'New Deaths'])
        for key, val in self.age_grp.items():
            all_age = pd.concat([all_age, self.df_b[val][-7:]], axis=0)
            
        if ((all_age['New Cases'].sum()==0) and
          (all_age['New Deaths'].sum()==0)):
            # Change title to no data available
            title = "No Data Available!"
        elif (all_age['New Cases'].sum()==0):
            title = 'Age and New Deaths Plot'
            values = 'New Deaths'
        else:
            values = 'New Cases'

        if (title == "No Data Available!"):
            try:
                t = pd.DataFrame(self.j['data'][self._country]['CasebyAgeSex'])
                t['casesB'] = t['casesM'] + t['casesF']

                fig = px.pie(t,
                         values='casesB', names='age_group', 
                         title='Data Not Found! Country Data from another source',
                         hole=.6)
            except:
                # Can't do anything more
                fig = px.pie(all_age, 
                     values=values, names='Age', 
                     title=title,
                     hole=.6)
        else:
            fig = px.pie(all_age, 
                         values=values, names='Age', 
                         title=title,
                         hole=.6)
        if convert2json:
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            return graphJSON

        return fig

if __name__ == '__main__':
    ag = AgeGender()
    ag.split_data('USA', 'Washington')
    agegrpplt = ag.get_agegrp(AGE_GRP='0-10', convert2json=False)
    agegrpplt.show()
import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go


class TimeSeries:
    def __init__(self, baseurl=None):
        if baseurl:
            self.baseurl = baseurl
        self.baseurl = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/'
        self.usurl = 'https://github.com/nytimes/covid-19-data/raw/master/us-states.csv'
        self.triggerurl = 'https://covid.ourworldindata.org/data/jhu/new_cases.csv'
        self.triggerdata = pd.read_csv(self.triggerurl)


    def find_country(self, country, region='All'):
        country_idx = self.data[self.data['Country/Region']==country].index[0] if len(self.data[self.data['Country/Region']==country]) else len(self.data)+1
       
        return country_idx

    def calc_newcases(self, country_idx):
        new = []
        ### Add first entry

        new.append(self.data.iloc[country_idx][4])
        ### Iterate over rest
        for i in range(4+1, len(self.data.iloc[country_idx])):
            new.append(self.data.iloc[country_idx][i]-self.data.iloc[country_idx][i-1])
        new = [0 if ele<0 else ele for ele in new]


        return new

    def tolog(self, data):
        ### log 0 is infinity. Fake one person 
        data_t = np.log(data+np.ones(len(data)))

        return data_t

    def make_fig(self, country_idx, data, type, name, roll_window=7):
        fig = go.Figure()

        fig.add_trace(go.Histogram(x=self.data.iloc[country_idx][4:].index, 
                                 y=data, marker_color='royalblue',
                                 histfunc="avg", xbins_size="M1",
                                 name=f'{type.title()} {name} Cases'))

        fig.add_trace(go.Scatter(x=self.data.iloc[country_idx][4:].index, 
                                 y=pd.DataFrame(data).rolling(roll_window).mean()[0], mode='lines', 
                                 line=dict(color='firebrick', width=4,),
                                 name=f'{roll_window} Day Average'))

        fig.update_layout(bargap=0.2)

        fig.update_layout(
            autosize=True,
            margin=dict(t=10, b=10, r=10, l=10))

        fig.update_layout(legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ))

        return fig
    
    def make_usfig(self, data, type, name, roll_window=7):
        fig = go.Figure()
        if type=='new':
            col = type
        else:
            col = name
        fig.add_trace(go.Histogram(x=data['date'].astype(str), 
                                 y=data[col], marker_color='royalblue',
                                 histfunc="avg", xbins_size="D1",
                                 name=f'{type.title()} {name}'))

        fig.add_trace(go.Scatter(x=data['date'].astype(str), 
                                 y=data[col].rolling(roll_window).mean(), mode='lines', 
                                 line=dict(color='firebrick', width=4,),
                                 name=f'{roll_window} Day Average'))

        fig.update_layout(bargap=0.2)

        fig.update_layout(
            autosize=True,
            margin=dict(t=10, b=10, r=10, l=10))

        fig.update_layout(legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ))

        return fig

    def get_fig(self, country='World', region='All', data='confirmed', type='new', scale='linear'):
        """
            Returns a plotly figure of time series data
            country: 
                > Recognizable country name
            data:
                > confirmed
                > recovered
                > deaths
            type:
                > total
                > new
            scale:
                > linear
                > log
        """
        if ((country=='US') and (region!='All')):
            url = self.usurl
        else:
            url = self.baseurl + 'time_series_covid19_' + data + '_global' + '.csv'

        self.data = pd.read_csv(url)

        if(country == 'World'):
            # Total sum per column: 
            self.data.loc[len(self.data)]= self.data.sum(axis=0)
            self.data['Country/Region'].loc[len(self.data)-1] = 'World'

        if ((country!='US') or ((country=='US') and (region=='All'))):
            self.data['Province/State'] = self.data['Province/State'].fillna('All')

            country_idx = self.find_country(country)

            if type=='new':
                data_t = self.calc_newcases(country_idx)
            else:
                data_t = self.data.loc[country_idx][2:].values

            if scale=='log':
                data_t = self.tolog(data_t)

            fig = self.make_fig(country_idx, data_t, type, data)


        elif country=='US':

            statedata = self.data[self.data['state']==region]
            ## Recovered not available on NYTimes
            statedata = statedata.drop(columns='fips')

            if data=='confirmed':
                us_col = 'cases'
            elif data=='deaths':
                us_col = 'deaths'
            else:
                us_col = 'cases'

            if type=='new':
                statedata['new'] = statedata[us_col] - statedata[us_col].shift(1)

            if scale=='log':
                statedata['new'] = self.tolog(statedata['new'])

            fig = self.make_usfig(statedata, type, us_col)

        return fig

    def trigger_war(self, data, roll=[7, 14]):
        fastma = data.rolling(roll[0]).mean()
        slowma = data.rolling(roll[1]).mean()
        if (fastma.iloc[-1] > slowma.iloc[-1]):
            return 'MA Warning'
        else:
            return 'MA Fail'

    def get_trigger(self, country):
        if country=='US':
            country = 'United States'

        lvl = self.trigger_war(self.triggerdata[country], roll=[7, 14])

        return lvl

if __name__ == '__main__':
    ts = TimeSeries()
    fig = ts.get_fig(country='World', region='All')
    fig.show()
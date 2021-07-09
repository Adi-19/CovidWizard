import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go


class TimeSeries:
    def __init__(self, baseurl=None):
        if baseurl:
            self.baseurl = baseurl
        self.baseurl = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/'

    def find_country(self, country):
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
        data = np.log(data+np.ones(len(data)))

        return data

    def make_fig(self, country_idx, data, type, roll_window=7):
        fig = go.Figure()

        fig.add_trace(go.Histogram(x=self.data.iloc[country_idx][4:].index, 
                                 y=data, marker_color='royalblue',
                                 histfunc="avg", xbins_size="M1",
                                 name=f'{type.title()} Cases'))

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

    def get_fig(self, country='World', data='confirmed', type='total', scale='percent'):
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
        if country=='US':
            url = self.baseurl + 'time_series_covid19_' + data + '_US' + '.csv'
        else:
            url = self.baseurl + 'time_series_covid19_' + data + '_global' + '.csv'

        self.data = pd.read_csv(url)

        if(country == 'World'):
            # Total sum per column: 
            self.data.loc[len(self.data)]= self.data.sum(axis=0)
            self.data['Country/Region'].loc[len(self.data)-1] = 'World'

        self.data['Province/State'] = self.data['Province/State'].fillna('All')

        country_idx = self.find_country(country)

        if type=='new':
            data = self.calc_newcases(country_idx)
        else:
            data = self.data.loc[country_idx][2:].values

        if scale=='log':
            data = self.tolog(data)

        fig = self.make_fig(country_idx, data, type)

        return fig


    

from flask import Flask, render_template,request
import plotly
import plotly.graph_objs as go

import pandas as pd
import numpy as np
import json

app = Flask(__name__)


@app.route('/')
def index():
    feature = 'Bar'
    bar = create_plot(feature)
    return render_template('test.html', plot=bar)

def create_plot(feature):
    ts = TimeSeries()
    fig = ts.get_fig()
   
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON


if __name__ == '__main__':
    app.run()

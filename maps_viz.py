﻿import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
import plotly.graph_objects as go
import plotly.express as px
from sklearn.preprocessing import LabelEncoder


class OxfordGormint:
    def __init__(self, fetch=True):
        if fetch:
            self.data = pd.read_csv('https://github.com/OxCGRT/covid-policy-tracker/blob/master/data/OxCGRT_latest.csv?raw=true', low_memory=False)
        else:
            self.data = pd.read_csv('data/OxCGRT_latest.csv', low_memory=False)
        self.cr = pd.read_csv('data/CountryStateLL.csv')
        self.access_token = 'pk.eyJ1IjoiZW5yaWNvamFjb2JzIiwiYSI6ImNrcXN5cTR0MjBvM2cyb28zdzF5dnM2bG8ifQ.H55kEL_vM4bTRLhS3CdytQ'
        self.gormintdata = None
        self.fetched = False
        self.indexes = ['ContainmentHealthIndex', 'EconomicSupportIndex', 'GovernmentResponseIndex', 'StringencyIndex']

    def day2week(self, data_mod, date_col='Date', format='%Y%m%d'):
        data_mod['Year-Week'] = pd.to_datetime(data_mod[date_col], format=format).dt.strftime('%Y-%U')
        return data_mod

    def init_gormint(self, ):
        self.gormintdata = self.data.copy()
        self.gormintdata['Year-Week'] = pd.to_datetime(self.gormintdata['Date'], format='%Y%m%d').dt.strftime('%Y-%U')

        self.gormintdata['NewCases'] = self.gormintdata['ConfirmedCases'] - self.gormintdata['ConfirmedCases'].shift(1)

        self.gormintdata['ThisWkCases'] = self.gormintdata['NewCases'].rolling(window=7).sum()
        indexer = pd.api.indexers.FixedForwardWindowIndexer(window_size=7)
        self.gormintdata['NxtWkCases'] = self.gormintdata['NewCases'].rolling(window=indexer).sum()
        self.gormintdata['New Cases Percentage Change'] = 100*(self.gormintdata['NxtWkCases']-self.gormintdata['ThisWkCases'])/(self.gormintdata['ThisWkCases']+1)
        self.gormintdata['New Cases Percentage Change'] = self.gormintdata['New Cases Percentage Change'].round(1).fillna(0)
        self.fetched = True

    def analysisviz(self, POLICY):
        if POLICY in self.indexes:
            title = POLICY
            POLICY = POLICY + 'ForDisplay'
        else:
            title = POLICY[3:]
        if not(self.fetched):
            self.init_gormint()
        try:
            self.gormintdata[f'{POLICY} Wk']
        except:
            self.gormintdata[f'{POLICY} Wk'] = self.gormintdata[POLICY].rolling(window=7).min()

        range_color = [self.gormintdata[POLICY].min(), self.gormintdata[POLICY].max()]
        fig = px.choropleth(self.gormintdata, locations="CountryCode",
                            color=POLICY,
                            hover_name="CountryName",
                            title = title,
                            animation_frame="Year-Week",
                            hover_data=['New Cases Percentage Change'], 
                            color_continuous_scale=px.colors.sequential.PuRd,
                            range_color=range_color,)
        
        fig.update_layout(autosize=True, margin=dict(l=5, r=5, t=40, b=5))
        fig['layout']['updatemenus'][0]['pad']=dict(r= 10, t= 10)
        fig['layout']['sliders'][0]['pad']=dict(r= 10, t= 0,)

        return fig


    def add_latlong(self, data, index=['Year-Week','CountryName','RegionName'],):
        ## Use Pivot tables
        country_region = pd.pivot_table(self.cr, index=['CountryName', 'RegionName'])
        data_t = pd.pivot_table(data, index=index).drop(columns=['C1_Flag', 'C2_Flag', 'C3_Flag', 'C4_Flag', 'C5_Flag', 'C6_Flag', 'C7_Flag',
                                                                 'E1_Flag', 
                                                                 'H1_Flag', 'H6_Flag', 'H7_Flag', 'H8_Flag',
                                                                 'ContainmentHealthIndex', 'EconomicSupportIndex', 'GovernmentResponseIndex',
                                                                 'StringencyIndex', 'StringencyLegacyIndex', 'StringencyLegacyIndexForDisplay'])

        ## Add Lattitude and Longitude
        data_t = data_t.join(country_region)
        ## Re-Pivot data to make indexing easier: Year-Week > CountryName > RegionName
        data_t = pd.pivot_table(data_t, index=index)

        return data_t

    def make_frames(self, data_mod, weeks, cmax=1000000, cases='ConfirmedCases', 
                    lat_col='latitude', lon_col='longitude',
                    colorscale=[[0, "#e9d8a6"], [0.15, "#ee9b00"], [0.30, "#ca6702"],
                                [0.50, "#bb3e03"], [0.75, "#ae2012"], [1, "#9b2226"]],
                    hovertemplate='<extra></extra>'+'<em>%{customdata[0]}</em><br>' + 
                                '🚨  %{customdata[1]}<br>',
                    ):
        frames = []
        for wk in weeks[1:]:
            ThisWk = data_mod.xs(wk)[cases]
            if (wk[-2:]=='00'):
                LastWk = data_mod.xs(wk[:3]+str(int(wk[3])-1)+wk[4:-2]+'52')[cases]
            else:
                LastWk = data_mod.xs(wk[:-2]+'%02d'%(int(wk[-2:])-1))[cases]
            NewCases = round((ThisWk - LastWk))
            NewCases = NewCases.where(NewCases>0, 0)

            frames.append(
                {
                'name':'frame_{}'.format(wk),
                'data':[{
                    'type':'scattermapbox',
                    'lat':data_mod.xs(wk)[lat_col],
                    'lon':data_mod.xs(wk)[lon_col],
                    'marker':go.scattermapbox.Marker(
                        size=20*NewCases.fillna(0)/(np.mean(NewCases)+1),
                        sizemode='area',
                        sizemin=3,
                        color=NewCases,
                        colorscale=colorscale,
                        showscale=True,
                        colorbar={'title':cases, 'titleside':'top', 'thickness':4,},
                        cauto=False,
                        cmax=cmax,
                        ),
                    'customdata':np.stack((data_mod.xs(wk).index, NewCases), axis=-1),
                    'hovertemplate':hovertemplate
                }],           
            }) 

        return frames

    def make_sliders(self, weeks, frame_duration=100, transition_duration=50):
        sliders = [{
            'transition':{'duration': 0},
            'x':0.08, 
            'len':0.88,
            'currentvalue':{'font':{'size':15}, 'prefix':'📅 ', 'visible':True, 'xanchor':'center'},  
            'steps':[
                {
                    'label':wk,
                    'method':'animate',
                    'args':[
                        ['frame_{}'.format(wk)],
                        {'mode':'immediate', 'frame':{'duration':frame_duration, 'redraw': True}, 'transition':{'duration':transition_duration}}
                      ],
                } for wk in weeks]
        }]

        return sliders

    def make_playbutton(self, frame_duration=100, trasition_duration=50):
        play_button = [{
            'type':'buttons',
            'showactive':True,
            'x':0.045, 'y':-0.08,
            'buttons':[{ 
                'label':'Play', # Play
                'method':'animate',
                'args':[
                    None,
                    {
                        'frame':{'duration':frame_duration, 'redraw':True},
                        'transition':{'duration':trasition_duration},
                        'fromcurrent':True,
                        'mode':'immediate',
                    }
                ]
            }]
        }]

        return play_button

    def make_animation(self, frames, sliders, play_button, map_center=[45, -73]):
        # Defining the initial state
        data_init = frames[0]['data']

        # Create the figure and feed it all the prepared columns
        fig = go.Figure(data=data_init, frames=frames)

        # Specify layout information
        fig.update_layout(
            sliders=sliders,
            updatemenus=play_button,
            mapbox=dict(
                accesstoken=self.access_token, #
                center=go.layout.mapbox.Center(lat=map_center[0], lon=map_center[1]),
                zoom=1
            )
        )
        fig.update_layout(
            autosize=True,
            margin=dict(t=10, b=10, r=10, l=10))

        return fig

    def animate(self, region_col='RegionName'):
        data = self.data.copy(deep=True)
        data = self.day2week(data)
      
        data[region_col] = data[region_col].fillna('All')
        data = self.add_latlong(data)

        weeks = data.index.levels[0].tolist()
        
        frames = self.make_frames(data, weeks)
        sliders = self.make_sliders(weeks)
        play_button = self.make_playbutton()
        fig = self.make_animation(frames, sliders, play_button)

        return fig

    def getXy(self, data, COUNTRY, REGION):
        X = data[(data.CountryName==COUNTRY) & (data.RegionName==REGION)].drop(columns=['Year-Week', 'CountryName', 'RegionName'])
        X.ConfirmedCases = 100*(X.ConfirmedCases-X.ConfirmedCases.shift(1))/(X.ConfirmedCases.shift(1)+1)
        X = X.fillna(0)

        y = X.ConfirmedCases.shift(-1)
        return X, y

    def model(self, criterion='mse', n_estimators=150, 
                    max_depth=20, min_samples_leaf=2):
        rf = RandomForestRegressor(criterion=criterion, 
                                   random_state=101, 
                                   n_estimators=n_estimators, 
                                   max_depth=max_depth, 
                                   min_samples_leaf=min_samples_leaf, 
                                   bootstrap=False)
        
        return rf

    def get_dataml(self):
        data = self.data.copy(deep=True)
        data = self.day2week(data)
        data['RegionName'] = data['RegionName'].fillna('All')

        data = self.add_latlong(data, index=['CountryName', 'RegionName', 'Year-Week'])
        data = data.drop(columns=['Date', 'latitude', 'longitude'])
        data = pd.DataFrame(data.to_records())

        return data

    def predict_bstpolicy(self, ):
        data = self.get_dataml()
        le_c, le_r = LabelEncoder(), LabelEncoder()
        data['CountryName'] = le_c.fit_transform(data['CountryName'])
        data['RegionName'] = le_r.fit_transform(data['RegionName'])
        X = data.drop(columns=['Year-Week'])
        X.ConfirmedCases = 100*(X.ConfirmedCases-X.ConfirmedCases.shift(1))/(X.ConfirmedCases.shift(1)+1)
        X = X.fillna(0)

        pols = ['C1_School closing',
            'C2_Workplace closing', 'C3_Cancel public events',
            'C4_Restrictions on gatherings', 'C5_Close public transport',
            'C6_Stay at home requirements', 'C7_Restrictions on internal movement',
            'C8_International travel controls']
        X[pols] = X[pols].astype('int')

        X_find = X[(X.CountryName!=X.CountryName.shift(-1)) | (X.RegionName!=X.RegionName.shift(-1))]

        X = X[(X.CountryName==X.CountryName.shift(-1)) & (X.RegionName==X.RegionName.shift(-1))].copy()
        y = X[pols].shift(-1)

        rf = RandomForestClassifier(random_state=101, n_estimators=150, max_depth=20, min_samples_leaf=2, bootstrap=False)
        rf.fit(X[:-1], y[:-1])

        _X = pd.DataFrame()
        _X['CountryName'] = le_c.inverse_transform(X_find['CountryName']).copy()
        _X['RegionName'] = le_r.inverse_transform(X_find['RegionName']).copy()
        _X[pols] = rf.predict(X_find).astype('int')   

        decrease = _X[pols].values < X_find[pols].values
        increase = _X[pols].values > X_find[pols].values

        return _X, increase, decrease


    def predict_nxt(self, country='India', region='All'):
        data = self.get_dataml()

        if country in data.CountryName.unique().tolist():
            COUNTRY = country
            if region in data[data.CountryName==COUNTRY].RegionName.unique().tolist():
                REGION = region
            else:
                REGION = 'All'

            X, y = self.getXy(data, COUNTRY, REGION)
            rf = self.model()
            rf.fit(X[:-1], y[:-1])

            return rf.predict(X[-1:])[0]
        else:
            return -1

if __name__ == '__main__':
    oxgormint = OxfordGormint(fetch=False)
    _X, inc, dec = oxgormint.predict_bstpolicy()
    print(_X.head())
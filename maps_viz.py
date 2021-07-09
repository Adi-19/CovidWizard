import numpy as np
import pandas as pd
import plotly.graph_objects as go


class OxfordGormint:
    def __init__(self, fetch=True):
        if fetch:
            self.data = pd.read_csv('https://github.com/OxCGRT/covid-policy-tracker/blob/master/data/OxCGRT_latest.csv?raw=true')
        else:
            self.data = pd.read_csv('data/OxCGRT_latest.csv')
        self.cr = pd.read_csv('data/CountryStateLL.csv')
        self.access_token = 'pk.eyJ1IjoiZW5yaWNvamFjb2JzIiwiYSI6ImNrcXN5cTR0MjBvM2cyb28zdzF5dnM2bG8ifQ.H55kEL_vM4bTRLhS3CdytQ'

    def day2week(self, data_mod, date_col='Date', format='%Y%m%d'):
        data_mod['Year-Week'] = pd.to_datetime(data_mod[date_col], format=format).dt.strftime('%Y-%U')
        return data_mod

    def add_latlong(self, data_mod):
        ## Use Pivot tables
        country_region = pd.pivot_table(self.cr, index=['CountryName', 'RegionName'])
        data_mod = pd.pivot_table(data_mod, index=['Year-Week', 'CountryName', 'RegionName'])
        data_mod = data_mod.drop(columns=['C1_Flag', 'C3_Flag', 'C4_Flag', 'C5_Flag', 'C6_Flag', 'C7_Flag',
                                        'E1_Flag', 
                                        'H1_Flag', 'H6_Flag', 'H7_Flag', 'H8_Flag',
                                        'ContainmentHealthIndex', 'EconomicSupportIndex', 'GovernmentResponseIndex',
                                        'StringencyIndex', 'StringencyLegacyIndex', 'StringencyLegacyIndexForDisplay'])
        ## Add Lattitude and Longitude
        data_mod = data_mod.join(country_region)
        ## Re-Pivot data to make indexing easier: Year-Week > CountryName > RegionName
        data_mod = pd.pivot_table(data_mod, index=['Year-Week', 'CountryName', 'RegionName'])

        return data_mod

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
            margin=dict(t=50, b=10, r=10, l=10))

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

if __name__ == '__main__':
    oxgormint = OxfordGormint(fetch=False)
    fig = oxgormint.animate()

    import dash
    import dash_core_components as dcc
    import dash_html_components as html

    app = dash.Dash()
    app.layout = html.Div([
        dcc.Graph(figure=fig)
    ])

    app.run_server(debug=True, use_reloader=False)
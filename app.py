from flask import request, render_template
import dash
import dash_core_components as dcc
import dash_html_components as html
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
import plotly
import json

from server import server
from subregion import SubRegion
from news import Wendor
from maps_viz import OxfordGormint
from timeseries import TimeSeries
from cases_dash import app as time_dash


DEBUG = True

ts = TimeSeries()
subreg = SubRegion()
wendi = Wendor()

oxgormint = OxfordGormint(fetch=not(DEBUG))
## Real Map
fig = oxgormint.animate()

dash_app = dash.Dash(name='world-map', server=server, url_base_pathname='/world-map/')
dash_app.layout = html.Div([
    dcc.Graph(figure=fig)
])

application = DispatcherMiddleware(server, {'/dash': dash_app.server, '/dash2': time_dash.server})

selected_country = 'World'
region_selected = 'All'

@server.route('/', methods=['GET', 'POST'])
def index():
    ## For Region and SubRegion
    global selected_country
    global region_selected
    reset_global()

    index.country = request.form.get("search-country")
    if index.country:
        selected_country = index.country
    regions = subreg.find(selected_country)
    index.region_selected = request.form.get("search-region")
    if index.region_selected:
        region_selected = index.region_selected

    ## For getting country News
    news = wendi.get_news(selected_country)

    if selected_country:
        if region_selected=='All':
            fig = ts.get_fig(country=selected_country)
   
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        else:
            pass
    
    if region_selected:
        return render_template('index.html', regions=regions, country=selected_country, region_selected=region_selected, news=news, plot=graphJSON)

    return render_template('index.html', regions=regions, country=selected_country, region_selected='All', news=news, plot=graphJSON)

selected_data_ts = 'confirmed' 
selected_type_ts = 'new'
selected_scale_ts = 'linear'

def reset_global():
    global selected_data_ts 
    global selected_type_ts 
    global selected_scale_ts
    selected_data_ts = 'confirmed' 
    selected_type_ts = 'new'
    selected_scale_ts = 'linear'

@server.route('/data_ts', methods=['GET', 'POST'])
def change_data_ts():
    global selected_data_ts  

    selected_data_ts = request.args['selected']
    fig = ts.get_fig(country=selected_country, data=selected_data_ts, type=selected_type_ts, scale=selected_scale_ts)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

@server.route('/type_ts', methods=['GET', 'POST'])
def change_type_ts():
    global selected_type_ts 

    selected_type_ts = request.args['selected']
    fig = ts.get_fig(country=selected_country, data=selected_data_ts, type=selected_type_ts, scale=selected_scale_ts)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

@server.route('/scale_ts', methods=['GET', 'POST'])
def change_scale_ts():
    global selected_scale_ts 

    selected_scale_ts = request.args['selected']
    fig = ts.get_fig(country=selected_country, data=selected_data_ts, type=selected_type_ts, scale=selected_scale_ts)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON


@server.route('/analysis.html')
def analysis():
    return render_template('analysis.html')

if __name__ == '__main__':
    run_simple('localhost', 5000, application)
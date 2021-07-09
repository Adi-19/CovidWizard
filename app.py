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
            ts = TimeSeries()
            fig = ts.get_fig()
   
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        else:
            pass
    
    if region_selected:
        return render_template('index.html', regions=regions, country=selected_country, region_selected=region_selected, news=news, plot=graphJSON)

    return render_template('index.html', regions=regions, country=selected_country, region_selected='All', news=news, plot=graphJSON)

@server.route('/analysis.html')
def analysis():
    return render_template('analysis.html')

if __name__ == '__main__':
    run_simple('localhost', 5000, application)
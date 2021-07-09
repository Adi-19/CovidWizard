from flask import Flask, request, render_template
from flask import Markup
import dash
import dash_core_components as dcc
import dash_html_components as html
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
import json
import plotly
import plotly.express as px
import pandas as pd
from subregion import SubRegion
from news import Wendor
from maps_viz import OxfordGormint

DEBUG = True

server = Flask(__name__)
subreg = SubRegion()
wendi = Wendor()

oxgormint = OxfordGormint(fetch=not(DEBUG))
## Real Map
fig = oxgormint.animate()
graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

dash_app = dash.Dash(name='mydash', server=server, url_base_pathname='/mydash/')
dash_app.layout = html.Div([
    dcc.Graph(figure=fig)
])
application = DispatcherMiddleware(server, {'/dash': dash_app.server})

## Debug

selected_country = 'Global'

@server.route('/', methods=['GET', 'POST'])
def index():
    ## For Region and SubRegion
    global selected_country
    index.country = request.form.get("search-country")
    if index.country:
        selected_country = index.country
    regions = subreg.find(selected_country)
    region_selected = request.form.get("search-region")

    ## For getting country News
    news = wendi.get_news(selected_country)
    
    if region_selected:
        return render_template('index.html', regions=regions, country=selected_country, region_selected=region_selected, news=news, fig=graphJSON)

    return render_template('index.html', regions=regions, country=selected_country, region_selected='All', news=news, fig=graphJSON)
   

index.country = 'Global'

@server.route('/analysis.html')
def analysis():
    return render_template('analysis.html')

if __name__ == '__main__':
    run_simple('localhost', 5000, application)
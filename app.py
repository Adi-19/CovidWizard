from flask import request, render_template,Flask
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
from mapspolicy import oxgormint
from timeseries import TimeSeries
from analysis_index import app as index_dash
from analysis_policycc import app as cclose_dash
from analysis_econpol import app as econ_dash
from age_gender import AgeGender
from stats import Stat


DEBUG = True

stats = Stat()
ts = TimeSeries()
subreg = SubRegion()
wendi = Wendor()
ag = AgeGender(fetch=not(DEBUG))                    # For downloading data, change fetch to True

## Real Map
fig = oxgormint.animate()

dash_app = dash.Dash(name='world-map', server=server, url_base_pathname='/world-map/')
dash_app.layout = html.Div([
    dcc.Graph(figure=fig)
])

app = DispatcherMiddleware(server, {'/dash': dash_app.server, '/dash2': index_dash.server, 
                                            '/dash3': cclose_dash.server, '/dash4': econ_dash.server})

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
        region_selected = 'All'
    regions = subreg.find(selected_country)
    index.region_selected = request.form.get("search-region")
    if index.region_selected:
        region_selected = index.region_selected

    ## For getting country News
    news = wendi.get_news(selected_country)

    if selected_country:
        lvl = ts.get_trigger(selected_country)
        fig = ts.get_fig(country=selected_country, region=region_selected)
   
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        

    if selected_country == 'US':
        ag.split_data('USA', region_selected)
    else:
        ag.split_data(selected_country, region_selected)

    agegrpplt = ag.get_agegrp(AGE_GRP=selected_agegrp)
    allageplt = ag.get_ageplot()

    cnf, actv, recv, dead = stats.get_stat(selected_country, region_selected)
    if (cnf==float('NaN')):
        cnf=0
    if (actv==float('NaN')):
        actv=0
    if (recv==float('NaN')):
        recv=0
    if (dead==float('NaN')):
        dead=0
    recv = 1 - ((cnf-actv-recv)/(cnf-actv+1))
    per_fvax, per_svax = stats.get_vax(selected_country)

    try:
        cnf=int(cnf) 
    except:
        cnf=0
    try:
        actv=int(actv)
    except:
        actv=0
    try:
        recv=round(100*recv, 1) 
    except:
        recv=0
    try:
        dead=int(dead)
    except:
        dead=0
    
    return render_template('index.html', regions=regions, 
                           country=selected_country, region_selected=region_selected, 
                           news=news, lvl=lvl,
                           cnf=cnf, actv=actv, recv=recv, dead=dead, 
                           per_fvax=per_fvax, per_svax=per_svax,
                           plot=graphJSON, agegrpplt=agegrpplt, allageplt=allageplt)


selected_data_ts = 'confirmed' 
selected_type_ts = 'new'
selected_scale_ts = 'linear'
selected_agegrp = '0-10'

def reset_global():
    global selected_data_ts 
    global selected_type_ts 
    global selected_scale_ts
    global selected_agegrp
    selected_data_ts = 'confirmed' 
    selected_type_ts = 'new'
    selected_scale_ts = 'linear'
    selected_agegrp = '0-10'

@server.route('/data_ts', methods=['GET', 'POST'])
def change_data_ts():
    global selected_data_ts  

    selected_data_ts = request.args['selected']
    if selected_country!='US':
        fig = ts.get_fig(country=selected_country, data=selected_data_ts, type=selected_type_ts, scale=selected_scale_ts)
    else:
        fig = ts.get_fig(country=selected_country, region=region_selected, data=selected_data_ts, type=selected_type_ts, scale=selected_scale_ts)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

@server.route('/type_ts', methods=['GET', 'POST'])
def change_type_ts():
    global selected_type_ts 

    selected_type_ts = request.args['selected']
    if selected_country=='US':
        fig = ts.get_fig(country=selected_country, region=region_selected, data=selected_data_ts, type=selected_type_ts, scale=selected_scale_ts)
    else:
        fig = ts.get_fig(country=selected_country, data=selected_data_ts, type=selected_type_ts, scale=selected_scale_ts)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

@server.route('/scale_ts', methods=['GET', 'POST'])
def change_scale_ts():
    global selected_scale_ts 

    selected_scale_ts = request.args['selected']
    if selected_country=='US':
        fig = ts.get_fig(country=selected_country, region=region_selected, data=selected_data_ts, type=selected_type_ts, scale=selected_scale_ts)
    else:
        fig = ts.get_fig(country=selected_country, data=selected_data_ts, type=selected_type_ts, scale=selected_scale_ts)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

@server.route('/agegrp', methods=['GET', 'POST'])
def change_grp():
    global selected_agegrp

    selected_agegrp = request.args['selected']
    graphJSON = ag.get_agegrp(selected_agegrp)

    return graphJSON


@server.route('/analysis')
def analysis():
    return render_template('analysis.html')

@server.route('/analysis-1')
def analysis1():
    return render_template('analysis-1.html')

@server.route('/analysis-2')
def analysis2():
    return render_template('analysis-2.html')

@server.route('/analysis-3')
def analysis3():
    return render_template('analysis-3.html')


@server.route('/resources')
def resources():
    return render_template('resources.html')

if __name__ == '__main__':
    run_simple('localhost', 5000, app)

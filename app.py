from flask import request, render_template, redirect, Flask
import dash
import dash_core_components as dcc
import dash_html_components as html
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
import pandas as pd
import numpy as np
import plotly
import plotly.graph_objects as go
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
from NLPbot import AzureCognitive


DEBUG = True

stats = Stat()
ts = TimeSeries()
subreg = SubRegion()
wendi = Wendor()
az = AzureCognitive()
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

def reset_home():
    global selected_country
    global region_selected
    selected_country = 'World'
    region_selected = 'All'

@server.route('/', methods=['GET', 'POST'])
def index():
    ## For Region and SubRegion
    global selected_country
    global region_selected
    global adminMode
    reset_global()

    index.country = request.form.get("search-country")
    if index.country:
        if (index.country.lower() in ['us', 'usa', 'america', 'united states of america']):
                selected_country = 'US'
        elif (index.country.lower() in ['uk', 'united kingdom']):
                selected_country = 'UK'
        elif (index.country.title() in oxgormint.data.CountryName.unique().tolist()):
            selected_country = index.country.title()
        else:
            selected_country = 'World'
        region_selected = 'All'
    regions = subreg.find(selected_country)
    index.region_selected = request.form.get("search-region")
    if index.region_selected:
        region_selected = index.region_selected

    ## For getting country News
    news = wendi.get_news(selected_country, dummy=DEBUG)

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

    ml_war = oxgormint.predict_nxt(selected_country, region_selected)

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
                           news=news, lvl=lvl, ml_war=ml_war,
                           cnf=cnf, actv=actv, recv=recv, dead=dead, 
                           per_fvax=per_fvax, per_svax=per_svax,
                           plot=graphJSON, agegrpplt=agegrpplt, allageplt=allageplt,
                           adminMode=adminMode)


selected_data_ts = 'confirmed' 
selected_type_ts = 'new'
selected_scale_ts = 'linear'
selected_agegrp = '0-10'

def reset_global():
    global selected_data_ts 
    global selected_type_ts 
    global selected_scale_ts
    global selected_agegrp
    global selected_polcountry
    selected_data_ts = 'confirmed' 
    selected_type_ts = 'new'
    selected_scale_ts = 'linear'
    selected_agegrp = '0-10'
    selected_polcountry = 'Afghanistan'

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
    global adminMode
    reset_home()
    return render_template('analysis.html', adminMode=adminMode)

@server.route('/analysis-1')
def analysis1():
    global adminMode
    reset_home()
    return render_template('analysis-1.html', adminMode=adminMode)

def changeencode(data, cols):
    for col in cols:
        data[col] = data[col].astype('str').str.encode('utf-8')
    return data 


selected_polcountry = 'Afghanistan'

def make_polmap(_X, inc, dec, location, SELECTED, graph_json=True):
    indexes = _X[_X.CountryName==SELECTED].index.tolist()
    country_region = pd.pivot_table(oxgormint.cr, index=['CountryName', 'RegionName'])
    X_temp = pd.pivot_table(_X[_X.CountryName==SELECTED], index=['CountryName', 'RegionName']).join(country_region)
    txt = pd.DataFrame(inc[indexes])

    for col in range(8):
        txt[col] = txt[col].map({True:'Increase', False:'Same'})

    # Create the figure and feed it all the prepared columns
    color = inc[indexes].sum(axis=1)-dec[indexes].sum(axis=1)
    size = color*25
    size[color<0] = -color[color<0]/2
    size[color==0] = 1
    customdata = np.stack((X_temp.index, np.array(color)), axis=-1)
    customdata = np.hstack((customdata, txt))

    fig = plt_polmap(X_temp, SELECTED, size, color, customdata)
    if graph_json:
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return graphJSON
    return fig

def plt_polmap(X_temp, SELECTED, size, color, customdata):
    fig = go.Figure()

    fig.add_trace(go.Scattermapbox(
            lat=X_temp['latitude'],
            lon=X_temp['longitude'],
            mode='markers',
            marker=go.scattermapbox.Marker(
                sizemin=10,
                size=size,
                color=color,
                cmin=-8,
                cmax=8,
                colorscale=[[0, "#00d1ff"],
                        [0.3, "#12c2e9"],
                        [0.5, "#c471ed"],
                        [0.7, "#f64f59"],
                        [1, "#ff000f"]],
                showscale=True,
                colorbar={'title':'Change', 'titleside':'top', 'thickness':4,}, 
                cauto=False,),
            customdata=customdata,
            hovertemplate='<extra></extra>' + 
                            '<em>%{customdata[0]}</em><br>' + 
                            '🚨 Increase in level: %{customdata[1]}<br>' + 
                            'School closing: %{customdata[2]}<br>' + 
                            'Workplace closing: %{customdata[3]}<br>' + 
                            'Public Events Cancel: %{customdata[4]}<br>' + 
                            'Restrictions on Gathering: %{customdata[5]}<br>' + 
                            'Closure of Public Transport: %{customdata[6]}<br>' + 
                            'Stay at Home requirement: %{customdata[7]}<br>' + 
                            'Restrictions on Internal Movement: %{customdata[8]}<br>' + 
                            'International travel controls: %{customdata[9]}<br>',
            ),
    )

    # Specify layout information
    fig.update_layout(
        mapbox=dict(
            accesstoken='pk.eyJ1IjoiZW5yaWNvamFjb2JzIiwiYSI6ImNrcXN5cTR0MjBvM2cyb28zdzF5dnM2bG8ifQ.H55kEL_vM4bTRLhS3CdytQ', #
            center=go.layout.mapbox.Center(lat=X_temp.xs(SELECTED).xs('All')['latitude'], lon=X_temp.xs(SELECTED).xs('All')['longitude']),
            zoom=2
        ),
        margin=dict(t=10, b=10, r=10, l=10)
    )

    return fig    

@server.route('/analysis-2')
def analysis2():
    global adminMode
    global selected_polcountry
    reset_home()
    prediction, increase, decrease = oxgormint.predict_bstpolicy()
    countries = prediction.CountryName.unique().tolist()
    pol_countrygraph = make_polmap(prediction, increase, decrease, oxgormint.cr, selected_polcountry)
    return render_template('analysis-2.html', countries=countries, plot=pol_countrygraph, adminMode=adminMode)

@server.route('/policycountry', methods=['GET', 'POST'])
def policycountry():
    global selected_polcountry
    selected_polcountry = request.args['selected']
    prediction, increase, decrease = oxgormint.predict_bstpolicy()
    countries = prediction.CountryName.unique().tolist()
    graphJSON = make_polmap(prediction, increase, decrease, oxgormint.cr, selected_polcountry)

    return graphJSON

@server.route('/analysis-3')
def analysis3():
    global adminMode
    reset_home()
    return render_template('analysis-3.html', adminMode=adminMode)


@server.route('/resources')
def resources():
    reset_home()
    return render_template('resources.html', adminMode=adminMode)

@server.route('/login', methods=['GET', 'POST'])
def login():
    global adminMode
    global superUser

    reset_home()
    email = request.form.get("email")
    password = request.form.get("password")
    for em, pas in superUser.items():
        if (email==em and password==pas):
            adminMode = True
            return redirect("/")
    ## Wrong EmailId or Pass
    return render_template('login.html')

@server.route('/signup', methods=['GET', 'POST'])
def signup():
    global adminMode
    global superUser

    reset_home()
    email = request.form.get("email")
    password = request.form.get("password")
    password_repeat = request.form.get("password_repeat")
    
    if email:
        for em, pas in superUser.items():
            if em==email:
                return render_template('register.html')
        if (password!=password_repeat):
            return render_template('register.html')

        superUser[email] = password
        return redirect("login")

    return render_template('register.html')

@server.route('/logout', methods=['GET', 'POST'])
def logout():
    global adminMode
    reset_home()
    adminMode = False
    return redirect("/")

@server.route('/get')
def get_bot_response():
    global az

    userText = request.args.get('msg')
    resp = az.get_prediction(userText)

    return str(resp)

## Login ::Temporary for prototype::
superUser = {'admin@admin.com': 'admin'}      #username: password
adminMode = False                   #set to true if loggen in

if __name__ == '__main__':
    run_simple('0.0.0.0', 8000, app)

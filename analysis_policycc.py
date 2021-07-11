import dash
import dash_html_components as html
import dash_core_components as dcc
from mapspolicy import oxgormint
from server import server


app = dash.Dash(name='ContainClose Policy', server=server, url_base_pathname='/policycc/')
app.layout = html.Div([
    html.Div([
        dcc.Dropdown(
            id='chng-policy',
            options=[
                {'label': 'School closing', 'value': 'C1_School closing'},
                {'label': 'Workplace closing', 'value': 'C2_Workplace closing'},
                {'label': 'Cancel public events', 'value': 'C3_Cancel public events'},
                {'label': 'Restrictions on gatherings', 'value': 'C4_Restrictions on gatherings'},
                {'label': 'Close public transport', 'value': 'C5_Close public transport'},
                {'label': 'Stay at home requirements', 'value': 'C6_Stay at home requirements'},
                {'label': 'Restrictions on internal movement', 'value': 'C7_Restrictions on internal movement'},
                {'label': 'International travel controls', 'value': 'C8_International travel controls'},
            ],
            searchable=False,
            clearable=False,
            value='C6_Stay at home requirements'
        )
    ], style={'width': '20%', 'display': 'inline-block', 'padding-left': '75%'}),

    html.Div([
        dcc.Graph(id='dd-output-container')
    ]),
    html.Div(
        id='textarea-example-output',
        style={'whiteSpace': 'pre-line'})
])


@app.callback(
    dash.dependencies.Output('dd-output-container', 'figure'),
    [dash.dependencies.Input('chng-policy', 'value')])
def update_output(pol):
    fig = oxgormint.analysisviz(pol)
    return fig

@app.callback(
    dash.dependencies.Output('textarea-example-output', 'children'),
    [dash.dependencies.Input('chng-policy', 'value')])
def update_txt(pol):
    if pol=='C1_School closing':
        return ("Recorded closings of schools and universities")
    elif pol=="C2_Workplace closing":
        return ("Recorded closings of workplaces")
    elif pol=='C3_Cancel public events':
        return 'Record cancelling public events'
    elif pol=='C4_Restrictions on gatherings':
        return 'Record limits on gatherings'
    elif pol=='C5_Close public transport':
        return 'Record closing of public transport'
    elif pol=='C6_Stay at home requirements':
        return 'Record orders to "shelter-in-place" and otherwise confine to the home'
    elif pol=='C7_Restrictions on internal movement':
        return 'Record restrictions on internal movement between cities/regions'
    elif pol=='C8_International travel controls':
        return 'Record restrictions on international travel <br> Note: this records policy for foreign travellers, not citizens'

if __name__ == '__main__':
    app.run_server(debug=True)
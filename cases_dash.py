import dash
import dash_html_components as html
import dash_core_components as dcc
from timeseries import TimeSeries
from server import server

app = dash.Dash(name='timeseries-cases', server=server, url_base_pathname='/timeseries-cases/')
app.layout = html.Div([
    html.Div([
        dcc.Dropdown(
            id='data-dropdown',
            options=[
                {'label': 'Confirmed', 'value': 'confirmed'},
                {'label': 'Deaths', 'value': 'deaths'},
                {'label': 'Recovered', 'value': 'recovered'}
            ],
            searchable=False,
            clearable=False,
            value='confirmed'
        )
    ], style={'width': '20%', 'display': 'inline-block', 'padding-left': '63%'}),

    html.Div([
        dcc.Dropdown(
            id='type-dropdown',
            options=[
                {'label': 'Total', 'value': 'total'},
                {'label': 'New', 'value': 'new'}
            ],
            searchable=False,
            clearable=False,
            value='new'
        ),
    ], style={'width': '10%', 'float': 'right', 'display': 'inline-block', 'padding-right': '5%'}),

    html.Div([
        dcc.RadioItems(
                id='scale',
                options=[
                    {'label': 'Linear', 'value': 'linear'},
                    {'label': 'Log', 'value': 'log'}
                ],
                value='linear',
                labelStyle={'display': 'inline-block', 'padding': '1%'}
            )
    ], style={'padding-left': '75%'}),

    html.Div([
        dcc.Graph(id='dd-output-container')
    ])
])


@app.callback(
    dash.dependencies.Output('dd-output-container', 'figure'),
    [dash.dependencies.Input('data-dropdown', 'value'),
     dash.dependencies.Input('type-dropdown', 'value'),
     dash.dependencies.Input('scale', 'value')])
def update_output(data, type, scale):
    ts = TimeSeries()
    fig = ts.get_fig(data=data, type=type, scale=scale)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
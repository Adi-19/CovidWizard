import dash
import dash_html_components as html
import dash_core_components as dcc
from mapspolicy import oxgormint
from server import server


app = dash.Dash(name='Economic Policies', server=server, url_base_pathname='/econpolicy/')
app.layout = html.Div([
    html.Div([
        dcc.Dropdown(
            id='chng-policy',
            options=[
                {'label': 'Income support', 'value': 'E1_Income support'},
                {'label': 'Debt/contract relief', 'value': 'E2_Debt/contract relief'},
                {'label': 'Fiscal measures', 'value': 'E3_Fiscal measures'},
                {'label': 'International support', 'value': 'E4_International support'},
            ],
            searchable=False,
            clearable=False,
            value='E2_Debt/contract relief'
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
        return ("Record if the government is providing direct cash payments to people who lose their jobs or cannot work.<br>"+
                "Note: only includes payments to firms if explicitly linked to payroll/salaries")
    elif pol=='E2_Debt/contract relief':
        return 'Record if the government is freezing financial obligations for households (eg stopping loan repayments, preventing services like water from stopping, or banning evictions)'
    elif pol=='E3_Fiscal measures':
        return 'Announced economic stimulus spending <br> Note: only record amount additional to previously announced spending'
    elif pol=='E4_International support':
        return 'Announced offers of Covid-19 related aid spending to other countries <br> Note: only record amount additional to previously announced spending'

if __name__ == '__main__':
    app.run_server(debug=True)
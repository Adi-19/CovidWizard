import dash
import dash_html_components as html
import dash_core_components as dcc
from mapspolicy import oxgormint
from server import server


app = dash.Dash(name='Policy Index Viz', server=server, url_base_pathname='/policyindex/')
app.layout = html.Div([
    html.Div([
        dcc.Dropdown(
            id='chng-index',
            options=[
                {'label': 'Containment Health Index', 'value': 'ContainmentHealthIndex'},
                {'label': 'Economic Support Index', 'value': 'EconomicSupportIndex'},
                {'label': 'Government Response Index', 'value': 'GovernmentResponseIndex'},
                {'label': 'Stringency Index', 'value': 'StringencyIndex'},
            ],
            searchable=False,
            clearable=False,
            value='StringencyIndex'
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
    [dash.dependencies.Input('chng-index', 'value')])
def update_output(indx):
    fig = oxgormint.analysisviz(indx)
    return fig

@app.callback(
    dash.dependencies.Output('textarea-example-output', 'children'),
    [dash.dependencies.Input('chng-index', 'value')])
def update_txt(indx):
    if indx=='StringencyIndex':
        return ("The OxCGRT project calculate a Government Stringency Index, a composite measure of nine of the response metrics." + 
               "The nine metrics used to calculate the Government Stringency Index are:" + 
               "school closures; workplace closures; cancellation of public events; restrictions on public gatherings; " +
               "closures of public transport; stay-at-home requirements; public information campaigns; " + 
               "restrictions on internal movements; and international travel controls.")
    elif indx=="ContainmentHealthIndex":
        return ("The OxCGRT project also calculate a Containment and Health Index, a composite measure of thirteen of the response metrics." +
                "This index builds on the Government Stringency Index, using its nine indicators plus testing policy, " +
                "the extent of contact tracing, requirements to wear face coverings, and policies around vaccine rollout. " + 
                "It's therefore calculated on the basis of the following thirteen metrics: "+
                "school closures; workplace closures; cancellation of public events; restrictions on public gatherings; "+
                "closures of public transport; stay-at-home requirements; public information campaigns; "+
                "restrictions on internal movements; international travel controls; testing policy; extent of contact tracing;"+
                "face coverings; and vaccine policy.")

    return 'Soon to be updated'

if __name__ == '__main__':
    app.run_server(debug=True)
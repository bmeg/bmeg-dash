
from bmeg_app.app import app

import pandas as pd
import base64
import plotly.graph_objects as go
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from bmeg_app.views import app_Home

# # format logo
# image_filename = 'bmeg_app/images/logo.png' 
# encoded_image = base64.b64encode(open(image_filename, 'rb').read())

#######
# Web app
#######
# Main Tab
tabs_styles = {
    'height': '50px'}
tab_style = {
    'borderBottom': '3px solid #88BDBC',
    'backgroundColor': '#88BDBC',
    'font_family':'sans-serif',
    'fontSize': 15,
    'color': 'azure',
    'padding': '10px'}
tab_selected_style = {
    'border': '3px solid #026670',
    'backgroundColor': '#026670',
    'font_family':'sans-serif',
    'fontSize': 15 ,
    'color': 'whitesmoke',
    'padding': '10px'}

app.layout = html.Div([
    dcc.Location(id='url'),
    # html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()),
    #     style={'height':'100%', 'width':'100%', 'textAlign': 'left', 'marginTop': 20, 'marginBottom':0}),
    # Tab at top of page
    dcc.Tabs(id='main-tab', value='tab-Home', children=[
        dcc.Tab(label='Home', value='tab-Home', style=tab_style, selected_style=tab_selected_style),
    ]),
    html.Div(id='main-tab-content')
])

# Tab at top of page
@app.callback(Output('main-tab-content', 'children'),
              [Input('main-tab', 'value')])
def render_content(tab):
    if tab == 'tab-Home':
        return html.Div([app_Home.tab_layout])
    


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True, port=80)


from bmeg_app.app import app

import pandas as pd
import base64
import plotly.graph_objects as go
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from bmeg_app.views import app_about, app_tcga, app_drugresp, app_repurpose_drug
import base64


# # format logo
# image_filename = 'bmeg_app/images/logo.png' 
# encoded_image = base64.b64encode(open(image_filename, 'rb').read())

#######
# Web app
#######
# Main color scheme
main_colors = {
    'background': 'lightcyan',
    'text': 'black',
    'pale_yellow':'#FCE181',
    'pale_orange':'#F4976C',
    'lightblue':'#17BECF',
    'darkgreen_border':'#556B2F',
    'lightgreen_borderfill':'olivedrab',
    'lightgrey':'whitesmoke',
    'tab_lightblue':'#88BDBC',
    'tab_darkblue':'#026670'
}
tabs_styles = {
    'height': '50px'}
tab_style = {
    # 'borderBottom': '#88BDBC',
    # 'backgroundColor': '#88BDBC',
    'border':main_colors['tab_darkblue'],
    'backgroundColor': main_colors['tab_darkblue'],
    'font_family':'sans-serif',
    'fontSize': 15,
    'color': 'azure',
    'padding': '1px'
}

styles={
    'section_spaced': {
        # 'border': 'thin #556B2F solid',
        'backgroundColor': main_colors['tab_darkblue'],
        'textAlign': 'center',
        # 'color':main_colors['tab_darkblue'],
        'color':'white',
        'fontSize': 15,
        'marginTop':0,
        'marginBottom':0,
        'padding':5},
}

image_filename = 'bmeg_app/images/bmeg_logo.png' 
encoded_image3 = base64.b64encode(open(image_filename, 'rb').read())
 
 
app.layout = html.Div([
    dcc.Location(id='url'),
    # html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()),
    #     style={'height':'100%', 'width':'100%', 'textAlign': 'left', 'marginTop': 20, 'marginBottom':0}),
    # Tab at top of page
    dcc.Tabs(id='main-tab', value='tab-Repurp', children=[
        dcc.Tab(label='TCGA', value='tab-Tcga',style=tab_style, selected_style=tab_style),
        dcc.Tab(label='Drug Response', value='tab-DrugResponse',style=tab_style, selected_style=tab_style),
        dcc.Tab(label='Repurposing Drugs', value='tab-Repurp',style=tab_style, selected_style=tab_style),
        dcc.Tab(label='About', value='tab-About', style=tab_style, selected_style=tab_style),
        
        
    ]),
    html.Div(html.Img(src='data:image/png;base64,{}'.format(encoded_image3.decode()),
        style={'height':'15%','width':'15%', 'marginTop': 0, 'marginBottom':0})
    ,style={'textAlign':'center'}),
    html.H4(children='',style=styles['section_spaced']),

    html.Div(id='main-tab-content'),

])

# Tab at top of page
@app.callback(Output('main-tab-content', 'children'),
              [Input('main-tab', 'value')])
def render_content(tab):
    if tab == 'tab-Tcga':
        return html.Div([app_tcga.tab_layout])    
    elif tab == 'tab-DrugResponse':
        return html.Div([app_drugresp.tab_layout]) 
    elif tab == 'tab-Repurp':
        return html.Div([app_repurpose_drug.tab_layout]) 
    elif tab == 'tab-About':
        return html.Div([app_about.tab_layout])
        
    
        
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True, port=80)

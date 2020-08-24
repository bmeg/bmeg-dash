from bmeg_app.app import app
import bmeg_app.appLayout as ly
from bmeg_app.views import app_about, app_tcga, app_drugresp, app_repurpose_drug
import base64
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output

#######
# Prep
#######
# Main color scheme
main_colors=ly.main_colors
styles=ly.styles
tab_style=ly.styles['tab_style']

# Images
image_filename = 'bmeg_app/images/bmeg_logo.png' 
encoded_image3 = base64.b64encode(open(image_filename, 'rb').read())
 
#######
# Page  
####### 
app.layout = html.Div([
    dcc.Location(id='url'),
    dcc.Tabs(id='main-tab', value='tab-Repurp', children=[
        dcc.Tab(label='TCGA', value='tab-Tcga',style=tab_style, selected_style=tab_style),
        dcc.Tab(label='Drug Response', value='tab-DrugResponse',style=tab_style, selected_style=tab_style),
        dcc.Tab(label='Repurposing Drugs', value='tab-Repurp',style=tab_style, selected_style=tab_style),
        dcc.Tab(label='About', value='tab-About', style=tab_style, selected_style=tab_style),
    ]),
    html.Div(html.Img(src='data:image/png;base64,{}'.format(encoded_image3.decode()),
        style={'height':'15%','width':'15%', 'marginTop': 0, 'marginBottom':0}),
        style={'textAlign':'center'}),
    html.Div(id='main-tab-content'),
])

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

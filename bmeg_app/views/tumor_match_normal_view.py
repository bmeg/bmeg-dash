from ..app import app
from ..db import G
from ..components import basic_plots as bp, tumor_match_normal_component as tmn
from .. import appLayout as ly
import pandas as pd
import gripql
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import json

######################
# Prep
######################
# Main color scheme
main_colors= ly.main_colors
styles=ly.styles

# Populate list of all genes for selection of 2.Drug response table 
# TODO: cache select_genes list so can remove (below) .limit()
print('querying initial data 1')
q= G.query().V().hasLabel('Gene').limit(150).as_('gene').out('g2p_associations').as_('lit').out('compounds').as_('comp').out('drug_responses')
q= q.render(['$gene._gid','$lit._data.response_type'])
select_genes={}
for a,b in q:
    select_genes[a]=1


########
# Page  
####### 
print('loading app layout')   
tab_layout = html.Div(children=[
    dbc.Row(
        [
            dbc.Col(
                html.Div([
                    dbc.Button('Info', id='open2',color='primary',style={'font-size':styles['textStyles']['size_font']}),
                    dbc.Modal(
                        [
                            dbc.ModalHeader('Header for TCGA'),
                            dbc.ModalBody('Info on \
                                TCGA. \
                                Stuff 2'),
                            dbc.ModalFooter(dbc.Button('Close',id='close2',className='ml-auto')),
                        ],
                        id='main_help2',
                        size='sm',
                        centered=True,
                    ),
                ]),
                width=1, 
            ),  
            
            dbc.Col(dcc.Dropdown(
                id='project-dropdown',
                options=[{'label': l, 'value': gid} for gid,l in tmn.options_project().items()],
                value='Project:TCGA-CHOL',
                ),style={'font-size' : styles['textStyles']['size_font']} ),
            dbc.Col(dcc.Dropdown(id='property-dropdown'), style={'font-size' : styles['textStyles']['size_font']}),
    ]),
    html.Hr(),
    dbc.Button('?', id='open'),
    dbc.Modal(
        [
            dbc.ModalHeader('TCGA Gene Expression Clustering'),
            dbc.ModalBody('Explore property trends underlying the gene expression profiles. \
                Shown here are sample expression profiles from the selected TCGA cancer cohort (ex. cholangiocarcinoma). \
                Uniform manifold approximation and projection (UMAP) is a popular technique that is a similar visualization to t-SNE, \
                but can be used for general non-linear dimension reduction.'),
            dbc.ModalFooter(
                dbc.Button('Close',id='close',className='ml-auto')
            ),
        ],
        id='modal_centered',
        size='sm',
        centered=True,
    ),
    html.Div(id='intermediate_baseDF', style={'display': 'none'}),
    dcc.Loading(type="default",children=html.Div(id="umap_fig")),
],style={'fontFamily': styles['textStyles']['type_font']})

########
# Callbacks 
########
# help button main
@app.callback(
    Output("main_help2", "is_open"),
    [Input("open2", "n_clicks"), Input("close2", "n_clicks")],
    [State("main_help2", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open
    
# help button 
@app.callback(
    Output("modal_centered", "is_open"),
    [Input("open", "n_clicks"), Input("close", "n_clicks")],
    [State("modal_centered", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(Output('intermediate_baseDF', 'children'), 
    [Input('project-dropdown', 'value')])    
def createDF(selected_project):
    baseDF = tmn.get_df(selected_project,'$c._data.gdc_attributes.diagnoses.tumor_stage')
    return baseDF.to_json(orient="index")    # if selected_project is None: 
 
@app.callback(Output("umap_fig", "children"),
    [Input('intermediate_baseDF', 'children'),
    Input('property-dropdown', 'value')])
def render_callback(jsonstring,selected_property):
    temp=json.loads(jsonstring)
    baseDF = pd.DataFrame.from_dict(temp, orient='index')
    if selected_property=='$c._data.gdc_attributes.diagnoses.tumor_stage':
        fig1=tmn.get_umap(baseDF, 'UMAP', selected_property.split('.')[-1])
        return dcc.Graph(figure=fig1),
    else:
        updatedDF= tmn.update_umap(selected_property, baseDF)
        fig1=tmn.get_umap(updatedDF, 'UMAP', selected_property.split('.')[-1])
        return dcc.Graph(figure=fig1),
        
@app.callback(
    dash.dependencies.Output('property-dropdown', 'options'),
    [dash.dependencies.Input('project-dropdown', 'value')])
def set_cities_options(selected_project):
    return [{'label': l, 'value': query_string} for l,query_string in tmn.options_property(selected_project).items()]
    
@app.callback(
    dash.dependencies.Output('property-dropdown', 'value'),
    [dash.dependencies.Input('property-dropdown', 'options')])
def set_cities_value(available_options):
    return available_options[14]['value']

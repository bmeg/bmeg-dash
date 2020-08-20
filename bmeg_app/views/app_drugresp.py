#!/usr/bin/env python

from ..app import app
from ..db import G
from ..components import dresp, basic_plots as bp, gene_cluster as gC
from ..markdown import examples_tab as mk
import pandas as pd
import time
import sys
import gripql
from collections import Counter
import plotly.express as px
import json
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from urllib.request import urlopen
import dash_core_components as dcc
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc



        
######################
# Layout
######################
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
    'tab_darkblue':'#026670'}

styles = {
    'section_spaced': {
        # 'border': 'thin #556B2F solid',
        'backgroundColor': main_colors['tab_lightblue'],
        'textAlign': 'center',
        # 'color':main_colors['tab_darkblue'],
        'color':'white',
        'fontSize': 15,
        'marginTop':20,
        'marginBottom':0,
        'padding':5},
    'outline': {
        'borderLeft': 'thin #556B2F solid',
        'borderRight': 'thin #556B2F solid'},
    'font_source_middle': {'font_family': 'sans-serif', 'textAlign':'right','fontSize':10,'padding': 10,'borderLeft': 'thin #556B2F solid','borderRight': 'thin #556B2F solid','marginTop':0,'marginBottom':0},
    'font_source_bottom': {'font_family': 'sans-serif', 'textAlign':'right','fontSize':10,'padding': 10, 'borderLeft': 'thin #556B2F solid','borderRight': 'thin #556B2F solid','borderBottom': 'thin #556B2F solid','marginTop':0,'marginBottom':0},
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    },
}


default_stylesheet = [
    {
        'selector': 'node',
        'style': {
            'background-color': '#BFD7B5',
            'label': 'data(label)'
        }
    }
]

# Populate list of all genes for selection of 2.Drug response table 
# TODO: cache select_genes list so can remove (below) .limit()
print('querying initial data 1')
q= G.query().V().hasLabel('Gene').limit(150).as_('gene').out('g2p_associations').as_('lit').out('compounds').as_('comp').out('drug_responses')
q= q.render(['$gene._gid','$lit._data.response_type'])
select_genes={}
for a,b in q:
    select_genes[a]=1
# clustering options drop dropdown_table 
option_projects = gC.dropdown_options()

########
# Page  
####### 
print('loading app layout')   
tab_layout = html.Div(children=[
    html.H4(children='Drug Response',style=styles['section_spaced']),
    # html.P(children='Differential gene experssion analysis has lead to a list of top differentially expressed genes. You want a quick and easy method to find what drug(s) might be useful. Task: Given a list of differentially expressed genes, what is the predicted drug response that is supported by published literature?', style={'textAlign': 'center'}),
    html.Label('Gene(s)'),
    html.Div([dcc.Dropdown(id='dr_dropdown',
        options=[
            {'label': g, 'value': g} for g in select_genes.keys()],
        value=[],
        multi=True,
        ),     
    ],style={'width': '100%', 'display': 'inline-block'}), 
    html.Hr(),
    dbc.Button('?', id='open_dr'),
    dbc.Modal(
        [
            dbc.ModalHeader('Explore Published Literature Gene-Drug Associations'),
            dbc.ModalBody('Find cell line responses to drug treatments from literature curation and the dataset.'),
            dbc.ModalFooter(
                dbc.Button('Close',id='close_dr',className='ml-auto')
            ),
        ],
        id='modal_dr',
        size='sm',
        centered=True,
    ),
    dcc.Loading(type="default",children=html.Div(id="dr_dropdown_table")),  
])

########
# Callbacks 
########
# help button 
@app.callback(
    Output("modal_dr", "is_open"),
    [Input("open_dr", "n_clicks"), Input("close_dr", "n_clicks")],
    [State("modal_dr", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open
    
# app
@app.callback(Output("dr_dropdown_table", "children"),
    [Input('dr_dropdown', 'value')])
def render_callback(User_selected):
    data = []
    for gene in User_selected:
        data.append(gene)
    ##########
    drug_resp = 'AAC' # TODO change from hardcoded to selection
    ##########
    
    ### Query for base table ###
    baseDF = dresp.fullDF(drug_resp,data)
    ### High Level Gene-Drug ###
    # Table
    tab= dash_table.DataTable(id='dropdown_table',data = baseDF.to_dict('records'),columns=[{"name": i, "id": i} for i in baseDF.columns])
    
    ### Detailed Gene-Drug ###
    df2 = baseDF[['Drug Compound', 'Cell Line', 'dr_metric', 'Dataset']]
    df2= df2.rename(columns={'dr_metric':drug_resp})
    # Histograms
    drug_plot= dcc.Graph(figure=bp.get_histogram_normal(df2['Drug Compound'], 'Drug Compound', 'Frequency', main_colors['pale_orange'], 300, 200, 'drug','yes'))
    cellLine_plot= dcc.Graph(figure=bp.get_histogram_normal(df2['Cell Line'], 'Cell Line', 'Frequency',main_colors['pale_yellow'], 300, 10, 'cellline','yes'))
    resp_plot= dcc.Graph(figure=bp.get_histogram_normal(df2[drug_resp], drug_resp, 'Frequency',main_colors['pale_orange'], 300, 10,'drug','no'))
    # Table
    tab2= dash_table.DataTable(data = df2.to_dict('records'),columns=[{"name": i, "id": i} for i in df2.columns])
    return drug_plot,html.H1(''),cellLine_plot,html.H1(''),resp_plot,html.H1(''), tab, html.H1(''),tab2

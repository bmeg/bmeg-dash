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
    html.H4(children='Explore TCGA Data',style=styles['section_spaced']),
    html.Label('Cancer Type'),
    dcc.Dropdown(
        id='project-dropdown',
        options=[{'label': k, 'value': k} for k in option_projects.keys()],
        value='TCGA-CHOL',
        ),
    html.Label('Property'),
    dcc.Dropdown(id='property-dropdown'),
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
    dcc.Loading(type="default",children=html.Div(id="umap_fig")),
])

########
# Callbacks 
########
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

# TCGA 
@app.callback(Output("umap_fig", "children"),
    [Input('project-dropdown', 'value'),
    Input('property-dropdown', 'value')])
def render_callback(selected_project, selected_property):
    if selected_project is None: 
        return
    if selected_project !=[]:
        print(selected_project)
        data = gC.get_df(selected_project,selected_property)
        fig1=gC.get_umap(data, 'UMAP')
        return dcc.Graph(figure=fig1),

@app.callback(
    dash.dependencies.Output('property-dropdown', 'options'),
    [dash.dependencies.Input('project-dropdown', 'value')])
def set_cities_options(selected_project):
    return [{'label': k, 'value': v} for k,v in gC.mappings(selected_project).items()]
    
@app.callback(
    dash.dependencies.Output('property-dropdown', 'value'),
    [dash.dependencies.Input('property-dropdown', 'options')])
def set_cities_value(available_options):
    return available_options[14]['value']

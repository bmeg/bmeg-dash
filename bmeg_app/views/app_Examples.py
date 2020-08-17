#!/usr/bin/env python

from ..app import app
from ..db import G
from ..components import dresp, basic_plots as bp
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
from dash.dependencies import Input, Output
from urllib.request import urlopen
import dash_core_components as dcc



        
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
# TODO: cache select_genes list so can remove (below) .limit(1000)
q= G.query().V().hasLabel('Gene').as_('gene').limit(1000).out('g2p_associations').as_('lit').out('compounds').as_('comp')
q= q.render(['$gene._gid','$lit._data.response_type'])
select_genes={}
for a,b in q:
    if b is not None and a not in select_genes:
        select_genes[a]=1
# All drugs for Drug Response 2b example 
temp = G.query().V().hasLabel('Compound').render(['$._data.synonym'])
drugs=[]
for a in temp:
    if a[0] is not None:
        drugs.append(a[0])

# Drugs with G2P gene g2p_associations 
temp = G.query().V().hasLabel('Gene').limit(1000).out('g2p_associations').out('compounds').as_('comp').render(['$comp._gid'])
drugs_g2pgene = [i[0] for i in temp]


########
# Page  
#######    
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
tab_layout = html.Div(children=[
    html.H4(children='Drug Response',style=styles['section_spaced']),
    html.P(children='2a. Differential gene experssion analysis has lead to a list of top differentially expressed genes. You want a quick and easy method to find what drug(s) might be useful. Task: Given a list of differentially expressed genes, what is the predicted drug response that is supported by published literature?', style={'textAlign': 'center'}),
    html.Div([dcc.Dropdown(id='dr_dropdown',
        options=[
            {'label': g, 'value': g} for g in select_genes.keys()],
        value='ENSG00000159377',
        multi=True,
        ),     
        dcc.Loading(type="default",children=html.Div(id="dr_dropdown_table")),
        
    ]), 
])


        
@app.callback(Output("dr_dropdown_table", "children"),
    [Input('dr_dropdown', 'value')])
def render_callback(User_selected):
    data = []
    for gene in User_selected:
        data.append(gene)
        
    ##########
    drug_resp = 'AAC' # TODO change from hardcoded to selection
    ##########
    
    ### High Level Gene-Drug ###
    # Table
    input_df= dresp.evidenceTable(data)
    tab= dash_table.DataTable(id='dropdown_table',data = input_df.to_dict('records'),columns=[{"name": i, "id": i} for i in input_df.columns])
    ### Detailed Gene-Drug ###
    input_df= dresp.drug_response(data, drug_resp)
    # Histograms
    fig = bp.get_histogram_normal(input_df['Drug Compound'], 'Drug Compound', 'Frequency', main_colors['pale_orange'], 300, 200)
    drug_plot= dcc.Graph(figure=fig)
    fig = bp.get_histogram_normal(input_df['Cell Line'], 'Cell Line', 'Frequency',main_colors['pale_yellow'], 300, 10)
    cellLine_plot= dcc.Graph(figure=fig)
    fig = bp.get_histogram_normal(input_df[drug_resp], drug_resp, 'Frequency',main_colors['pale_orange'], 300, 10)
    resp_plot= dcc.Graph(figure=fig)
    # Table
    tab2= dash_table.DataTable(data = input_df.to_dict('records'),columns=[{"name": i, "id": i} for i in input_df.columns])
    return tab, html.H1(''), drug_plot,html.H1(''),cellLine_plot,html.H1(''),resp_plot,html.H1(''),tab2

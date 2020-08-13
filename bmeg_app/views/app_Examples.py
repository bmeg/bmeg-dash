#!/usr/bin/env python

from ..app import app
from ..db import G
from ..components import dresp
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
import dash_cytoscape as cyto
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
        'border': 'thin #556B2F solid',
        'backgroundColor': main_colors['lightgreen_borderfill'],
        'textAlign': 'center',
        'color':main_colors['lightgrey'],
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
    }
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


# Page      
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
tab_layout = html.Div(children=[
    html.H4(children='Cohort Genomics',style=styles['section_spaced']),
    html.P(children='1. Conduct a query that starts on the TCGA BRCA cohort, goes though Cases -> Samples -> Aliquots -> SomaticCallsets -> Alleles. Once at the alleles, do an aggregation to count the number of times each chromsome occurs', style={'textAlign': 'center'}),
    cyto.Cytoscape(
        id='click_node_data-callback',
        layout={'name': 'preset'},
        stylesheet=default_stylesheet,
        style={'width': '90%', 'height': '200px'},
        elements=[
            #Node
            {'data': {'id': 'proj', 'label': 'Project'}, 'position': {'x': 0, 'y': 0}},
            {'data': {'id': 'case', 'label': 'Case'}, 'position': {'x': 100, 'y': 100}},
            {'data': {'id': 'samp', 'label': 'Sample'}, 'position': {'x': 200, 'y': 0}},
            {'data': {'id': 'aliq', 'label': 'Aliquot'}, 'position': {'x': 300, 'y': 100}},
            {'data': {'id': 'allele', 'label': 'Allele'}, 'position': {'x': 400, 'y': 0}},
            #Edge
            {'data': {'source': 'proj', 'target': 'case'}},
            {'data': {'source': 'case', 'target': 'samp'}},
            {'data': {'source': 'samp', 'target': 'aliq'}},
            {'data': {'source': 'aliq', 'target': 'allele'}},
        ]
    ),
    # html.Pre(id='click_node_data', style=styles['pre']),  
    dcc.Markdown('''
    ```py
    import matplotlib.pyplot as plt
    import gripql
    conn = gripql.Connection("https://bmeg.io/api", credential_file="bmeg_credentials.json")
    G = conn.graph("rc5")

    q = G.query().V("Project:TCGA-BRCA").out("cases").out("samples")
    q = q.has(gripql.eq("gdc_attributes.sample_type", "Primary Tumor"))
    q = q.out("aliquots").out("somatic_callsets").out("alleles")
    q = q.has(gripql.eq("variant_type", "SNP"))
    q = q.aggregate(gripql.term("chrom", "chromosome"))
    res = q.execute()
    
    name = []
    count = []
    for i in res[0].chrom.buckets:
        name.append(i["key"])
        count.append(i["value"])
    plt.bar(name, count, width=0.35)
    ```
    ''', style={'textAlign': 'left'}),


    html.H4(children='Drug Response',style=styles['section_spaced']),
    html.P(children='2. Differential gene experssion analysis has lead to a list of top differentially expressed genes. You want a quick an easy method to find what drug(s) might be useful. Task: Given a list of differentially expressed genes, what is the predicted drug response that is supported by published literature?', style={'textAlign': 'center'}),

    html.Div([dcc.Dropdown(id='dr_dropdown',
        options=[
            {'label': g, 'value': g} for g in select_genes.keys()],
        value=[],
        placeholder='Search or Select',
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
    input_df= dresp.evidenceTable(data)
    tab= dash_table.DataTable(id='dropdown_table',data = input_df.to_dict('records'),columns=[{"name": i, "id": i} for i in input_df.columns])
    return tab




##############


    
@app.callback(Output('click_node_data', 'children'),
              [Input('click_node_data-callback', 'tapNodeData')])
def displayTapNodeData(data):
    if data is None: # if event is trigged before page/url fully loaded
        return 'Select Data'
    return json.dumps(data, indent=2)#.strip().split(',')[0].split(':')[1]

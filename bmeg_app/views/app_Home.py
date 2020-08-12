#!/usr/bin/env python

from ..app import app
from ..db import G
from ..components import basic_plots as bp
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

FORMAT_stripTABLE={
    'style_cell_conditional':[{'textAlign':'center','padding': '5px', 'height':'auto','whiteSpace': 'normal'}],
    'style_data_conditional':[{'if': {'row_index': 'odd'},'backgroundColor': 'rgb(248, 248, 248)','width': '100%'}],
    'style_header':{'backgroundColor': 'rgb(230, 230, 230)','fontWeight': 'bold'},
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


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

tab_layout = html.Div(children=[
    html.P(id='overview_table', children=''),
    dcc.Loading(id="overview_table",
            type="default",children=html.Div(id="overview_table_output")),
            
    html.P(id='lit_tab', children=''),
    dcc.Loading(id="lit_tab",
            type="default",children=html.Div(id="lit_tab_output")),    
])





    
    
    
    
    

@app.callback(Output("overview_table", "children"),
    [Input('url', 'pathname')])
def render_pip_rural(href):
    if href is None: # if event is trigged before page/url fully loaded
        raise PreventUpdate
    # count nodes of interest
    nodes_interest = ['Gene','Allele','Transcript','Protein','GeneOntologyTerm', 'PfamFamily'
                      'Compounds']
    res={}
    for node in nodes_interest:
        traverse = G.query().V().hasLabel(node).limit(500).as_('a')
        q = traverse.render('$a._gid')
        for a in q:
            if node in res:
                res[node]+=1
            else:
                res[node]=1
    keys=[]
    values=[]
    for k,v in res.items():
        keys.append(k)
        values.append(v)
    fig = bp.bar_thresh('Database Highlights','Node', keys, values, 5000, main_colors['pale_yellow'], 200, 'Graph Node', 'Available Data')

    # count nodes of interest
    nodes_interest = ['Sample','Aliquot']
    res={}
    for node in nodes_interest:
        traverse = G.query().V().hasLabel(node).limit(500).as_('a')
        q = traverse.render('$a._gid')
        for a in q:
            if node in res:
                res[node]+=1
            else:
                res[node]=1
    keys=[]
    values=[]
    for k,v in res.items():
        keys.append(k)
        values.append(v)
    fig2 = bp.bar_thresh('','Node', keys, values, 5000, main_colors['lightblue'], 200, 'Graph Node', 'Available Data')
    
    return dcc.Graph(id='overview_table_output', figure=fig),dcc.Graph(id='overview_table_output', figure=fig2),
    
    
@app.callback(Output("lit_tab", "children"),
    [Input('url', 'pathname')])
def render_pip_rural(href):
    if href is None: # if event is trigged before page/url fully loaded
        raise PreventUpdate
    # count nodes of interest
    nodes_interest = ['Publication','G2PAssociation']
    res={}
    for node in nodes_interest:
        traverse = G.query().V().hasLabel(node).limit(500).as_('a')
        q = traverse.render('$a._gid')
        for a in q:
            if node in res:
                res[node]+=1
            else:
                res[node]=1
    keys=[]
    values=[]
    for k,v in res.items():
        keys.append(k)
        values.append(v)
    fig = bp.bar_thresh('Database Highlights - Published Literature','Node', keys, values, 5000, main_colors['pale_yellow'], 200, 'Graph Node', 'Available Data')
    return dcc.Graph(id='lit_tab_output', figure=fig),

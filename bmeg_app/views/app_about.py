#!/usr/bin/env python

from ..app import app
from ..db import G
from ..components import basic_plots as bp, cards
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
import dash_table
import base64

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
        'marginTop':0,
        'marginBottom':0,
        'padding':5},
    'outline': {
        'borderLeft': 'thin #556B2F solid',
        'borderRight': 'thin #556B2F solid'},
    'font':{'font_family': 'sans-serif'},
    'font_source_middle': {'font_family': 'sans-serif', 'textAlign':'right','fontSize':10,'padding': 10,'borderLeft': 'thin #556B2F solid','borderRight': 'thin #556B2F solid','marginTop':0,'marginBottom':0},
    'font_source_bottom': {'font_family': 'sans-serif', 'textAlign':'right','fontSize':10,'padding': 10, 'borderLeft': 'thin #556B2F solid','borderRight': 'thin #556B2F solid','borderBottom': 'thin #556B2F solid','marginTop':0,'marginBottom':0},
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

style_table={
    'style_cell_conditional':[{'textAlign':'center', 'whiteSpace': 'normal'}],
    'style_data_conditional':[{'if': {'row_index': 'odd'},'backgroundColor': 'white'}],
    'style_header':{'backgroundColor': 'rgb(2,21,70)','fontWeight': 'bold', 'color':'white'},
}


# format logo
image_filename = 'bmeg_app/images/rc5_schema.png' 
encoded_image0 = base64.b64encode(open(image_filename, 'rb').read())
image_filename = 'bmeg_app/images/example1.png' 
encoded_image1 = base64.b64encode(open(image_filename, 'rb').read())
 
tab_layout = html.Div(children=[
    html.H4(children='What is stored inside the database?',style=styles['section_spaced']),
    dcc.Loading(id="cards",
            type="default",children=html.Div(id="cards_output")),  
    dcc.Loading(id="node_cts_bar",
            type="default",children=html.Div(id="node_cts_bar_output")),
                        
    html.H4(children='Database architecture',style=styles['section_spaced']),
    html.Img(src='data:image/png;base64,{}'.format(encoded_image0.decode()),
        style={'height':'30%', 'width':'50%','marginTop': 10, 'marginBottom':0}),

    html.P(children='Explore Node Properties'),
    html.Div([
        dcc.Dropdown(id='node_dd',
            options=[
                {'label': 'Gene', 'value': 'gene'},
                {'label': 'Project', 'value': 'project'},
                {'label': 'TODO Add all other nodes', 'value': 'todo'}
            ],
            value=[],
            placeholder='Select Node'),
        dcc.Loading(id="node_prop_table",
            type="default",children=html.Div(id="node_dd-selection")),
    ]),

    html.H1(children=''),        
    html.P(children='Example Usage'),
    dcc.Markdown('''
    ```py
    import gripql
    import pandas as pd
    conn = gripql.Connection("https://bmeg.io/api", credential_file = 'bmeg_credentials.json')
    G = conn.graph('rc5') # schema version 
    # Query BMEG
    q = G.query().V().hasLabel('Gene').as_('gene')
    q= q.render(['$gene._gid', '$gene._label', '$gene._data.start', '$gene._data.end'])
    ID=[]
    TYPE=[]
    START=[]
    STOP=[]
    for a,b,c,d in q:
        ID.append(a)
        TYPE.append(b)
        START.append(c)
        STOP.append(d)
    # Store as Pandas DataFrame
    df=pd.DataFrame(list(zip(ID,TYPE,START,STOP)),columns=['ID','Type','Start','Stop'])
    # View DataFrame Head
    df.iloc[:10,:]
    ```
    ''', style={'textAlign': 'left'}),
    html.P(children='Outputs the following DataFrame'),
    html.Img(src='data:image/png;base64,{}'.format(encoded_image1.decode()),
        style={'height':'30%', 'width':'30%','marginTop': 10, 'marginBottom':0}),
])


@app.callback(Output("node_dd-selection", "children"),
    [
        Input('url', 'pathname'),
        Input('node_dd', 'value')
    ])
def render_callback(href, node_selection):
    if href is None: # if event is trigged before page/url fully loaded
        raise PreventUpdate
    if node_selection == 'gene':
        NodeProperty = ['_gid','_label','_data',    
            '_data.chromosome',
            '_data.description',
            '_data.end',
            '_data.gene_id',
            '_data.genome',
            '_data.project_id',
            '_data.start',
            '_data.strand',
            '_data.submitter_id',
            '_data.symbol']
        Description=['Ensembl gene ID', 'BMEG tagged label', 'Data dictionary',
            '','','','','','','','','BMEG tagged submitter_id']
        Example= ['ENSG00000176022', 'Gene', '{\'chromosome\': \'1\', \'description\': \'UDP-Gal:betaGal beta 1,3-galactosyltransferase polypeptide 6\', ...}',
            1,'\'UDP-Gal:betaGal beta 1,3-galactosyltransferase polypeptide 6\'',1170421,'ENSG00000176022','GRCh37','Project:Reference',1167629,'+','None','B3GALT6']
        definitions_gene= pd.DataFrame(list(zip(NodeProperty, Description, Example)),columns=['Node Property', 'Description', 'Example'])
        df= definitions_gene
        return dash_table.DataTable(id='table_output',data = df.to_dict('records'),columns=[{"name": i, "id": i} for i in df.columns],
            # style_cell_conditional=style_table['style_cell_conditional'],
            # style_data_conditional = style_table['style_data_conditional'],
            # style_header = style_table['style_header'],
            )
        
    elif node_selection == 'project':
        NodeProperty = ['_gid','_label','_data',    
            '_data.gdc_attributes',
            '_data.project_id',
            '_data.submitter_id']
        Description=['Project Name', 'BMEG tagged label', 'Data dictionary',
            'TCGA Specific Data','Project ID','BMEG tagged submitter_id']
        Example= ['Project:TCGA-LUSC', 'Project', '{\'gdc_attributes\': {\'dbgap_accession_number\': None, \'disease_type\': [\'Squamous Cell Neoplasms\'],...}',
            '{\'gdc_attributes\': {\'dbgap_accession_number\': None, \'disease_type\': [\'Squamous Cell Neoplasms\'],...}',
            'TCGA-LUSC', 'None']
        definitions_gene= pd.DataFrame(list(zip(NodeProperty, Description, Example)),columns=['Node Property', 'Description', 'Example'])
        df= definitions_gene
        return dash_table.DataTable(id='table_output',data = df.to_dict('records'),columns=[{"name": i, "id": i} for i in df.columns],
            # style_cell_conditional=style_table['style_cell_conditional'],
            # style_data_conditional = style_table['style_data_conditional'],
            # style_header = style_table['style_header'],
            )
    elif node_selection=='todo':
        return
        
        
    
    
@app.callback(Output("cards", "children"),
    [Input('url', 'pathname')])
def render_callback(href):
    if href is None: # if event is trigged before page/url fully loaded
        raise PreventUpdate
    nodes_interest = ['Allele','Gene','Transcript','Exon','Protein','DrugResponse', 'Pathway','Compound', 'Interaction','Project','Publication', 'Aliquot']
    res = {}
    for l in nodes_interest:
        res[l] = G.query().V().hasLabel(l).count().execute()[0]['count']
    fig= cards.counts(100, res,main_colors['lightgrey'],styles['font']['font_family'])
    return dcc.Graph(id='cards_output', figure=fig),
        
    
    
@app.callback(Output("node_cts_bar", "children"),
    [Input('url', 'pathname')])
def render_callback(href):
    if href is None: # if event is trigged before page/url fully loaded
        raise PreventUpdate
    all_v =  G.listLabels()['vertex_labels']
    to_rm = ['Aliquot','Allele', 'Gene', 'Protein', 'Transcript', 'Exon','Pathway', 'Compound', 'DrugResponse', 'Interaction','Project', 'Publication']
    verts = [x for x in all_v if x not in to_rm]
    # count nodes of interest
    res = {}
    for l in verts:
        res[l] = G.query().V().hasLabel(l).count().execute()[0]['count']
    keys=[]
    values=[]
    for k,v in res.items():
        keys.append(k)
        values.append(v)
    fig = bp.bar_thresh('','Node', keys, values, 5000, main_colors['pale_yellow'], 250, '', '')
    return dcc.Graph(id='node_cts_bar_output', figure=fig),

    
        

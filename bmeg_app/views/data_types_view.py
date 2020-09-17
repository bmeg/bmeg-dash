from .. import appLayout as ly
from ..app import app
from ..components import data_types_component as dty
from ..db import G
import dash
from dash.dependencies import Input, Output
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import gripql
import pandas as pd
import plotly.express as px

#######
# Prep
#######
main_colors= ly.main_colors
styles=ly.styles

#######
# Page  
####### 
tab_layout = html.Div(children=[
    html.H4(children='What is stored inside the database?',style=styles['sh']),
    dcc.Loading(id="cards",
            type="default",children=html.Div(id="cards_output")),  
    dcc.Loading(id="node_cts_bar",
            type="default",children=html.Div(id="node_cts_bar_output")),
    html.P(children='Explore Node Properties',style={'font-size' : styles['t']['size_font']}),
    html.Div([
        dcc.Dropdown(id='node_dd',
            options=[
                {'label': 'Gene', 'value': 'gene'},
                {'label': 'Project', 'value': 'project'},
                {'label': 'TODO Add all other nodes', 'value': 'todo'}
            ],
            value=[],
            placeholder='Select Node',
            style={'font-size' : styles['t']['size_font']}),
        dcc.Loading(id="node_prop_table",
            type="default",children=html.Div(id="node_dd-selection")),
    ]),
],style={'fontFamily': styles['t']['type_font'],})


@app.callback(
    Output("node_dd-selection", "children"),
    [Input('url', 'pathname'),
    Input('node_dd', 'value')]
)
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
        return dash_table.DataTable(id='table_output',data = df.to_dict('records'),columns=[{"name": i, "id": i} for i in df.columns],style_table={'overflowY': 'scroll','font-size' : styles['t']['size_font']},page_size=10)
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
        return dash_table.DataTable(id='table_output',data = df.to_dict('records'),columns=[{"name": i, "id": i} for i in df.columns],style_table={'overflowY': 'scroll','font-size' : styles['t']['size_font']},page_size=10)
    elif node_selection=='todo':
        return
                
@app.callback(
    Output("cards", "children"),
    [Input('url', 'pathname')]
)
def render_callback(href):
    if href is None:
        raise PreventUpdate
    nodes_interest = ['Allele','Gene','Transcript','Exon','Protein','DrugResponse', 'Pathway','Compound', 'Interaction','Project','Publication', 'Aliquot']
    res = {}
    for l in nodes_interest:
        res[l] = G.query().V().hasLabel(l).count().execute()[0]['count']
    fig= dty.counts(100, res,main_colors['lightgrey'],styles['t']['type_font'])
    return dcc.Graph(id='cards_output', figure=fig),    
    
@app.callback(
    Output("node_cts_bar", "children"),
    [Input('url', 'pathname')]
)
def render_callback(href):
    if href is None:
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
    fig = dty.bar('','Node', keys, values, main_colors['pale_yellow'], 250, '', '')
    return dcc.Graph(id='node_cts_bar_output', figure=fig),

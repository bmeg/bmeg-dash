from ..app import app
from ..db import G
from ..components import dresp, basic_plots as bp, gene_cluster as gC
from .. import appLayout as ly
import pandas as pd
import gripql
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc

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
    
# clustering options drop dropdown_table 
option_projects = gC.dropdown_options()

########
# Page  
####### 
print('loading app layout')   
tab_layout = html.Div(children=[
    html.Label('Drug Screen Results Supported by Curated Literature', style={'font-size' : styles['textStyles']['size_font']}),
    html.Div([dcc.Dropdown(id='dr_dropdown',
        options=[
            {'label': g, 'value': g} for g in select_genes.keys()],
        value=[],
        multi=True,
        ),     
    ],style={'width': '100%', 'display': 'inline-block','font-size' : styles['textStyles']['size_font']}), 
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
        style={'font-size' : styles['textStyles']['size_font']},
    ),
    dcc.Loading(type="default",children=html.Div(id="dr_dropdown_table")),  
],style={'fontFamily': styles['textStyles']['type_font']})

@app.callback(
    Output("modal_dr", "is_open"),
    [Input("open_dr", "n_clicks"), Input("close_dr", "n_clicks")],
    [State("modal_dr", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open
    
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
    tab= dash_table.DataTable(id='dropdown_table',
        data = baseDF.to_dict('records'),columns=[{"name": i, "id": i} for i in baseDF.columns],
        style_table={'overflowY': 'scroll', 'maxHeight':200})
    
    ### Detailed Gene-Drug ###
    df2 = baseDF[['Drug Compound', 'Cell Line', 'dr_metric', 'Dataset']]
    df2= df2.rename(columns={'dr_metric':drug_resp})
    # Histograms
    drug_plot= dcc.Graph(figure=bp.get_histogram_normal(df2['Drug Compound'], 'Drug Compound', 'Frequency', main_colors['pale_orange'], 300, 200, 'drug','yes'))
    cellLine_plot= dcc.Graph(figure=bp.get_histogram_normal(df2['Cell Line'], 'Cell Line', 'Frequency',main_colors['pale_yellow'], 300, 10, 'cellline','yes'))
    resp_plot= dcc.Graph(figure=bp.get_histogram_normal(df2[drug_resp], drug_resp, 'Frequency',main_colors['pale_orange'], 300, 10,'drug','no'))
    # Table
    tab2= dash_table.DataTable(data = df2.to_dict('records'),
        columns=[{"name": i, "id": i} for i in df2.columns],
        style_table={'overflowY': 'scroll', 'maxHeight':200})
        
    # formatting figure arrangement 
    bar_plots = dbc.Row(
        [
            dbc.Col(drug_plot),
            dbc.Col(cellLine_plot),
            dbc.Col(resp_plot),
        ]
    )
    return bar_plots, tab, html.H1(''),tab2

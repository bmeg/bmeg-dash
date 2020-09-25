from .. import appLayout as ly
from ..app import app
from ..components import tumor_match_normal_component as tmn
from ..db import G
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_html_components as html
import gripql
import json
import pandas as pd

#######
# Prep
#######
main_colors= ly.main_colors
styles=ly.styles
print('querying initial data 1') # TODO: cache select_genes list so can remove (below) .limit()
q= G.query().V().hasLabel('Gene').limit(150).as_('gene').out('g2p_associations').as_('lit').out('compounds').as_('comp').out('drug_responses')
q= q.render(['$gene._gid','$lit._data.response_type'])
select_genes={}
for a,b in q:
    select_genes[a]=1

#######
# Page
#######
print('loading app layout')
NAME="TCGA Clustering"
LAYOUT = html.Div(children=[
    dbc.Row(
        [
            dbc.Col(
                [
                    html.Label('Cancer cohort'),
                    dcc.Dropdown(id='project_dd_tmn',
                        options=[{'label': l, 'value': gid} for gid,l in tmn.options_project().items()],value='Project:TCGA-CHOL',
                    )
                ],
                style={'font-size' : styles['t']['size_font']}
            ),
            dbc.Col(
                [
                    html.Label('Property'),
                    dcc.Dropdown(id='property_dd_tmn')
                ],
                style={'font-size' : styles['t']['size_font']}
            ),
    ]),
    html.Hr(),
    dbc.Button('?', id='info_open_tmn'),
    dbc.Modal(
        [
            dbc.ModalHeader('TCGA Gene Expression Clustering'),
            dbc.ModalBody('Explore property trends underlying the gene expression profiles. \
                Shown here are sample expression profiles from the selected TCGA cancer cohort (ex. cholangiocarcinoma). \
                Uniform manifold approximation and projection (UMAP) is a popular technique that is a similar visualization to t-SNE, \
                but can be used for general non-linear dimension reduction.'),
            dbc.ModalFooter(
                dbc.Button('Close',id='info_close_tmn',className='ml-auto')
            ),
        ],
        id='info_modal',
        size='sm',
        centered=True,
    ),
    html.Div(id='hidden_base_df_tmn', style={'display': 'none'}),
    dcc.Loading(type="default",children=html.Div(id="umap_fig")),
],style={'fontFamily': styles['t']['type_font']})

@app.callback(
    Output("info_modal", "is_open"),
    [Input("info_open_tmn", "n_clicks"), Input("info_close_tmn", "n_clicks")],
    [State("info_modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(
    Output('hidden_base_df_tmn', 'children'),
    [Input('project_dd_tmn', 'value')]
)
def createDF(selected_project):
    df = tmn.get_df(selected_project,'$c._data.gdc_attributes.diagnoses.tumor_stage')
    return df.to_json(orient="index")

@app.callback(
    Output("umap_fig", "children"),
    [Input('hidden_base_df_tmn', 'children'),
    Input('property_dd_tmn', 'value')]
)
def render_callback(jsonstring,selected_property):
    temp=json.loads(jsonstring)
    df = pd.DataFrame.from_dict(temp, orient='index')
    if selected_property=='$c._data.gdc_attributes.diagnoses.tumor_stage':
        fig=tmn.get_umap(df, 'UMAP', selected_property.split('.')[-1])
        return dcc.Graph(figure=fig),
    else:
        df2= tmn.update_umap(selected_property, df)
        fig=tmn.get_umap(df2, 'UMAP', selected_property.split('.')[-1])
        return dcc.Graph(figure=fig),

@app.callback(
    Output('property_dd_tmn', 'options'),
    [Input('project_dd_tmn', 'value')]
)
def render_callback(selected_project):
    return [{'label': l, 'value': query_string} for l,query_string in tmn.options_property(selected_project).items()]

@app.callback(
    Output('property_dd_tmn', 'value'),
    [Input('property_dd_tmn', 'options')]
)
def render_callback(available_options):
    return available_options[14]['value']

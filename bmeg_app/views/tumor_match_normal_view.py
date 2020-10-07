from ..app import app
from ..components import tumor_match_normal_component as tmn
from ..db import G
from ..style import format_style
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_html_components as html
import gripql
import json
import pandas as pd

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
                style={'font-size' : format_style('font_size')}
            ),
            dbc.Col(
                [
                    html.Label('Property'),
                    dcc.Dropdown(id='property_dd_tmn')
                ],
                style={'font-size' : format_style('font_size')}
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
],style={'fontFamily': format_style('font_size')})

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

from ..app import app
from ..components import tumor_match_normal_component as tmn, info_button
from ..db import G
from ..style import format_style
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import dash_html_components as html
import gripql
import os
import json
from glob import glob
import pandas as pd
import plotly.express as px
import i18n
i18n.load_path.append('bmeg_app/locales/')

#######
# Page
#######
PROJECT_LOCS = {}
PROJECT_NAME = {}
for path in glob("bmeg_app/data/*.id"):
    base = path.split(".id")[0]
    if os.path.exists(base + ".locs"):
        with open(path) as handle:
            project_id = handle.read().rstrip()
        PROJECT_LOCS[project_id] = base + ".locs"
        PROJECT_NAME[project_id] = os.path.basename(base)
del PROJECT_NAME['Project:CTRP']
del PROJECT_NAME['Project:GDSC']
del PROJECT_LOCS['Project:CTRP']
del PROJECT_LOCS['Project:GDSC']

NAME="RNA expression projection"
LAYOUT = html.Div(
    children=[
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label(i18n.t('app.widget_cluster.menu1')),
                        dcc.Dropdown(
                            id='project_dd_tmn',
                            options=[
                                {'label': l, 'value': gid}
                                for gid, l in PROJECT_NAME.items()
                            ],
                            value='Project:TCGA-CHOL',
                        )
                    ],
                    style={'font-size': format_style('font_size')}
                ),
                dbc.Col(
                    [
                        html.Label(i18n.t('app.widget_cluster.menu2')),
                        dcc.Dropdown(id='property_dd_tmn')
                    ],
                    style={'font-size': format_style('font_size')}
                ),
            ]
        ),
        html.Hr(),
        html.Div(
            info_button(
                'help_umap',
                i18n.t('app.widget_cluster.button_body')
            ),
            style={'textAlign': 'right'}
        ),
        html.Div(id='hidden_base_df_tmn', style={'display': 'none'}),
        dcc.Loading(type="default", children=html.Div(id="umap_fig")),
    ],
    style={'fontFamily': format_style('font')}
)


# @app.callback(
#     Output('hidden_base_df_tmn', 'children'),
#     [Input('project_dd_tmn', 'value')]
# )
# def createDF(selected_project):
#     df = tmn.get_df(
#         selected_project,
#         '$c._data.gdc_attributes.diagnoses.tumor_stage'
#     )
#     return df.to_json(orient="index")


@app.callback(
    Output("umap_fig", "children"),
    [
        Input('project_dd_tmn', 'value'),
        Input('property_dd_tmn', 'value')
    ]
)
def render_callback(project, prop):
    if not project:
        raise PreventUpdate
    app.logger.info("loading: %s" % (PROJECT_LOCS[project]))
    df = pd.read_csv(PROJECT_LOCS[project], sep="\t", index_col=0, names=["sample", "x", "y"], skiprows=1)
    new_col=[]
    q = G.query().V(list(df.index)).out("case").as_('c').render([prop])
    for row in q:
        info = row[0]
        if info is None:
            info = 'Not Reported'
        if 'TCGA' in project:
            new_col.append(info[0])
        else:
            new_col.append(info)
    df['Characteristic']=new_col
    fig = px.scatter(
        df,
        x='x',
        y='y',
        color='Characteristic')
    fig.update_layout(title=PROJECT_NAME[project],height=400)
    return dcc.Graph(figure=fig)
# def render_umap(jsonstring, selected_property):
#     temp = json.loads(jsonstring)
#     df = pd.DataFrame.from_dict(temp, orient='index')
#     if selected_property == '$c._data.gdc_attributes.diagnoses.tumor_stage':
#         fig = tmn.get_umap(
#             df,
#             'UMAP',
#             selected_property.split('.')[-1]
#         )
#         return dcc.Graph(figure=fig),
#     else:
#         df2 = tmn.update_umap(selected_property, df)
#         fig = tmn.get_umap(df2, 'UMAP', selected_property.split('.')[-1])
#         return dcc.Graph(figure=fig),
#
#
@app.callback(
    Output('property_dd_tmn', 'options'),
    [Input('project_dd_tmn', 'value')]
)
def render_options(selected_project):
    out = [
        {'label': label.capitalize(), 'value': query_string}
        for label, query_string in
        tmn.options_property(selected_project).items()
    ]
    return out
#
#
@app.callback(
    Output('property_dd_tmn', 'value'),
    [Input('property_dd_tmn', 'options')]
)
def render_value(available_options):
    return available_options[0]['value']

from ..app import app
from ..components import tumor_match_normal_component as tmn, info_button
from ..style import format_style
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_html_components as html
import json
import pandas as pd
import i18n
i18n.load_path.append('bmeg_app/locales/')

#######
# Page
#######
print('loading app layout')
NAME = "TCGA Clustering"
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
                                {'label': l.split('-')[1], 'value': gid}
                                for gid, l in tmn.options_project().items()
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


@app.callback(
    Output('hidden_base_df_tmn', 'children'),
    [Input('project_dd_tmn', 'value')]
)
def createDF(selected_project):
    df = tmn.get_df(
        selected_project,
        '$c._data.gdc_attributes.diagnoses.tumor_stage'
    )
    return df.to_json(orient="index")


@app.callback(
    Output("umap_fig", "children"),
    [
        Input('hidden_base_df_tmn', 'children'),
        Input('property_dd_tmn', 'value')
    ]
)
def render_umap(jsonstring, selected_property):
    temp = json.loads(jsonstring)
    df = pd.DataFrame.from_dict(temp, orient='index')
    if selected_property == '$c._data.gdc_attributes.diagnoses.tumor_stage':
        fig = tmn.get_umap(
            df,
            'UMAP',
            selected_property.split('.')[-1]
        )
        return dcc.Graph(figure=fig),
    else:
        df2 = tmn.update_umap(selected_property, df)
        fig = tmn.get_umap(df2, 'UMAP', selected_property.split('.')[-1])
        return dcc.Graph(figure=fig),


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


@app.callback(
    Output('property_dd_tmn', 'value'),
    [Input('property_dd_tmn', 'options')]
)
def render_value(available_options):
    return available_options[14]['value']

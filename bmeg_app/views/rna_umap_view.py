from ..app import app
from ..components import tumor_match_normal_component as tmn, info_button
from ..db import G
from ..style import format_style
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output
import dash_html_components as html
import os
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
for p in ['Project:CTRP', 'Project:GDSC']:
    if p in PROJECT_NAME:
        del PROJECT_NAME[p]
    if p in PROJECT_LOCS:
        del PROJECT_LOCS[p]

NAME = "RNA expression projection"
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
                            value='Project:CCLE',
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
    df = pd.read_csv(
        PROJECT_LOCS[project],
        sep="\t",
        index_col=0,
        names=["sample", "x", "y"],
        skiprows=1
    )
    print('selected: ', project, prop)
    new_col = []
    if prop == '$c._data.gdc_attributes.sample_type':
        print('reached this if statement')
        q = G.query().V(list(df.index)).as_('c').render([prop])
        for row in q:
            info = row[0]
            if info is None:
                info = 'Not Reported'
            new_col.append(info)

    else:
        q = G.query().V(list(df.index)).out("case").as_('c').render([prop])
        for row in q:
            info = row[0]
            if info is None:
                info = 'Not Reported'
            if isinstance(info, list):
                if len(info) == 0:
                    new_col.append('Not Reported')
                else:
                    new_col.append(info[0])
            else:
                new_col.append(info)

    display_prop = prop.split('.')[-1].replace('_', ' ').capitalize()
    df[display_prop] = new_col
    fig = px.scatter(
        df,
        x='x',
        y='y',
        color=display_prop)
    fig.update_layout(title=PROJECT_NAME[project], height=400)
    return dcc.Graph(figure=fig)


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
    if 'TCGA' in selected_project:
        out.append({
            'label': 'Sample Type',
            'value': '$c._data.gdc_attributes.sample_type'
        })
    return out


@app.callback(
    Output('property_dd_tmn', 'value'),
    [Input('property_dd_tmn', 'options')]
)
def render_value(available_options):
    return available_options[0]['value']

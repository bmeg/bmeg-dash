from ..app import app
from ..components import compare_dresp_component as cdr
from ..db import G
from ..components import info_button
from ..style import format_style
import dash_bootstrap_components as dbc
from dash import dcc
from dash.dependencies import Input, Output, State, MATCH
from dash import html
import json
import pandas as pd
import plotly.express as px
import i18n
import os

#######
# Prep
#######

BASEDIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASEDIR, '../locales/data.json'), 'r') as fh:
    menu_options = json.load(fh)
projects_options = menu_options['cell_line_projects']
dresp_options = menu_options['drug_responses']

#######
# Page
#######
print('loading app layout')
NAME = i18n.t('app.config.tabname_widget_dresp')


def CREATE(index):
    return html.Div(
        children=[
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            [
                                html.Label(i18n.t('app.widget_dresp.menu1')),
                                dcc.Dropdown(
                                    id={"type":'project_dd_cdr', "index":index},
                                    options=[
                                        {'label': l, 'value': gid}
                                        for gid, l in projects_options.items()
                                    ],
                                    value='Project:CCLE'
                                )
                            ],
                            style={
                                'width': '100%',
                                'display': 'inline-block',
                                'font-size': format_style('font_size')
                            }
                        )
                    ),
                    dbc.Col(
                        html.Div(
                            [
                                html.Label(i18n.t('app.widget_dresp.menu2')),
                                dcc.Dropdown(
                                    id={"type":'dresp_dd_cdr', "index":index},
                                    style={'font-size': format_style('font_size')}
                                )
                            ],
                            style={
                                'width': '100%',
                                'display': 'inline-block',
                                'font-size': format_style('font_size')
                            }
                        )
                    ),
                ]
            ),
            html.Hr(),
            #dbc.Row(
            #    [
            #        html.Label(i18n.t('app.widget_dresp.display')),
            #        html.Div(
            #            info_button(
            #                {"type":'help_pair', "index":index},
            #                i18n.t('app.widget_dresp.button_body')
            #            )
            #        ),
            #    ]
            #),
            dbc.Row([
                dbc.Col(
                    [
                        html.Div(
                            [
                                html.Label(i18n.t('app.widget_dresp.menu3')),
                                dcc.Dropdown(
                                    id={"type":'drug1_dd_cdr', "index":index},
                                    style={'font-size': format_style('font_size')}
                                )
                            ],
                            style={
                                'width': '100%',
                                'display': 'inline-block',
                                'font-size': format_style('font_size')
                            }
                        )
                    ],
                    width=2
                ),
                dbc.Col(
                    [
                        html.Div(
                            [
                                html.Label(i18n.t('app.widget_dresp.menu4')),
                                dcc.Dropdown(
                                    id={"type":'drug2_dd_cdr', "index":index},
                                    style={
                                        'font-size': format_style('font_size')
                                    }
                                )
                            ],
                            style={
                                'width': '100%',
                                'display': 'inline-block',
                                'font-size': format_style('font_size')
                            }
                        ),
                    ],
                    width=2
                ),
            ]),
            html.Div(
                info_button(
                    'help_plot',
                    i18n.t('app.widget_dresp.button_body2')
                ),
                style={'textAlign': 'right'}
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Loading(
                            id={"type":'pairwise', "index":index},
                            type="default",
                            children=html.Div()
                        )
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Loading(
                            id={"type":'drug1_box', "index":index},
                            type="default",
                            children=html.Div()
                        )
                    ),
                    dbc.Col(
                        dcc.Loading(
                            id={"type":'drug2_box', "index":index},
                            type="default",
                            children=html.Div()
                        )
                    ),
                ]
            )
        ],
        style={'fontFamily': format_style('font')}
    )

@app.callback(
    [Output({"type":'dresp_dd_cdr', "index":MATCH}, 'options'), Output({"type":'dresp_dd_cdr', "index":MATCH}, 'value')],
    [Input({"type":'project_dd_cdr', "index":MATCH}, 'value')]
)
def set_project_dresp_selector(selected_project):
    print("Getting Dose response for %s" % (selected_project))
    if selected_project not in dresp_options:
        return [], ""
    out = [
        {'label': k, 'value': v}
        for k, v in dresp_options[selected_project].items()
    ]
    return out, out[0]['value']


@app.callback(
    [Output({"type":'drug1_dd_cdr', "index":MATCH}, 'options'), Output({"type":'drug1_dd_cdr', "index":MATCH}, 'value')],
    [Input({"type":'project_dd_cdr', "index":MATCH}, 'value')]
)
def set_project_compound1_selector(selected_project):
    out = [
        {'label': l, 'value': gid}
        for gid, l in sorted(
            cdr.get_project_drugs(selected_project).items(), key=lambda a: a[1]
        )
    ]
    return out, out[cdr.find_index(out)+1]['value']

@app.callback(
    [Output({"type":'drug2_dd_cdr', "index":MATCH}, 'options'), Output({"type":'drug2_dd_cdr', "index":MATCH}, 'value')],
    [Input({"type":'project_dd_cdr', "index":MATCH}, 'value')]
)
def set_project_compound2_selector(selected_project):
    out = [
        {'label': l, 'value': gid}
        for gid, l in sorted(
            cdr.get_project_drugs(selected_project).items(), key=lambda a: a[1]
        )
    ]
    return out, out[cdr.find_index(out)+1]['value']


@app.callback(
    Output({"type":'drug1_box', "index":MATCH}, 'children'),
    [Input({"type":'drug1_dd_cdr', "index":MATCH}, 'value')]
)
def render_callback(selected_drug):
    if selected_drug is None:
        return None
    q = G.query().V(selected_drug).render(
        ['_data.name', '_gid']
    )
    for row in q:
        print('search result from %s: %s' % (selected_drug, row))
        name = row[1]
        if row[0] is not None:
            name = row[0]
        header = name.upper() + ' (' + row[1] + ')'
        descrip = "N/A" #row[2]
    fig = dbc.Card(
        dbc.CardBody(
            [
                html.H4(
                    header,
                    className="card-title",
                    style={
                        'fontFamily': format_style('font'),
                        'font-size': format_style('font_size_lg'),
                        'fontWeight': 'bold'
                    }
                ),
                html.P(
                    descrip,
                    style={
                        'fontFamily': format_style('font'),
                        'font-size': '12px'
                    }
                )
            ]),
        color="info",
        inverse=True,
        style={
            'Align': 'center',
            'width': '98%',
            'fontFamily': format_style('font')
        }
    )
    return fig


@app.callback(
    Output({"type":'drug2_box', "index":MATCH}, 'children'),
    [Input({"type":'drug2_dd_cdr', "index":MATCH}, 'value')]
)
def render_drug2_box(selected_drug):
    if selected_drug is None:
        return None
    q = G.query().V(selected_drug).render(
        ['_data.name', '_gid']
    )
    for row in q:
        print('search result from %s: %s' % (selected_drug, row))
        if row[0] is not None:
            header = row[0].upper() + ' (' + row[1] + ')'
        else:
            header = row[1].upper()
        descrip = "N/A" #row[2]
    fig = dbc.Card(
        dbc.CardBody(
            [
                html.H4(
                    header,
                    className="card-title",
                    style={
                        'fontFamily': format_style('font'),
                        'font-size': format_style('font_size_lg'),
                        'fontWeight': 'bold'
                    }
                ),
                html.P(
                    descrip,
                    style={
                        'fontFamily': format_style('font'),
                        'font-size': '12px'
                    }
                )
            ]
        ),
        color="info",
        inverse=True,
        style={
            'Align': 'center',
            'width': '98%',
            'fontFamily': format_style('font')
        }
    )
    return fig,


@app.callback(
    Output({"type":'pairwise', "index":MATCH}, "children"),
    [
        Input({"type":'project_dd_cdr', "index":MATCH}, 'value'),
        Input({"type":'drug1_dd_cdr', "index":MATCH}, 'value'),
        Input({"type":'drug2_dd_cdr', "index":MATCH}, 'value'),
        Input({"type":'dresp_dd_cdr', "index":MATCH}, 'value')
    ]
)
def render_comparison_graph(project, compound1, compound2, selected_dresp):
    '''create pairwise plots '''
    app.logger.info(
        "Rendering %s %s %s %s",
        project,
        compound1,
        compound2,
        selected_dresp
    )

    aliquot_disease = cdr.get_project_aliquot_disease(project)

    cmpd1 = cdr.get_project_compound_dr(project, compound1, selected_dresp)
    cmpd2 = cdr.get_project_compound_dr(project, compound2, selected_dresp)

    a = pd.Series(aliquot_disease).rename("disease")
    df = pd.DataFrame(
        {compound1: cmpd1, compound2: cmpd2, "disease": a}
    ).dropna()
    fig = px.scatter(x=df[compound1], y=df[compound2], color=df["disease"])
    fig.update_layout(xaxis_title='Compound 1', yaxis_title='Compound 2')
    return dcc.Graph(figure=fig)


@app.callback(
    Output({"type":'help_violin', "index":MATCH}, "is_open"),
    [Input({"type":'help_violin-target', "index":MATCH}, "n_clicks")],
    [State({"type":'help_violin', "index":MATCH}, "is_open")],
)
def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output({"type":'main_help1', "index":MATCH}, "is_open"),
    [Input({"type":'open1', "index":MATCH}, "n_clicks"), Input({"type":'close1', "index":MATCH}, "n_clicks")],
    [State({"type":'main_help1', "index":MATCH}, "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

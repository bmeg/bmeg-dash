from .. import appLayout as ly
from ..app import app
from ..components import compare_dresp_component as cdr
from ..db import G
from ..components import info_button
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_table
import gripql
import json
import pandas as pd
import plotly.express as px
import i18n
i18n.load_path.append('bmeg_app/locales/')

#######
# Prep
#######
main_colors= ly.main_colors
styles=ly.styles

project_dresp = {
    'Project:CCLE' : {
        'AAC':'aac',
        'EC50': 'ec50',
        'IC50': 'ic50'
    },
    'Project:GDSC' : {
        'AAC':'aac',
        'EC50': 'ec50',
        'IC50':'ic50'
    },
    'Project:CTRP' : {
        'AAC':'aac',
        'EC50': 'ec50'
     }
}


drug_response_projects = {
    "Project:CCLE" : "CCLE",
    "Project:CTRP" : "CTRP",
    "Project:GDSC" : "GDSC"
}
#######
# Page
#######
print('loading app layout')
NAME = i18n.t('app.config.tabname_widget_dresp')
LAYOUT = html.Div(children=[
    dbc.Row(
        [
            dbc.Col(
                html.Div([
                    html.Label(i18n.t('app.widget_dresp.menu1')),
                    dcc.Dropdown(id='project_dd_cdr',options=[{'label': l, 'value': gid} for gid,l in drug_response_projects.items()],value='Project:CCLE')
                ],
                style={'width': '100%', 'display': 'inline-block','font-size' : styles['t']['size_font']})
            ),
            dbc.Col(
                html.Div([
                    html.Label(i18n.t('app.widget_dresp.menu2')),
                    dcc.Dropdown(id='dresp_dd_cdr',style={'font-size' : styles['t']['size_font']})
                ],
                style={'width': '100%', 'display': 'inline-block','font-size' : styles['t']['size_font']})
            ),
        ]
    ),

    html.Hr(),
    dbc.Row(
        [
            html.Label(i18n.t('app.widget_dresp.display')),
            html.Div(info_button('help_pair',i18n.t('app.widget_dresp.button_body'))),
        ]
    ),
    # html.Div(id='hidden_base_df_cdr', style={'display': 'none'}),
    dbc.Row([
        dbc.Col([
            html.Div(
                [
                    html.Label(i18n.t('app.widget_dresp.menu2')),
                    dcc.Dropdown(id='drug_dd_cdr', style={'font-size' : styles['t']['size_font']})
                ],
                style={'width': '100%', 'display': 'inline-block','font-size' : styles['t']['size_font']}
            )
        ],width=2),
        dbc.Col([
            html.Div(
                [
                    html.Label(i18n.t('app.widget_dresp.menu4')),
                    dcc.Dropdown(id='drug2_dd_cdr',style={'font-size' : styles['t']['size_font']})
                ],
                style={'width': '100%', 'display': 'inline-block','font-size' : styles['t']['size_font']}
            ),
        ],width=2),
    ]),
    dbc.Row([
        dbc.Col(dcc.Loading(id="pairwise",type="default",children=html.Div())),
    ]),
    dbc.Row([
        dbc.Col(dcc.Loading(id="drug1_box",type="default",children=html.Div())),
        dbc.Col(dcc.Loading(id="drug2_box",type="default",children=html.Div())),
    ])
],style={'fontFamily': styles['t']['type_font']})

app.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks > 0)
            document.querySelector("#export_sample_table button.export").click()
        return ""
    }
    """,
    Output("export_button_sample", "data-dummy"),
    [Input("export_button_sample", "n_clicks")]
)

@app.callback(
    [Output('dresp_dd_cdr', 'options'), Output('dresp_dd_cdr', 'value')],
    [Input('project_dd_cdr', 'value')]
)
def set_project_dresp_selector(selected_project):
    out = [{'label': k, 'value': v} for k,v in project_dresp[selected_project].items()]
    return out, out[0]['value']

@app.callback(
    [Output('drug_dd_cdr', 'options'),Output('drug_dd_cdr', 'value')],
    [Input('project_dd_cdr', 'value')]
)
def set_project_compound1_selector(selected_project):
    out = [{'label': l, 'value': gid} for gid,l in sorted(cdr.get_project_drugs(selected_project).items(), key=lambda a: a[1])]
    return out, out[0]['value']

@app.callback(
    [Output('drug2_dd_cdr', 'options'), Output('drug2_dd_cdr', 'value')],
    [Input('project_dd_cdr', 'value')]
)
def set_project_compound2_selector(selected_project):
    out = [{'label': l, 'value': gid} for gid,l in sorted(cdr.get_project_drugs(selected_project).items(), key=lambda a: a[1])]
    i = 1 if len(out) > 1 else 0
    return out, out[i]['value']

@app.callback(
    Output('drug1_box', 'children'),
    [Input('drug_dd_cdr', 'value')]
)
def render_callback(selected_drug):
    q=G.query().V(selected_drug).render(['_data.synonym','_data.pubchem_id','_data.taxonomy.description'])
    for row in q:
        print('starting search')
        header = row[0].upper() + ' ('+ row[1]+')'
        descrip = row[2]
    fig = dbc.Card(
        dbc.CardBody(
            [
            html.H4(header, className="card-title",style={'fontFamily':styles['t']['type_font'],'font-size' : styles['t']['size_font_card'], 'fontWeight':'bold'}),
            html.P(descrip,style={'fontFamily':styles['t']['type_font'],'font-size' : '12px'})
            ]),
        color="info", inverse=True,style={'Align': 'center', 'width':'98%','fontFamily':styles['t']['type_font']})
    return fig

@app.callback(
    Output('drug2_box', 'children'),
    [Input('drug2_dd_cdr', 'value')]
)
def render_callback(selected_drug):
    q=G.query().V(selected_drug).render(['_data.synonym','_data.pubchem_id','_data.taxonomy.description'])
    for row in q:
        print('starting search')
        header = row[0].upper() + ' ('+ row[1]+')'
        descrip = row[2]
    fig = dbc.Card(
        dbc.CardBody(
            [
            html.H4(header, className="card-title",style={'fontFamily':styles['t']['type_font'],'font-size' : styles['t']['size_font_card'], 'fontWeight':'bold'}),
            html.P(descrip,style={'fontFamily':styles['t']['type_font'],'font-size' : '12px'})
            ]),
        color="info", inverse=True,style={'Align': 'center', 'width':'98%','fontFamily':styles['t']['type_font']})
    return fig,

@app.callback(
    Output("pairwise", "children"),
    [Input('project_dd_cdr', 'value'),
    Input('drug_dd_cdr', 'value'),
    Input('drug2_dd_cdr', 'value'),
    Input('dresp_dd_cdr', 'value')]
)
def render_comparison_graph(project, compound1, compound2, selected_dresp):
    '''create pairwise plots '''
    app.logger.info("Rendering %s %s %s %s", project, compound1, compound2, selected_dresp)

    aliquot_disease = cdr.get_project_aliquot_disease(project)

    cmpd1 = cdr.get_project_compound_dr(project, compound1, selected_dresp)
    cmpd2 = cdr.get_project_compound_dr(project, compound2, selected_dresp)

    a = pd.Series(aliquot_disease).rename("disease")
    df = pd.DataFrame({compound1:cmpd1, compound2:cmpd2, "disease":a}).dropna()
    fig = px.scatter(x=df[compound1], y=df[compound2], color=df["disease"])
    return dcc.Graph(figure=fig)

@app.callback(
    Output("help_violin", "is_open"),
    [Input("help_violin-target", "n_clicks")],
    [State("help_violin", "is_open")],
)
def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("main_help1", "is_open"),
    [Input("open1", "n_clicks"), Input("close1", "n_clicks")],
    [State("main_help1", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

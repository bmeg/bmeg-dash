from bmeg_app.app import app
import bmeg_app.appLayout as ly
from bmeg_app.views import home_view, tumor_match_normal_view, literature_support_view, compare_dresp_view
import base64
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_html_components as html
import gripql
import yaml

#######
# Prep
#######
styles=ly.styles
image_filename = 'bmeg_app/images/bmeg_logo.png' 
encoded_image3 = base64.b64encode(open(image_filename, 'rb').read())

#######
# Page  
#######
navlink_cancer_screen=dbc.NavLink(
    "Cancer Drug Screening", href="/page-2", id="page-2-link",
    style={'font-size':styles['t']['size_font_card'],'fontFamily':styles['t']['type_font']}
)
 
help_cancer_screen= html.Div([
    dbc.Button('?', id='open1',color='link',style=styles['tab_help_button']),
    dbc.Modal(
        [
            dbc.ModalHeader('Identify Drug Treatment Candidates from Cancer Cell Line Drug Screens'),
            
            dbc.ModalBody("Interrogate cell line drug screening trials from large established sources (CCLE, CTRP, GDSC). Dig into drug sensitivity trends within a particular disease and explore associated metadata."),
            dbc.ModalBody( 'What’s going on behind the scenes?'),
            dbc.ModalBody( '•	Data is queried from BMEG, filtered for relevant cell lines (breast tissue derived cell lines kept if breast cancer is selected), and analyzed in the viewer.'),
            dbc.ModalBody( 'Panel 1 Features'),
            dbc.ModalBody( '• Download a table of all cell line drug screening results based on three dropdown menus. Quickly see metadata composition of the table from the pie charts.'),
            dbc.ModalBody( 'Panel 2 Features'),
            dbc.ModalBody( '• Dive deeper to explore underlying trends between two drugs. Drug response values are plotted to quickly identify potential drug candidates that elicted similar responses from cell lines.'),
            dbc.ModalBody( '• Blue cards provide a summary of the selected drugs to provide insight on the molecular and/or biological realm of the selected drug.'),
            dbc.ModalBody( '• Examine the drug characteristics table for potential taxonomic reasons for similar and different responses from drugs.'),
            dbc.ModalFooter(dbc.Button('Close',id='close1',className='ml-auto')),
        ],
        id='main_help1',
        size='lg',
        centered=True,
    ),
])

sidebar_header = dbc.Row(
    [
        dbc.Col(
            html.Div(html.Img(src='data:image/png;base64,{}'.format(encoded_image3.decode()),
                style={'height':'85%','width':'85%', 'marginTop': 0, 'marginBottom':0}),
            ),
            className="display-4"),
        dbc.Col(
            [
                html.Button(
                    html.Span(className="navbar-toggler-icon"),
                    className="navbar-toggler",
                    style={
                        "color": "rgba(0,0,0,.5)",
                        "border-color": "rgba(0,0,0,.1)",
                    },
                    id="navbar-toggle",
                ),
                html.Button(
                    html.Span(className="navbar-toggler-icon"),
                    className="navbar-toggler",
                    style={
                        "color": "rgba(0,0,0,.5)",
                        "border-color": "rgba(0,0,0,.1)",
                    },
                    id="sidebar-toggle",
                ),
            ],
            width="auto",
            align="center",
        ),
    ]
)

sidebar = html.Div(
    [
        sidebar_header,
        html.Div(
            [
                html.Hr(),
                html.P(
                    "A graph database for "
                    "merging and analyzing connected data",
                    className="lead",
                    style={'font-size':styles['t']['size_font_card'],'fontFamily':styles['t']['type_font']},
                ),
            ],
            id="blurb",
        ),
        dbc.Collapse(
            dbc.Nav(
                [
                    dbc.NavLink("Home", href="/page-1", id="page-1-link",
                        style={'font-size':styles['t']['size_font_card'],
                        'fontFamily':styles['t']['type_font']
                        },),
                    dbc.Row(
                        [
                            dbc.Col(navlink_cancer_screen,width=10),
                            dbc.Col(help_cancer_screen,width=2),
                        ]
                    ),
                    dbc.NavLink("TCGA Clustering", href="/page-3", id="page-3-link",
                        style={'font-size':styles['t']['size_font_card'],
                        'fontFamily':styles['t']['type_font']
                        },),
                    dbc.NavLink("Literature Gene-Drug Associations", href="/page-4", id="page-4-link",
                        style={'font-size':styles['t']['size_font_card'],
                        'fontFamily':styles['t']['type_font']
                        },),
                ],
                vertical=True,
                pills=True,
            ),
            id="collapse",
        ),
    ],
    id="sidebar",
)
content = html.Div(id="page-content")
app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


@app.callback(
    [Output(f"page-{i}-link", "active") for i in range(1, 5)],
    [Input("url", "pathname")],
)
def toggle_active_links(pathname):
    '''active link for widget view'''
    if pathname == "/":
        return True, False, False, False
    return [pathname == f"/page-{i}" for i in range(1, 5)]

@app.callback(
    Output("page-content", "children"), 
    [Input("url", "pathname")]
)
def render_page_content(pathname):
    '''render selected widget view'''
    if pathname in ["/", "/page-1"]:
        return html.Div([home_view.tab_layout])
    elif pathname == "/page-2":
        return html.Div([compare_dresp_view.tab_layout]) 
    elif pathname == "/page-3":
        return html.Div([tumor_match_normal_view.tab_layout])    
    elif pathname == "/page-4":
        return html.Div([literature_support_view.tab_layout]) 

    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )

@app.callback(
    Output("sidebar", "className"),
    [Input("sidebar-toggle", "n_clicks")],
    [State("sidebar", "className")]
)
def toggle_classname(n, classname):
    '''Side menu state'''
    if n and classname == "":
        return "collapsed"
    return ""

@app.callback(
    Output("collapse", "is_open"),
    [Input("navbar-toggle", "n_clicks")],
    [State("collapse", "is_open")]
)
def toggle_collapse(n, is_open):
    '''Side menu'''
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
    
with open('bmeg_app/config.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
if __name__ == '__main__':
    app.run_server(host=config['app']['host'], debug=config['app']['dev'], port=config['app']['port'])

from bmeg_app.app import app
import bmeg_app.appLayout as ly
from bmeg_app.views import data_types_view, tumor_match_normal_view, literature_support_view, compare_trt_view
import base64
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

# Layout 
styles=ly.styles

# Images
image_filename = 'bmeg_app/images/bmeg_logo.png' 
encoded_image3 = base64.b64encode(open(image_filename, 'rb').read())
 
 
# we use the Row and Col components to construct the sidebar header
# it consists of a title, and a toggle, the latter is hidden on large screens
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
                    # use the Bootstrap navbar-toggler classes to style
                    html.Span(className="navbar-toggler-icon"),
                    className="navbar-toggler",
                    # the navbar-toggler classes don't set color
                    style={
                        "color": "rgba(0,0,0,.5)",
                        "border-color": "rgba(0,0,0,.1)",
                    },
                    id="navbar-toggle",
                ),
                html.Button(
                    # use the Bootstrap navbar-toggler classes to style
                    html.Span(className="navbar-toggler-icon"),
                    className="navbar-toggler",
                    # the navbar-toggler classes don't set color
                    style={
                        "color": "rgba(0,0,0,.5)",
                        "border-color": "rgba(0,0,0,.1)",
                    },
                    id="sidebar-toggle",
                ),
            ],
            # the column containing the toggle will be only as wide as the
            # toggle, resulting in the toggle being right aligned
            width="auto",
            # vertically align the toggle in the center
            align="center",
        ),
    ]
)

sidebar = html.Div(
    [
        sidebar_header,
        # we wrap the horizontal rule and short blurb in a div that can be
        # hidden on a small screen
        html.Div(
            [
                html.Hr(),
                html.P(
                    "A graph database for "
                    "merging and analyzing connected data",
                    className="lead",
                    style={'font-size':styles['textStyles']['size_font_card'],'fontFamily':styles['textStyles']['type_font']},
                ),
            ],
            id="blurb",
        ),
        # use the Collapse component to animate hiding / revealing links
        dbc.Collapse(
            dbc.Nav(
                [
                    dbc.NavLink("Compare Drug Treatments", href="/page-1", id="page-1-link",
                        style={'font-size':styles['textStyles']['size_font_card'],
                        'fontFamily':styles['textStyles']['type_font']
                        },),
                    dbc.NavLink("TCGA Clustering", href="/page-2", id="page-2-link",
                        style={'font-size':styles['textStyles']['size_font_card'],
                        'fontFamily':styles['textStyles']['type_font']
                        },),
                    dbc.NavLink("Literature Gene-Drug Associations", href="/page-3", id="page-3-link",
                        style={'font-size':styles['textStyles']['size_font_card'],
                        'fontFamily':styles['textStyles']['type_font']
                        },),
                    dbc.NavLink("BMEG Data Types", href="/page-4", id="page-4-link",
                        style={'font-size':styles['textStyles']['size_font_card'],
                        'fontFamily':styles['textStyles']['type_font']
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


# this callback uses the current pathname to set the active state of the
# corresponding nav link to true, allowing users to tell see page they are on
@app.callback(
    [Output(f"page-{i}-link", "active") for i in range(1, 5)],
    [Input("url", "pathname")],
)
def toggle_active_links(pathname):
    if pathname == "/":
        # Treat Drug Repurposing as the homepage / index
        return True, False, False, False
    return [pathname == f"/page-{i}" for i in range(1, 5)]


@app.callback(Output("page-content", "children"), 
    [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/", "/page-1"]:
        return html.Div([compare_trt_view.tab_layout]) 
    elif pathname == "/page-2":
        return html.Div([tumor_match_normal_view.tab_layout])    
    elif pathname == "/page-3":
        return html.Div([literature_support_view.tab_layout]) 
    elif pathname == "/page-4":
        return html.Div([data_types_view.tab_layout])
    # If the user tries to reach a different page, return a 404 message
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
    [State("sidebar", "className")],
)
def toggle_classname(n, classname):
    if n and classname == "":
        return "collapsed"
    return ""


@app.callback(
    Output("collapse", "is_open"),
    [Input("navbar-toggle", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True, port=80)

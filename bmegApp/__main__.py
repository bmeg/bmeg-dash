from .app import app
from . import config
from .style import format_style
from .views import view_map, create_window
import base64
import json
import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash.dependencies import Input, Output, State, ALL
from dash import html
import yaml
import os
import i18n


#######
# Page
#######

sidebar_header = dbc.Row(
    [
        dbc.Col(
            html.Div(
                html.Img(
                    src='data:image/png;base64,{}'.format(
                        config.LOGO_IMAGE.decode()
                        ), style={
                        'height': '85%',
                        'width': '85%',
                        'marginTop': 0,
                        'marginBottom': 0
                        }
                )
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


def genNavBarList():
    i = 0
    out = []
    for k, v in view_map.items():
        e = dbc.NavLink(
            v.NAME,
            href="/%s" % (k),
            id="page-%d-link" % (i),
            style={
                'font-size': format_style('font_size_lg'),
                'fontFamily': format_style('font')
            }
        )
        out.append(e)
        i += 1
    return out


sidebar = html.Div(
    [
        sidebar_header,
        html.Div(
            [
                html.Hr(),
                html.P(
                    i18n.t('app.config.tab_title'),
                    className="lead",
                    style={
                        'font-size': format_style('font_size_lg'),
                        'fontFamily': format_style('font')
                    },
                ),
            ],
            id="blurb",
        ),
        dbc.Collapse(
            dbc.Nav(
                genNavBarList(),
                vertical=True,
                pills=True,
            ),
            id="collapse",
        ),
    ],
    id="sidebar",
)


@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def render_page_content(pathname):
    '''render selected widget view'''
    if pathname == "/" + config.CONFIG[config.STAGE]['basepath'] + "/":
        pathname = "/" + list(view_map.keys())[0]
    print(pathname[1:], view_map)
    if pathname[1:] in view_map:
        return html.Div(view_map[pathname[1:]].CREATE(0))
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


if __name__ == '__main__':
    content = html.Div(id="page-content")
    app.layout = html.Div([dcc.Location(id="url"), sidebar, content])
    app.run_server(
        host=config.CONFIG[config.STAGE]['host'],
        debug=config.CONFIG[config.STAGE]['dev'],
        port=config.CONFIG[config.STAGE]['port']
    )

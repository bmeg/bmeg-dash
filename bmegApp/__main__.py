from .app import app
from . import config
from .style import format_style
from .views import view_map, create_window
import base64
import json
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Input, Output, State, ALL
import dash_html_components as html
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
        e = dbc.Button(
            v.NAME,
            id={"type" : "new-button", "index":k}
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
    Output('page-content', 'children'),
    [Input({'type': 'new-button', 'index': ALL}, 'n_clicks'), Input({'type':'close-button', 'index':ALL}, 'n_clicks')],
    [State('page-content', 'children')])
def update_output(n_clicks, close_clicks, content):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'No clicks yet'
        return [ ]
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        d = json.loads(button_id)
        print(button_id)
        if d['type'] == "new-button":
            n = d['index']
            if n in view_map:
                print("Creating: %s" % (n))
                clicks = sum( a for a in n_clicks if a is not None )
                content = [ create_window(n, clicks) ] + content
        elif d['type'] == "close-button":
            print("Close ", d['index'])
            o = []
            for c in content:
                if c['props']['id']['index'] != d['index']:
                    o.append(c)
            content = o
    return content


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

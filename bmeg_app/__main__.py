from bmeg_app.app import app
from bmeg_app.style import format_style
from bmeg_app.views import view_map
import base64
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_html_components as html
import yaml
import i18n
i18n.load_path.append('bmeg_app/locales/')

#######
# Prep
#######
image_filename = 'bmeg_app/images/bmeg_logo.png'
encoded_image3 = base64.b64encode(open(image_filename, 'rb').read())

#######
# Page
#######

sidebar_header = dbc.Row(
    [
        dbc.Col(
            html.Div(
                html.Img(
                    src='data:image/png;base64,{}'.format(
                        encoded_image3.decode()
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
content = html.Div(id="page-content")
app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


@app.callback(
    [Output(f"page-{i[0]}-link", "active") for i in enumerate(view_map)],
    [Input("url", "pathname")],
)
def toggle_active_links(pathname):
    '''active link for widget view'''
    if pathname is None:
        return [True] + [False] * (len(view_map)-1)
    return [pathname == f"/{i}" for i in view_map.keys()]


@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def render_page_content(pathname):
    '''render selected widget view'''
    if pathname == "/":
        pathname = "/" + list(view_map.keys())[0]
    if pathname[1:] in view_map:
        return html.Div(view_map[pathname[1:]].LAYOUT)
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


with open('bmeg_app/config.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
if __name__ == '__main__':
    app.run_server(
        host=config['app']['host'],
        debug=config['app']['dev'],
        port=config['app']['port']
    )

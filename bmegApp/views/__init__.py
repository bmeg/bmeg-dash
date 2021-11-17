
from ..app import app
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc

from collections import OrderedDict
import yaml
from . import home_view, \
    rna_umap_view, \
    literature_support_view, \
    compare_dresp_view, \
    mutation_view, pathway_view

# # Each submodule is imported an a single entity and mapped into 'view_map'
# # The view_map key is the url page (with "/" defaulting to the first element)
# # Every view module is expected to define the following variables

# # - NAME : string name that is displayed in the menu
# # - LAYOUT : a Dash component for the view

view_map = OrderedDict([
    ("", home_view),
    ("rna_umap", rna_umap_view),
    ("g2p", literature_support_view),
    ("drug_response", compare_dresp_view),
    ("mutations", mutation_view),
    ("pathway", pathway_view)
])


def create_window(name, index):
    print("Creating Window", name, index)
    return dbc.Card([
        dbc.CardHeader(html.Div([dbc.Button("X", id={"type":"close-button", "index":index}), html.Span(view_map[name].NAME, style={"text-align":"center"})])),
        dbc.CardBody([
            html.Div(
                children=[view_map[name].CREATE(index)],
                #style={'border': '1px solid'}
            )
        ],
        )
    ],
    id={"type":"view_window", "index": index},
    )

from collections import OrderedDict
from . import home_view, tumor_match_normal_view, literature_support_view, compare_dresp_view #, mutation_view, pathway_view

## Each submodule is imported an a single entity and mapped into 'view_map'
## The view_map key is the url page (with "/" defaulting to the first element)
## Every view module is expected to define the following variables

## - NAME : string name that is displayed in the menu
## - LAYOUT : a Dash component for the view

view_map = OrderedDict([
    ("home", home_view),
    ("tumors", tumor_match_normal_view),
    ("g2p", literature_support_view),
    ("drug_response", compare_dresp_view),
    # ("oncoprint", mutation_view),
    # ("pathway", pathway_view)
])

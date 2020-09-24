
from collections import OrderedDict
from . import home_view, tumor_match_normal_view, literature_support_view, compare_dresp_view, mutation_view, pathway_view

view_map = OrderedDict([
    ("home", home_view),
    ("tumors", tumor_match_normal_view),
    ("g2p", literature_support_view),
    ("drug_response", compare_dresp_view),
    ("oncoprint", mutation_view),
    ("pathway", pathway_view)
])

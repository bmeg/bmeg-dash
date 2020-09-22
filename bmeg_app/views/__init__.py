
from collections import OrderedDict
from . import data_types_view, tumor_match_normal_view, literature_support_view, compare_dresp_view

view_map = OrderedDict([
    ("data", data_types_view),
    ("tumors", tumor_match_normal_view),
    ("g2p", literature_support_view),
    ("drug_response", compare_dresp_view)
])

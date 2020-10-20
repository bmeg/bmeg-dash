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

with open('bmeg_app/config.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
path_name = config['DEV']['basepath']

view_map = OrderedDict([
    (path_name, home_view),
    (path_name + "/rna_umap", rna_umap_view),
    (path_name + "/g2p", literature_support_view),
    (path_name + "/drug_response", compare_dresp_view),
    (path_name + "/oncoprint", mutation_view),
    (path_name + "/pathway", pathway_view)
])

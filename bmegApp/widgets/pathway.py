from ..app import app
from ..components import info_button
from ..db import G
from ..style import format_style
import dash
from dash import dcc
from dash.exceptions import PreventUpdate
from dash import html
import dash_cytoscape as cyto
import logging
import i18n
from dash.dependencies import Input, Output, MATCH
logger = logging.getLogger(__name__)
i18n.load_path.append('bmeg_app/locales/')

#######
# Prep
#######
pathwayList = []
for row in G.query().V().hasLabel("Pathway").render(["$._gid", "$.name"]):
    pathwayList.append([row[0], row[1].lower()])


def getPathwayGraph(pathway):
    q = G.query().V(pathway).out("interactions").as_("i")
    q = q.in_("interaction_input").as_("in").select("i")
    q = q.out("interaction_output").as_("out").select("o")
    q = q.render(["$in._gid", "$i._gid", "$out._gid"])

    nodes = set()
    data = []
    for src, inter, dst in q:
        if src not in nodes:
            data.append({"data": {"id": src, "label": src}})
        if dst not in nodes:
            data.append({"data": {"id": dst, "label": dst}})
        data.append({"data": {"source": src, "target": dst}})
    return data

def CREATE(index):

    element = cyto.Cytoscape(
        id={"type":'bmeg-cytoscape', "index":index},
        layout={'name': 'cose'},
        style={
            'width': '100%',
            'height': '400px',
            'arrow-scale': 2,
            'target-arrow-shape': 'vee'
        },
        elements=[]
    )
    return html.Div(
        children=[
            html.Label(i18n.t('app.widget_pathway.menu1')),
            dcc.Dropdown(id={"type":'pathway-dropdown', "index":index},
                            value="pathwaycommons.org/pc11/" +
                            "Pathway_2d307e80e3a7b4ae590fcd73c4d058cf",
                            search_value="mtor signaling pathway"),
            html.Hr(),
            html.Div(
                info_button(
                    'help_pathway',
                    i18n.t('app.widget_pathway.button_body')
                )
            ),
            element,
            html.Div(id={"type":'bmeg-cytoscape-gene', "index":index})
        ],
        style={
            'font-size': format_style('font_size'),
            'fontFamily': format_style('font')
        }
    )


@app.callback(
    Output({"type":'pathway-dropdown', "index":MATCH}, 'options'),
    [Input({"type":'pathway-dropdown', "index":MATCH}, 'search_value')]
)
def update_options(search_value):
    """Lookup the search value in elastic."""
    if not search_value:
        raise PreventUpdate
    hits = []
    for g, n in pathwayList:
        if search_value in n:
            hits.append({"label": n, "value": g})
    return hits


@app.callback(
    Output({"type":'bmeg-cytoscape', "index":MATCH}, 'elements'),
    [Input({"type":'pathway-dropdown', "index":MATCH}, 'value')]
)
def update_pathway(value):
    app.logger.info("Getting pathway: %s" % (value))
    out = getPathwayGraph(value)
    app.logger.info("%s has %d elements" % (value, len(out)))
    return out

@app.callback(Output({"type":'bmeg-cytoscape-gene', "index":MATCH}, 'children'),
              Input({"type":'bmeg-cytoscape', "index":MATCH}, 'tapNodeData'))
def displayTapNodeData(data):
    return str(data)

from ..app import app
from ..components import info_button
from ..db import G, gene_search
from ..style import format_style
import dash
import dash_core_components as dcc
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, MATCH
import dash_html_components as html
import dash_bio
import json
import pandas as pd
import logging
import i18n
logger = logging.getLogger(__name__)
i18n.load_path.append('bmeg_app/locales/')

#######
# Prep
#######


def getGeneMutations(gene):
    app.logger.info("Updating mutation Track")
    res = G.query().V(gene).out("alleles").as_("a") \
        .outE("somatic_callsets").as_("c") \
        .render(["$a.ensembl_transcript", "$a.cds_position", "$c._to"])
    o = []
    t = []
    for transcript, cds, dst in res:
        v = cds.split("/")[0]
        try:
            d = int(v)
            o.append(d)
        except ValueError:
            pass
        t.append(transcript)
    logger.info("Transcript %s" % (set(t)))
    df = pd.Series(o)
    counts = df.value_counts()
    mData = {
        "x": list("%d.0" % (i) for i in counts.index),
        "y": list("%d" % (i) for i in counts.values)
    }
    return mData



#######
# Page
#######


def CREATE(index):

    component = dash_bio.NeedlePlot(
      id={"type": 'mutation-dashbio-needleplot', "index":index},
      mutationData={},
      needleStyle={
            'stemColor': '#FF8888',
            'stemThickness': 2,
            # 'stemConstHeight': True,
            'headSize': 10,
            'headColor': ['#FFDD00', '#000000']
      }
    )
    return html.Div(
        children=[
            html.Label(
                i18n.t('app.widget_gmut.menu1')
            ),
            dcc.Dropdown(
                id={"type" : "mutation-single-dropdown", "index":index},
                value="TP53/ENSG00000141510",
                search_value="TP53/ENSG00000141510"
            ),
            html.Hr(),
            html.Div(
                info_button(
                    'help_genemutation',
                    i18n.t('app.widget_gmut.button_body')
                )
            ),
            component,
            html.Div(id={"type": 'mutation-needle-selection', "index":index})
        ],
        style={
            'font-size': format_style('font_size'),
            'fontFamily': format_style('font')
        }
    )


@app.callback(
    dash.dependencies.Output({"type" : "mutation-single-dropdown", "index":MATCH}, 'options'),
    [dash.dependencies.Input({"type" : "mutation-single-dropdown", "index":MATCH}, 'search_value')]
)
def update_options(search_value):
    """Lookup the search value in elastic."""
    if not search_value:
        raise PreventUpdate
    genes = gene_search(search_value)
    return genes


@app.callback(
    dash.dependencies.Output({"type": 'mutation-dashbio-needleplot', "index":MATCH}, 'mutationData'),
    [dash.dependencies.Input({"type" : "mutation-single-dropdown", "index":MATCH}, 'value')])
def process_single(value):
    if not value:
        raise PreventUpdate
    gene = value.split("/")[1]
    app.logger.info("Getting: %s" % (gene))
    return getGeneMutations(gene)


#@app.callback(
#    Output('needle-selection', 'children'),
#    [Input('my-dashbio-needleplot', 'selectedData')])
#def display_selected_data(selectedData):
#    # This doesn't seem to respond so will probably delete
#    app.logger.info("Got selectedData")
#    return json.dumps(selectedData, indent=2)

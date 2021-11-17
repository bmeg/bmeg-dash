from ..app import app
from ..components import info_button
from ..db import G, gene_search
from ..style import format_style
import dash
from dash import dcc
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, MATCH
from dash import html
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


def CREATE(gene, index):
    geneSelect = None
    if gene is None:
        gene = "TP53"
    t = gene_search(gene)
    if len(t):
        geneSelect = t[0]['value']
    print("Select", geneSelect)
    component = dash_bio.NeedlePlot(
      id={"type": 'mutation-dashbio-needleplot', "index":index},
      mutationData={},
      needleStyle={
            'stemColor': '#FF8888',
            'stemThickness': 2,
            # 'stemConstHeight': True,
            'headSize': 10,
            'headColor': ['#FFDD00', '#000000']
      },
      rangeSlider=True
    )
    return html.Div(
        children=[
            html.Label(
                i18n.t('app.widget_gmut.menu1')
            ),
            dcc.Dropdown(
                id={"type" : "mutation-single-dropdown", "index":index},
                value=geneSelect,
                search_value=geneSelect,
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


@app.callback(
    Output({"type":'mutation-needle-selection', "index":MATCH}, 'children'),
    [Input({"type": 'mutation-dashbio-needleplot', "index":MATCH}, 'clickData')])
def display_selected_data(selectData):
    # This doesn't seem to respond so will probably delete
    app.logger.info("Got selectedData %s" % (selectData) )
    return json.dumps(selectData, indent=2)

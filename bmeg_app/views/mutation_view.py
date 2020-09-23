from .. import appLayout as ly
from ..app import app
from ..db import G
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_table
import dash_bio
import gripql
import json
import pandas as pd
from plotly.subplots import make_subplots

#######
# Prep
#######

main_colors= ly.main_colors
styles=ly.styles

cds = G.query().V("ENSG00000141510").out("alleles").render("cds_position").execute()
o = []
for i in cds:
    v = i.split("/")[0]
    try:
        d = int(v)
        o.append(d)
    except ValueError:
        pass
df = pd.Series(o)
counts = df.value_counts()
mData = {
    "x" : list("%d.0" % (i) for i in counts.index),
    "y" : list("%d" % (i) for i in counts.values)
}
#print(json.dumps(mData))

component = dash_bio.NeedlePlot(
  id='my-dashbio-needleplot',
  mutationData=mData,
  needleStyle={
        'stemColor': '#FF8888',
        'stemThickness': 2,
        #'stemConstHeight': True,
        'headSize': 10,
        'headColor': ['#FFDD00', '#000000']
  }
)


#######
# Page
#######
print('loading app layout')
NAME="OncoPrint"
tab_layout = html.Div(children=[
    html.Label('OncoPrint HERE!!!'),
    component
])

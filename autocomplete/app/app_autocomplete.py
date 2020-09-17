import dash
from dash.exceptions import PreventUpdate
import dash_html_components as html
import dash_core_components as dcc
from elastic import gene_search

import logging
logger = logging.getLogger('app')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([html.Label(['Single gene dynamic Dropdown',
                      dcc.Dropdown(id='my-dynamic-dropdown')]),
                      html.Label(['Multi gene dynamic Dropdown',
                      dcc.Dropdown(id='my-multi-dynamic-dropdown',
                      multi=True)])])


@app.callback(dash.dependencies.Output('my-dynamic-dropdown', 'options'
              ), [dash.dependencies.Input('my-dynamic-dropdown',
              'search_value')])
def update_options(search_value):
    logger.debug(search_value)
    if not search_value:
        raise PreventUpdate
    genes = gene_search(search_value)
    logger.debug(genes)
    return genes


@app.callback(dash.dependencies.Output('my-multi-dynamic-dropdown', 'options'),
              [dash.dependencies.Input('my-multi-dynamic-dropdown', 'search_value')],
              [dash.dependencies.State('my-multi-dynamic-dropdown', 'value')])
def update_multi_options(search_value, value):
    """See https://dash.plotly.com/dash-core-components/dropdown."""

    logger.debug(f'search_value:{search_value} value:{value}')
    if not search_value:
        raise PreventUpdate

    # Make sure that the set values are in the option list, else they will disappear
    # from the shown select list, but still part of the `value`.

    genes = gene_search(search_value) or []
    if genes and value:
        genes.extend([{'label': v, 'value': v} for v in value])
    logger.debug(genes)

    return genes

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')

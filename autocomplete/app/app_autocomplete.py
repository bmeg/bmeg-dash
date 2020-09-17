import dash
from dash.exceptions import PreventUpdate
import dash_html_components as html
import dash_core_components as dcc
import logging

import i18n
from i18n import t

# our elastic wrapper
from elastic import gene_search

# our example backend
from ensembl import fetch_phenotypes

# setup logger and translations
logger = logging.getLogger(__name__)
i18n.load_path.append('./assets/')

# configure dash app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    [
        html.H1(children=t('autocomplete.instructions')),
        html.Label([t('autocomplete.single'), dcc.Dropdown(id='single-dropdown')]),
        html.Button(t('autocomplete.process'), id='process-single', n_clicks=0),
        html.Div(id='process-single-output'),
        html.Label([t('autocomplete.multiple'), dcc.Dropdown(id='multi-dropdown', multi=True)]),
        html.Button(t('autocomplete.process'), id='process-multiple'),
        html.Div(id='process-multiple-output'),
    ]
)


@app.callback(
    dash.dependencies.Output('single-dropdown', 'options'),
    [dash.dependencies.Input('single-dropdown', 'search_value')]
)
def update_options(search_value):
    """Lookup the search value in elastic."""
    if not search_value:
        raise PreventUpdate
    genes = gene_search(search_value)
    return genes


@app.callback(
    dash.dependencies.Output('multi-dropdown', 'options'),
    [dash.dependencies.Input('multi-dropdown', 'search_value')],
    [dash.dependencies.State('multi-dropdown', 'value')]
)
def update_multi_options(search_value, value):
    """See https://dash.plotly.com/dash-core-components/dropdown."""

    # logger.debug(f'search_value:{search_value} value:{value}')
    if not search_value:
        raise PreventUpdate

    # Make sure that the set values are in the option list,
    #  else they will disappear from the shown select list,
    #  but still part of the `value`.

    genes = gene_search(search_value) or []
    if genes and value:
        genes.extend([{'label': v, 'value': v} for v in value])

    return genes


@app.callback(
    dash.dependencies.Output('process-single-output', 'children'),
    [dash.dependencies.Input('process-single', 'n_clicks')],
    [dash.dependencies.State('single-dropdown', 'value')])
def process_single(n_clicks, value):
    return f'The input value was "{value}", button was clicked {n_clicks}'


@app.callback(
    dash.dependencies.Output('process-multiple-output', 'children'),
    [dash.dependencies.Input('process-multiple', 'n_clicks')],
    [dash.dependencies.State('multi-dropdown', 'value')])
def process_multiple(n_clicks, value):
    return f'The input value was "{value}", button was clicked {n_clicks}'


# listen on all ports
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')

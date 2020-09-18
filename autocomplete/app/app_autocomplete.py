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

# optimize using view level cache
from flask_caching import Cache
from elastic import gene_index_creation_date

# setup logger and translations
logger = logging.getLogger(__name__)
i18n.load_path.append('./assets/')

# configure dash app
app = dash.Dash(__name__)

# Setup cache, just use local file system for now.
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': '/tmp/'
})
# check last load of elastic every hour
CHECK_ELASTIC_LOAD_TIMEOUT = 60*60
# otherwise, infinite - use creation_date to invalidate cache
TIMEOUT = 0
# flask cache has no stats, so let's maintain one here
# (not necessary for app, just an FYI)
CACHE_STATS = {'hits': 0, 'misses': 0, 'calls': 0}

app.layout = html.Div(
    [
        html.H1(children=t('autocomplete.instructions')),

        html.Label([t('autocomplete.single'), dcc.Dropdown(id='single-dropdown')]),
        html.Button(t('autocomplete.phenotypes'), id='process-single', n_clicks=0),
        html.Div(id='process-single-output'),

        html.Label([t('autocomplete.multiple'), dcc.Dropdown(id='multi-dropdown', multi=True)]),
        html.Button(t('autocomplete.phenotypes'), id='process-multiple'),
        html.Div(id='process-multiple-output'),

        html.Button(t('autocomplete.clear_cache'), id='clear-cache', n_clicks=0),
        html.Button(t('autocomplete.cache_stats'), id='info-cache', n_clicks=0),
        html.Div(id='cache-output'),
        html.Div(id='info-cache-output'),

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


def format_phenotype(p):
    """Reduce phenotype for display."""
    return f"{p['description']}/{p['attributes'].get('external_reference','?')}"


@app.callback(
    dash.dependencies.Output('process-single-output', 'children'),
    [dash.dependencies.Input('process-single', 'n_clicks')],
    [dash.dependencies.State('single-dropdown', 'value')])
def process_single(n_clicks, value):
    """As an example backend, call ensemble."""
    if not value:
        raise PreventUpdate
    phenotypes = cached_phenotypes(value.split('/')[1])
    CACHE_STATS['calls'] += 1
    formatted_phenotypes = [format_phenotype(p) for p in phenotypes]
    return f'phenotypes: {formatted_phenotypes}'


@app.callback(
    dash.dependencies.Output('process-multiple-output', 'children'),
    [dash.dependencies.Input('process-multiple', 'n_clicks')],
    [dash.dependencies.State('multi-dropdown', 'value')])
def process_multiple(n_clicks, value):
    """As an example backend, call ensemble."""
    if not value:
        raise PreventUpdate
    phenotypes_list = [cached_phenotypes(v.split('/')[1]) for v in value]
    formatted_phenotypes = [[format_phenotype(p) for p in phenotypes] for phenotypes in phenotypes_list]
    CACHE_STATS['calls'] += len(value)
    return f'phenotypes: {formatted_phenotypes}'


@cache.memoize(timeout=CHECK_ELASTIC_LOAD_TIMEOUT)
def invalidate_cache():
    """Return the timestamp of graph load time."""
    return gene_index_creation_date()


@cache.memoize(timeout=TIMEOUT)
def cached_phenotypes(ensemble_id, _valid=invalidate_cache()):
    """Wrap call to backend in cache."""
    CACHE_STATS['misses'] += 1
    return fetch_phenotypes(ensemble_id)


@app.callback(
    dash.dependencies.Output('cache-output', 'children'),
    [dash.dependencies.Input('clear-cache', 'n_clicks')])
def clear_cache(n_clicks):
    """Clears the cache."""
    if n_clicks == 0:
        raise PreventUpdate
    cache.clear()
    global CACHE_STATS
    CACHE_STATS = {'hits': 0, 'misses': 0, 'calls': 0}
    return t('autocomplete.cached_cleared')


@app.callback(
    dash.dependencies.Output('info-cache-output', 'children'),
    [dash.dependencies.Input('info-cache', 'n_clicks')])
def cache_stats(n_clicks):
    """Shows stats on cache."""
    if n_clicks == 0:
        raise PreventUpdate
    CACHE_STATS['hits'] = CACHE_STATS['calls'] - CACHE_STATS['misses']
    return repr(CACHE_STATS)


# listen on all ports
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')

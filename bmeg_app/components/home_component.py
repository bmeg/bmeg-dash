import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def build_card(header, body, button, button_href):
    '''
    Create dbc cards, Input strings of each card section.
    Card body can be a list of paragraph strings
    '''
    contents = []
    contents.append(html.H4((header), className="card-title"))
    for b in body:
        contents.append(html.P(b))
    contents.append(
        dbc.Button(dbc.NavLink(button), href=button_href, color="info")
    )
    return dbc.Card(dbc.CardBody(contents), color='light')


def bar(fig_title, infotext, xvals, yvals, plot_color, height, xlabel, ylabel):
    '''Bar chart'''
    assert len(xvals) == len(yvals)
    layout = go.Layout(
        hovermode='x unified',
        title=fig_title,
        height=height,
        margin={'t': 5, 'b': 0},
        legend_orientation="h",
        font=dict(family="sans-serif", size=10, color='black'),
        plot_bgcolor='white',
        paper_bgcolor='white')
    fig = go.Figure(layout=layout)
    fig.add_trace(
        go.Bar(
            x=xvals,
            y=yvals,
            marker=dict(color=plot_color),
            textposition='auto'
        )
    )
    fig.update_yaxes(
        showline=False,
        title=ylabel
    )
    fig.update_xaxes(
        showline=True,
        title=xlabel,
        linewidth=1,
        linecolor='black'
    )
    return fig


def card(k, v):
    '''Count card'''
    mod_plural = {
        'Publication': 'PubLit Article',
        'DrugResponse': 'Drug Response'
    }
    label = k
    if label in mod_plural:
        label = mod_plural[k]
    fig = go.Indicator(
        mode="number",
        value=v,
        number={'suffix': " {}s".format(label)},
        domain={'x': [0, 1], 'y': [0, 1]}
    )
    return fig


def counts(h, res_dict):
    '''Banner of count cards'''
    fig = make_subplots(
        rows=4, cols=3,
        specs=[
            [
                {'type': 'indicator'},
                {'type': 'indicator'},
                {'type': 'indicator'}
            ],
            [
                {'type': 'indicator'},
                {'type': 'indicator'},
                {'type': 'indicator'}
            ],
            [
                {'type': 'indicator'},
                {'type': 'indicator'},
                {'type': 'indicator'}
            ],
            [
                {'type': 'indicator'},
                {'type': 'indicator'},
                {'type': 'indicator'}
            ]
        ]
    )
    fig.add_trace(
        card('Allele', res_dict['Allele']),
        row=1, col=1
    )
    fig.add_trace(
        card('Gene', res_dict['Gene']),
        row=1, col=2
    )
    fig.add_trace(
        card('Protein', res_dict['Protein']),
        row=1, col=3
    )
    fig.add_trace(
        card('Transcript', res_dict['Transcript']),
        row=2, col=1
    )
    fig.add_trace(
        card('Pathway', res_dict['Pathway']),
        row=2, col=2
    )
    fig.add_trace(
        card('Compound', res_dict['Compound']),
        row=2, col=3
    )
    fig.add_trace(
        card('DrugResponse', res_dict['DrugResponse']),
        row=3, col=1
    )
    fig.add_trace(
        card('Interaction', res_dict['Interaction']),
        row=3, col=2
    )
    fig.add_trace(
        card('Exon', res_dict['Exon']),
        row=3, col=3
    )
    fig.add_trace(
        card('Aliquot', res_dict['Aliquot']),
        row=4, col=1
    )
    fig.add_trace(
        card('Project', res_dict['Project']),
        row=4, col=2
    )
    fig.add_trace(
        card('Publication', res_dict['Publication']),
        row=4, col=3
    )
    fig.update_layout(margin={'t': 10, 'b': 0, 'l': 10, 'r': 10}, height=h)
    return fig

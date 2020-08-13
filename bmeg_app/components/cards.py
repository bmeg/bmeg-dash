
def card(k,v,graph_col,graph_font,h):
    '''
    input text to display (k), numeric value (v), and plot height
    '''
    mod_plural = {'Publication':'PubLit Article','DrugResponse': 'Drug Response'}
    import plotly.graph_objects as go
    label = k
    if label in mod_plural:
        label = mod_plural[k]
    lay = go.Layout(margin={'t':0,'b':0, 'l':100,'r':1000},paper_bgcolor = graph_col,height=h,font=dict(family=graph_font,size=8,color='black'))
    gofig = go.Indicator(
        mode = "number",
        value = v,
        number = {'suffix': " {}s".format(label)},
            domain = {'x': [0, 1], 'y': [0, 1]})
#     fig = go.Figure(gofig, layout=lay)
    return gofig

def counts(h,res_dict,graph_col,graph_font):
    from plotly.subplots import make_subplots
    fig = make_subplots(rows=4, cols=3, specs=[[{'type':'indicator'}, {'type':'indicator'}, {'type':'indicator'}],
                                                [{'type':'indicator'}, {'type':'indicator'}, {'type':'indicator'}],
                                                [{'type':'indicator'}, {'type':'indicator'}, {'type':'indicator'}],
                                                [{'type':'indicator'}, {'type':'indicator'},{'type':'indicator'}]])
    fig.add_trace(card('Allele', res_dict['Allele'],graph_col,graph_font,h),row=1, col=1)
    fig.add_trace(card('Gene', res_dict['Gene'],graph_col,graph_font,h),row=1, col=2)
    fig.add_trace(card('Protein', res_dict['Protein'],graph_col,graph_font,h),row=1, col=3)
    fig.add_trace(card('Transcript', res_dict['Transcript'],graph_col,graph_font,h),row=2, col=1)
    fig.add_trace(card('Pathway', res_dict['Pathway'],graph_col,graph_font,h),row=2, col=2)
    fig.add_trace(card('Compound', res_dict['Compound'],graph_col,graph_font,h),row=2, col=3)
    fig.add_trace(card('DrugResponse', res_dict['DrugResponse'],graph_col,graph_font,h),row=3, col=1)
    fig.add_trace(card('Interaction', res_dict['Interaction'],graph_col,graph_font,h),row=3, col=2)
    fig.add_trace(card('Exon', res_dict['Exon'],graph_col,graph_font,h),row=3, col=3)
    fig.add_trace(card('Aliquot', res_dict['Aliquot'],graph_col,graph_font,h),row=4, col=1)
    fig.add_trace(card('Project', res_dict['Project'],graph_col,graph_font,h),row=4, col=2)
    fig.add_trace(card('Publication', res_dict['Publication'],graph_col,graph_font,h),row=4, col=3)
    fig.update_layout(margin={'t':10, 'b':0, 'l':10, 'r':10}, height=h)
    return fig

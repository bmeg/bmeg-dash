def bar_thresh(fig_title, infotext, X_VALS, Y_VALS,INPUT_freq_threshold, plot_color,INPUT_HEIGHT,x_axis_label,y_axis_label):
    '''
    Create plots
    '''
    import plotly.graph_objects as go
    assert len(X_VALS) ==len(Y_VALS)
    X_VALS = X_VALS
    Y_VALS = Y_VALS
    layout = go.Layout(hovermode='x unified',title=fig_title,height=INPUT_HEIGHT,margin={'t':5, 'b':0},legend_orientation="h",font=dict(family="sans-serif",size=10,color='black'),plot_bgcolor='white',paper_bgcolor='white')  
    fig = go.Figure(layout=layout)
    fig.add_trace(go.Bar(x=X_VALS, y=Y_VALS,
                        marker=dict(color=plot_color),
                        textposition='auto'))
    fig.update_yaxes(showline=False, title=y_axis_label)
    fig.update_xaxes(showline=True,title =x_axis_label,linewidth=1,linecolor='black')
    return fig

def bar_thresh_additional(fig_title, infotext, X_VALS, Y_VALS,INPUT_freq_threshold, plot_color,INPUT_HEIGHT,x_axis_label,y_axis_label):
    '''
    Create plots
    '''
    import plotly.graph_objects as go
    assert len(X_VALS) ==len(Y_VALS)
    X_VALS = X_VALS
    Y_VALS = Y_VALS
    layout = go.Layout(hovermode='x unified',title=fig_title,height=INPUT_HEIGHT,margin={'t':5, 'b':5},legend_orientation="h",font=dict(family="sans-serif",size=10,color='black'),plot_bgcolor='white',paper_bgcolor='white')  
    fig = go.Figure(layout=layout)
    fig.add_trace(go.Bar(x=X_VALS, y=Y_VALS,
                        marker=dict(color=plot_color),
                        text=[f'{element}<br>{infotext}' for element in X_VALS],
                        textposition='auto'))
    fig.update_yaxes(showline=False, title=y_axis_label)
    fig.update_xaxes(showline=True,title =x_axis_label,linewidth=1,linecolor='black')
    return fig

def get_histogram_normal(data, x_title, y_title, box_color, plot_height, y_ticks):
    '''
    input values to plot. can be pandas df['col']
    yticks == how far apart ticks
     returns go figure
    '''
    import pandas as pd
    import plotly.graph_objects as go
    fig = go.Figure(data=[go.Histogram(x=data,marker=dict(color=box_color))])#.update_yaxes(categoryorder="total ascending")
    fig.update_layout(margin={'t':10, 'b':100},
        height=plot_height,
        yaxis=dict(title=y_title),
        # yaxis=dict(title=y_title,tickmode='linear', dtick=y_ticks),
        xaxis=dict(title=x_title),
        plot_bgcolor='white',
        paper_bgcolor='white',
        hovermode='x unified')
    fig.update_xaxes(showline=True,linewidth=1,ticks='outside',linecolor='black')
    fig.update_yaxes(showline=True,linewidth=1,ticks='outside',linecolor='black')
    return fig

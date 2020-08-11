def bar_thresh(fig_title, infotext, X_VALS, Y_VALS,INPUT_freq_threshold, plot_color,INPUT_HEIGHT,x_axis_label,y_axis_label):
    '''
    Create plots
    '''
    import plotly.graph_objects as go
    assert len(X_VALS) ==len(Y_VALS)
    X_VALS = X_VALS
    Y_VALS = Y_VALS
    layout = go.Layout(hovermode='x unified',title=fig_title,height=INPUT_HEIGHT,margin={'t':30, 'b':10},legend_orientation="h",font=dict(family="sans-serif",size=10,color='black'),plot_bgcolor='white',paper_bgcolor='white')  
    fig = go.Figure(layout=layout)
    fig.add_trace(go.Bar(x=X_VALS, y=Y_VALS,
                        marker=dict(color=plot_color),
                        text=[f'{element}<br>{infotext}' for element in X_VALS],
                        textposition='auto'))
    fig.update_yaxes(showline=False, title=y_axis_label)
    fig.update_xaxes(showline=True,title =x_axis_label,linewidth=1,linecolor='black')
    return fig

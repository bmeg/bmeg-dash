


@app.callback(
    Output('page-content', 'children'),
    [Input({'type': 'new-button', 'index': ALL}, 'n_clicks'), Input({'type':'close-button', 'index':ALL}, 'n_clicks')],
    [State('page-content', 'children')])
def update_output(n_clicks, close_clicks, content):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'No clicks yet'
        return [ ]
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        d = json.loads(button_id)
        print(button_id)
        if d['type'] == "new-button":
            n = d['index']
            if n in view_map:
                print("Creating: %s" % (n))
                clicks = sum( a for a in n_clicks if a is not None )
                content = [ create_window(n, clicks) ] + content
        elif d['type'] == "close-button":
            print("Close ", d['index'])
            o = []
            for c in content:
                if c['props']['id']['index'] != d['index']:
                    o.append(c)
            content = o
    return content

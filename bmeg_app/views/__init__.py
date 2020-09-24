import dash_bootstrap_components as dbc
from .. import appLayout as ly

styles=ly.styles

def info_button(id,text):
    return [get_icon(id), icon_hovertext(id,text)]
    
def get_icon(out_id):
    return dbc.Button(
        '?',
        id=f"icon_target_{out_id}",
        style=styles['help_button'],
        className="mx-2",
    )

def icon_hovertext(in_id,text):
    return dbc.Tooltip(
        text,
        target=f"icon_target_{in_id}",
        style=styles['help_button_text'],
        placement='right',
    )

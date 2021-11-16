import dash_bootstrap_components as dbc
from ..style import format_style


def info_button(id, text):
    return [get_icon(id), icon_hovertext(id, text)]


def get_icon(out_id):
    return dbc.Button(
        '?',
        id=f"icon_target_{out_id}",
        style=format_style('help_button'),
        className="mx-2",
    )


def icon_hovertext(in_id, text):
    return dbc.Tooltip(
        text,
        target=f"icon_target_{in_id}",
        style=format_style('help_button_text'),
        placement='right',
    )

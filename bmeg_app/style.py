def color_palette(key):
    ''' '''
    dictionary = {
        'background': 'lightcyan',
        'text': 'black',
        'pale_yellow':'#FCE181',
        'pale_orange':'#F4976C',
        'lightblue':'#17BECF',
        'darkgreen_border':'#556B2F',
        'lightgreen_borderfill':'olivedrab',
        'lightgrey':'whitesmoke',
        'tab_lightblue':'#88BDBC',
        'tab_darkblue':'#026670'
    }
    return dictionary[key]

def format_style(key):
    dictionary = {
        'font':'Arial',
        'font_size': 12,
        'font_size_lg': 14,
        'banner': {
            'textAlign': 'center',
            'color':'#026670', #tab_darkblue
            'type-font':'Arial',
            'font-size':50,
            'font-style':'italic',
            'font-weight':'bold',
            'padding':10,
        },
        'subbanner': {
            'backgroundColor' : '#88BDBC', # tab_lightblue
            'textAlign': 'center',
            'color':'white',
            'type_font':'Arial',
            'padding':10,
        },
    }
    return dictionary[key]


# styles = {
#     'banner': { #added
#         'textAlign': 'center',
#         'color':main_colors['tab_darkblue'],
#         'type-font':'Arial',
#         'font-size':50,
#         'font-style':'italic',
#         'font-weight':'bold',
#         'padding':10,
#     },
#     'subbanner': { #added
#         'backgroundColor': main_colors['tab_lightblue'],
#         'textAlign': 'center',
#         'color':'white',
#         'type_font':'Arial',
#         'padding':10,
#     },
#     'card_header':{
#         'height':'10%'
#     },
#     'card_body':{
#         'height':'25%'
#     },
#     'sh': {
#         'backgroundColor': main_colors['tab_lightblue'],
#         'textAlign': 'center',
#         'color':'white',
#         'fontSize': 15,
#         'marginTop':20,
#         'marginBottom':0,
#         'padding':5
#     },
#     't': {
#         'type_font':'Arial',
#         'size_font':12,
#         'font_size_lg':14,
#     },
#     'tab_help_button':{
#         'paddingTop':2,
#         'paddingBottom':2,
#         'paddingLeft':8,
#         'paddingRight':8,
#         'font-size':14,
#         'font-family':'Arial',
#         'textAlign':'middle',
#         'margin':'bottom'
#     },
#     'help_button':{
#         'paddingTop':2,
#         'paddingBottom':2,
#         'paddingLeft':8,
#         'paddingRight':8,
#         'font-size':10,
#         'font-family':'Arial',
#     },
#     'help_button_text':{
#         'padding':20,
#         'font-size':12,
#         'font-family':'Arial',
#     },
#     'b': {
#         'padding_left':'15px',
#         'padding_top':'15px'
#     }
# }

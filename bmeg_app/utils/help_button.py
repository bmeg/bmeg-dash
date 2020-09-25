import dash_html_components as html
import dash_bootstrap_components as dbc
from .. import appLayout as ly


import dash_bootstrap_components as dbc

def button_text(modaltext_id,header,text_list):
    '''Help button display information when clicked
    Input header string, dash component id, list of text body strings.
    Each element in text body list will be displayed as a new line.'''
    out_list = []
    out_list.append(dbc.ModalHeader(header))
    for i in range(0, len(text_list)):
        out_list.append(dbc.ModalBody(text_list[i]))
    out_list.append(dbc.ModalFooter(dbc.Button('Close',id=modaltext_id,className='ml-auto')),)
    return out_list
    
        
def sidebar_button(button_id,modal_id,modaltext_id,button, header,text_body):
    styles=ly.styles
    out = html.Div([
        dbc.Button(button, id=button_id,color='link',style=styles['tab_help_button']),
        dbc.Modal(button_text(modaltext_id,header,text_body),
            id=modal_id,
            size='lg',
            centered=True,
        ),
    ])   
    return out 
    # html.Div([
    #     dbc.Button(button, id='open1',color='link',style=styles['tab_help_button']),
    #     dbc.Modal(
    #         [
    #             dbc.ModalHeader(header),
    # 
    #             dbc.ModalBody("Interrogate cell line drug screening trials from large established sources (CCLE, CTRP, GDSC). Dig into drug sensitivity trends within a particular disease and explore associated metadata."),
    #             dbc.ModalBody( 'What’s going on behind the scenes?'),
    #             dbc.ModalBody( '•	Data is queried from BMEG, filtered for relevant cell lines (breast tissue derived cell lines kept if breast cancer is selected), and analyzed in the viewer.'),
    #             dbc.ModalBody( 'Panel 1 Features'),
    #             dbc.ModalBody( '• Download a table of all cell line drug screening results based on three dropdown menus. Quickly see metadata composition of the table from the pie charts.'),
    #             dbc.ModalBody( 'Panel 2 Features'),
    #             dbc.ModalBody( '• Dive deeper to explore underlying trends between two drugs. Drug response values are plotted to quickly identify potential drug candidates that elicted similar responses from cell lines.'),
    #             dbc.ModalBody( '• Blue cards provide a summary of the selected drugs to provide insight on the molecular and/or biological realm of the selected drug.'),
    #             dbc.ModalBody( '• Examine the drug characteristics table for potential taxonomic reasons for similar and different responses from drugs.'),
    #             dbc.ModalFooter(dbc.Button('Close',id='close1',className='ml-auto')),
    #         ],
    #         id='main_help1',
    #         size='lg',
    #         centered=True,
    #     ),
    # ])

import pandas as pd
import numpy as np
from collections import deque
import datetime
from datetime import datetime, timedelta
from dash import Dash, dcc, html, register_page, callback
from dash.dependencies import Output, Input
import plotly.express as px
import time

register_page(__name__)

layout = html.Div([
    html.H1("Cancellations by Airline"),
    dcc.Graph(id='airline-live-chart', animate=False),
    dcc.Interval(
        id='airline-graph-update',
        interval=1000,
        n_intervals=0
    )
])

max_length = 72
events_deq = deque(maxlen=max_length)
graph_updates_deq = deque(maxlen=max_length)
time_deque = deque(maxlen=1)
carrier_events_cols = []

start_time = pd.to_datetime('2022-12-27')
time_deque.append(start_time)

carrier_list = ['WN', 'AA', 'DL', 'UA']

fig1_event_list = []


for carr in carrier_list:
    fig1_event_list.append(f'is_normal_{carr}')
    fig1_event_list.append(f'delay_cancleled_{carr}')

pretty_carrier_names = ['Southwest', 'American', 'Delta', 'United']
fig2_pretty_event_list = []
for carr in [0, 1, 2, 3]:
    pretty_col_name = f'{pretty_carrier_names[carr]} Cancelled'
    fig2_pretty_event_list.append(pretty_col_name)

percent_cancelled_deque = deque(maxlen=max_length)
# % cancelled by carrier
fig2_event_list = []
fig2_help_list_1 = []
fig2_help_list_2 = []
for carr in carrier_list:
    fig2_event_list.append(f'PERCENT_CANCELLED_{carr}')
    fig2_help_list_1.append(f'CARR_CANCL_{carr}')
    fig2_help_list_2.append(f'FL_TOTAL_{carr}')

    carrier_events_cols.append(f'CARR_CANCL_{carr}')
    carrier_events_cols.append(f'FL_TOTAL_{carr}')

graph_perc_update_deq = deque(maxlen=max_length)

@callback(Output('airline-live-chart', 'figure'),
              [Input('airline-graph-update', 'n_intervals')])
def deque_update(n):

    file_timestamp = pd.Timestamp(time_deque[0]).strftime('%Y%m%d_%H%M')
    event_file_name = f'live_graph_data/cancl_airline/cancl_airline_{file_timestamp}.csv'

    new_event = pd.read_csv(event_file_name)

    if len(events_deq) >= max_length:
        # Be careful with time objs
        graph_update = graph_updates_deq[-1][carrier_events_cols] + new_event[carrier_events_cols] - events_deq[0][
            carrier_events_cols]

    if len(events_deq) < max_length and (len(events_deq) != 0):
        graph_update = graph_updates_deq[-1][carrier_events_cols] + new_event[carrier_events_cols]

    if len(events_deq) == 0:
        graph_update = new_event[carrier_events_cols].copy()

    ###
    ### TESTING
    new_time = time_deque[0] + timedelta(minutes=10)
    time_deque.append(new_time)

    new_event['date'] = time_deque[0]
    #new_event['date'] = indicator_deque[0]

    ### TESTING
    #

    graph_update.loc[:, 'TIME_GRAPH'] = new_event['date']
    events_deq.append(new_event)
    graph_updates_deq.append(graph_update)

    ###
    # Figure 2 update specific
    fig2_data = graph_updates_deq[-1]

    for carrier in list(range(0, 4)):
        fig2_data[fig2_event_list[carrier]] = fig2_data[fig2_help_list_1[carrier]] / fig2_data[fig2_help_list_2[carrier]]
    fig2_data['TIME_GRAPH'] = new_event['date']

    perc_canc_fillna_dict = dict(zip(fig2_event_list, [0, 0, 0, 0]))
    fig2_data.fillna(perc_canc_fillna_dict, inplace=True)

    ###TESTING
    fig2_data['test_time_xmin'] = 0
    fig2_data['test_time_xmax'] = 10

    graph_perc_update_deq.append(fig2_data)

    fig2_df = graph_perc_update_deq[0]
    for update in list(range(1, (len(graph_perc_update_deq)))):
        fig2_df = pd.concat([fig2_df, graph_perc_update_deq[update]])

    # Specify figure2 params
    xmin = (graph_perc_update_deq[0]['TIME_GRAPH'] - timedelta(minutes=10))
    xmin = (xmin.item())

    xmax = (graph_perc_update_deq[-1]['TIME_GRAPH'] + timedelta(minutes=20))
    xmax = (xmax.item())

    for carr in [0, 1, 2, 3]:
        fig2_df[fig2_pretty_event_list[carr]] = fig2_df[fig2_event_list[carr]]

    fig2 = px.line(fig2_df, y=fig2_pretty_event_list, x='TIME_GRAPH', range_y=[0, 1], range_x=[xmin, xmax])
    fig2.update_xaxes(autorange=False)
    fig2.update_layout(yaxis_tickformat=',.0%')
    fig2.update_layout(legend_title_text='Airline')

    return fig2
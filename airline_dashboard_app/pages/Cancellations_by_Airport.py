import pandas as pd
import numpy as np
from collections import deque
from datetime import timedelta
from dash import Dash, dcc, html, register_page, callback
from dash.dependencies import Output, Input
import plotly.express as px
import time

register_page(__name__)

layout = html.Div([
    html.H1("Cancellations by Airport"),
    dcc.Graph(id='airport-live-chart', animate=False),
    dcc.Interval(
        id='airport-graph-update',
        interval=1000,
        n_intervals=0,
        max_intervals=72
    )
])

max_length = 72
events_deq = deque(maxlen=max_length)
graph_updates_deq = deque(maxlen=max_length)
carrier_events_cols = []

start_time = pd.to_datetime('2022-12-27')
time_deque = deque(maxlen=1)
time_deque.append(start_time)
time_len = timedelta(minutes=10)

###
###

#Test DF Data
df = pd.read_csv("T_MASTER_CORD.csv")

df.dropna(subset=['LATITUDE'], inplace=True)
df.dropna(subset=['LONGITUDE'], inplace=True)

df_lat = df.groupby('AIRPORT', as_index=False)['LATITUDE'].mean()
df_lon = df.groupby('AIRPORT', as_index=False)['LONGITUDE'].mean()

com_df = pd.merge(df_lat, df_lon, how='left', on='AIRPORT')
com_df.columns = ['AIRPORT', 'LATITUDE', 'LONGITUDE']

orig_airport_file = pd.read_csv(
        "airport_zone_adjustors_mins_orig.csv")

orig_airport_file['AIRPORT'] = orig_airport_file['ORIGIN']
com_df = pd.merge(com_df, orig_airport_file, on='AIRPORT')

com_df['ORIGIN'] = com_df['AIRPORT']
airport_cords_df = com_df[['ORIGIN', 'LATITUDE', 'LONGITUDE']].copy()

airport_cords_df['Name'] = airport_cords_df['ORIGIN']
airport_cords_df.set_index('ORIGIN', inplace=True)


@callback(Output('airport-live-chart', 'figure'),
              [Input('airport-graph-update', 'n_intervals')])
def deque_update(n):
    file_timestamp = pd.Timestamp(time_deque[0]).strftime('%Y%m%d_%H%M')
    event_file_name = f'live_graph_data/cancl_airports/cancl_airports_{file_timestamp}.csv'
    new_event = pd.read_csv(event_file_name, index_col=0)
    new_event = new_event.T
    new_event.index.name = 'ORIGIN'
    new_event.columns = ['CANCELLED']

    if len(events_deq) >= max_length:
        # Be careful with time objs
        graph_update = graph_updates_deq[-1] + new_event - events_deq[0]

    if len(events_deq) < max_length and (len(events_deq) != 0):
        graph_update = graph_updates_deq[-1] + new_event

    if len(events_deq) == 0:
        graph_update = new_event

    new_time = time_deque[0] + time_len
    time_deque.append(new_time)

    events_deq.append(new_event)
    graph_updates_deq.append(graph_update)

    # Figure 3 update specific
    cancellations = graph_update.copy()
    cancellations.columns = ['CANCELLATIONS']

    airport_cords_df['CANCELLATIONS'] = 0
    airport_cords_df['CANCELLATIONS'] = cancellations['CANCELLATIONS']

    fig3_data = airport_cords_df
    fig3_data['CANCELLATIONS'] = pd.to_numeric(fig3_data['CANCELLATIONS'])

    fig3 = px.scatter_geo(
        fig3_data,
        hover_name='Name',
        lat="LATITUDE", lon="LONGITUDE",
        size='CANCELLATIONS',
        color_discrete_sequence=["royalblue"])

    fig3.update_geos(center=dict(lon=-93, lat=36), projection_scale=5.5)

    return fig3
import pandas as pd
import datetime
from datetime import datetime, timedelta

wn_total = 0

df_raw_file = pd.read_csv("big_four_crisis_days.csv")

red_df = df_raw_file[df_raw_file['FL_DATE'].str.startswith('2022-12-2')]

# origin data merge for ap numbers and tzones
orig_airport_file = pd.read_csv(
    "airport_zone_adjustors_mins_orig.csv")
dest_airport_file = pd.read_csv(
    "airport_zone_adjustors_mins_dest.csv")

red_df = red_df.merge(orig_airport_file, how='inner', on='ORIGIN')

# DEST data merge for ap numbers and tzones
red_df = red_df.merge(dest_airport_file, how='inner', on='DEST')

red_df['CRS_DEP_TIME'] = pd.to_datetime(red_df['FL_DATE'].astype(str) + ' ' + red_df['CRS_DEP_TIME'].astype(str))

red_df['CRS_DEP_TIME'] = red_df['CRS_DEP_TIME'] - pd.to_timedelta(red_df['ORIG_ADJUSTOR'], unit='m')

red_df['CRS_ARR_TIME'] = red_df['CRS_DEP_TIME'] + pd.to_timedelta(red_df['CRS_ELAPSED_TIME'], unit='m')

red_df.fillna({'DELAY_DUE_CARRIER': 0, 'DELAY_DUE_WEATHER': 0, 'DELAY_DUE_NAS': 0,
               'DELAY_DUE_LATE_AIRCRAFT': 0, 'DELAY_DUE_SECURITY': 0, 'CANCELLATION_CODE': 0}, inplace=True)

red_df['MINS_DELAY'] = (
    red_df['DELAY_DUE_CARRIER'].astype(int) + red_df['DELAY_DUE_WEATHER'].astype(int) +
    red_df['DELAY_DUE_NAS'].astype(int) + red_df['DELAY_DUE_SECURITY'].astype(int) +
    red_df['DELAY_DUE_LATE_AIRCRAFT'].astype(int)
)
red_df['DELAY_BY_20'] = (red_df['MINS_DELAY'] >= 20).astype(int)
red_df['IS_CANCEL'] = (red_df['CANCELLATION_CODE'] != 0).astype(int)
red_df['IS_DELAY20_CANCEL'] = (((red_df['DELAY_BY_20']).astype(int) + (red_df['IS_CANCEL']).astype(int)) != 0).astype(int)

###
#crisis_df = red_df
#red_df = crisis_df

carrier_list = ['WN']
carrier_events_cols = []
for carrier in carrier_list:
    for column in ['CARR_DELAY20_', 'CARR_CANCL_', 'CARR_ISNORMAL_', 'IS_DELAY20_CANCEL_', 'FL_TOTAL_']:
        carrier_events_cols.append(f'{column}{carrier}')

    red_df[f'CARR_DELAY20_{carrier}'] = (((red_df[f'DELAY_BY_20'] == 1) & (red_df[f'AIRLINE_CODE'] == carrier)).astype(int))
    red_df[f'CARR_CANCL_{carrier}'] = (((red_df[f'IS_CANCEL'] == 1) & (red_df[f'AIRLINE_CODE'] == carrier)).astype(int))
    red_df[f'CARR_ISNORMAL_{carrier}'] = (((red_df[f'IS_DELAY20_CANCEL'] != 1) & (red_df[f'AIRLINE_CODE'] == carrier)).astype(int))
    red_df[f'IS_DELAY20_CANCEL_{carrier}'] = (((red_df[f'IS_DELAY20_CANCEL'] == 1) & (red_df[f'AIRLINE_CODE'] == carrier)).astype(int))
    red_df[f'FL_TOTAL_{carrier}'] = 1

carrier_events_cols.append('TIMESTAMP')
carrier_events_cols.append('ORIGIN')
red_df['TIMESTAMP'] = 0

red_df.sort_values(by='CRS_DEP_TIME', inplace=True)

airport_list = pd.read_csv(
        "airport_zone_adjustors_mins_orig.csv")

event_file_name_list = []
info_list = []

tag = 'true'
time_len = timedelta(minutes=10)
start_time = pd.to_datetime('2022-12-27') - timedelta(minutes=10)
count_add = 0
end_time = pd.to_datetime('2022-12-27') + timedelta(hours=24)
while tag == 'true':
    start_time = start_time + time_len
    stop_time = start_time + time_len

    loop_df = red_df[(red_df['CRS_DEP_TIME'] >= start_time) & (red_df['CRS_DEP_TIME'] < stop_time)]
    loop_df = loop_df[carrier_events_cols]

    cancl_airport_df = airport_list[['ORIGIN']].copy()

    sum_df = loop_df.groupby('ORIGIN').sum([[carrier_events_cols]])
    sum_df['CANCELLED'] = sum_df['CARR_CANCL_WN']

    reduced_sum_df = sum_df[['CANCELLED']]
    cancl_airport_df = pd.merge(cancl_airport_df, reduced_sum_df, how='left', on='ORIGIN')

    cancl_airport_df = cancl_airport_df.T
    cancl_airport_df = cancl_airport_df.sort_values('ORIGIN', axis=1)

    cancl_airport_df.columns = cancl_airport_df.iloc[0]

    export_data_df = cancl_airport_df.iloc[[1]].copy()
    export_data_df = export_data_df.fillna(0)

    file_timestamp = pd.Timestamp(start_time).strftime('%Y%m%d_%H%M')
    event_file_name = f'airline_dashboard/live_graph_data/cancl_airports/cancl_airports_{file_timestamp}.csv'
    sum_df['TIMESTAMP'] = file_timestamp

    export_data_df.to_csv(event_file_name)

    info_list.append(sum_df)

    if stop_time >= end_time:
        tag = 'false'

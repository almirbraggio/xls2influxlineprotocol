import pandas as pd
import warnings, math

calc_diff = False

file_path = "/mnt/d/Users/almir/Downloads/input_file.xlsx"

'''
col_names = ['num', 'time', 'gps', 'location', 'ign', 'din1', 'speed', 'fuel_level', \
    'fuel_rate', 'fuel_inst', 'fuel_total', 'pedal', 'load', 'rpm', 'batt', 'temp_eng', \
    'temp_air', 'odom', 'can0', 'can1', 'can2', 'can3', 'can4', 'can6', 'can7', 'can8']
col_types = {'num': int, 'time': object, 'gps': object, 'location': object, 'ign': bool, 'din1': bool, \
    'speed': float, 'fuel_level': float, 'fuel_rate': float, 'fuel_inst': float, 'fuel_total': float, \
    'pedal': bool, 'load': float, 'rpm': float, 'batt': float, 'temp_eng': float, 'temp_air': float, \
    'odom': float, 'can0': float, 'can1': float, 'can2': float, 'can3': float, 'can4': float, \
    'can6': float, 'can7': float, 'can8': float}
col_ids = 'A:N,P:R,AB,AF:AJ,AL:AN'
'''

col_names = ['time', 'gps', 'ign', 'din1', 'speed', \
    'fuel_level', 'fuel_rate', 'fuel_inst', 'fuel_total', 'pedal', \
    'load', 'rpm', 'batt_volt', 'eng_temp', 'air_temp', \
    'can0', 'can1', 'can2', 'can3', 'can4', \
    'can6', 'can7', 'can8']
col_types = {'time': object, 'gps': object, 'ign': float, 'din1': float, 'speed': float, \
    'fuel_level': float, 'fuel_rate': float, 'fuel_inst': float, 'fuel_total': float, 'pedal': float, \
    'load': float, 'rpm': float, 'batt_volt': float, 'eng_temp': float, 'air_temp': float, \
    'can0': float, 'can1': float, 'can2': float, 'can3': float, 'can4': float, \
    'can6': float, 'can7': float, 'can8': float}
#col_ids = 'B,C,E,F,G, H,I,J,K,L, M,N,P,Q,R, AF,AG,AH,AI,AJ, AL,AM,AN'
#col_ids = 'B,C,E,F,G, H,I,J,K,L, M,N,P,Q,R, AE,AF,AG,AH,AI, AK,AL,AM'
col_ids = 'B,F,H,I,J, K:O, P,Q,S:U, AH:AL, AN:AP'

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    excel_file = pd.ExcelFile(file_path)
    df = pd.read_excel(excel_file, names=col_names, usecols=col_ids, dtype=col_types, \
    sheet_name='Sensor tracing', engine='openpyxl', na_values=['-----'])#, nrows=100)

df.time = pd.to_datetime(df.time, format='%d/%m/%Y %H:%M:%S')

# remove invalid time lines
df = df.loc[~df.time.isnull()]

# lat and long assignment
df = df.assign(lat=0.0, long=0.0)
df.lat = df.gps.str.slice(stop=10).astype(float)
df.long = df.gps.str.slice(start=-10).astype(float)

# fuel data from can
df = df.assign(fuel_total_can=0.0, fuel_level_can=0.0)
df.fuel_total_can = df.can0 * 0.5
df.fuel_level_can = df.can1 * 0.4

# odometer from can
df = df.assign(odom_can=0.0)
df.odom_can = df.can6 * 5.0/1000.0

if (calc_diff == True):
    # convert gps to degrees to rad
    df = df.assign(lat_rad=0.0, long_rad=0.0)
    df.lat_rad = df.lat * 3.1415 / 180.0
    df.long_rad = df.long * 3.1415 / 180.0

    # speed difference and time difference
    df = df.assign(diff_speed=0.0, diff_time=0.0, diff_gps=0.0)
    df.diff_speed = df.speed.diff(periods=1)
    df.diff_time = df.time.diff(periods=1)

    # convert datetime difference to seconds
    df.diff_time = df.diff_time.dt.total_seconds()

    # gps distance in meters
    for i in range(1, len(df)):
        df.loc[i, 'diff_gps'] = 6371.0*2.0*math.atan( \
        math.sqrt( \
            math.pow(math.sin(df.loc[i, 'lat_rad']-df.loc[i-1, 'lat_rad'])/2.0,2)+ \
            math.pow(math.sin(df.loc[i, 'long_rad']-df.loc[i-1, 'long_rad'])/2.0,2)* \
            math.cos(df.loc[i-1, 'lat_rad'])*math.cos(df.loc[i, 'lat_rad']) \
            )/ \
        math.sqrt(1- \
            math.sin((df.loc[i, 'lat_rad']-df.loc[i-1, 'lat_rad'])/2.0)* \
            math.sin((df.loc[i, 'lat_rad']-df.loc[i-1, 'lat_rad'])/2.0)+ \
            math.sin((df.loc[i, 'long_rad']-df.loc[i-1, 'long_rad'])/2.0)* \
            math.sin((df.loc[i, 'long_rad']-df.loc[i-1, 'long_rad'])/2.0)* \
            math.cos(df.loc[i, 'lat_rad'])*math.cos(df.loc[i-1, 'lat_rad']) \
            ) \
        )

# convert datetime to unix timestamp
df.time = pd.to_datetime(df.time).map(pd.Timestamp.timestamp)
df.time = (df.time + (3.0*3600.0))*1000.0 # to utc milliseconds

df = df.fillna(0.0)

lines = [ \
        "from_wialon" + ",vehicle=hmv3723 " +
        "lat=" + str(df["lat"][d]) + "," +
        "long=" + str(df["long"][d]) + "," +
        "ign=" + str(df["ign"][d]) + "," +
        "din1=" + str(df["din1"][d]) + "," +
        "speed=" + str(df["speed"][d]) + "," +
        "fuel_level=" + str(df["fuel_level"][d]) + "," +
        "fuel_rate=" + str(df["fuel_rate"][d]) + "," +
        "fuel_inst=" + str(df["fuel_inst"][d]) + "," +
        "fuel_total=" + str(df["fuel_total"][d]) + "," +
        "pedal=" + str(df["pedal"][d]) + "," +
        "load=" + str(df["load"][d]) + "," +
        "rpm=" + str(df["rpm"][d]) + "," +
        "batt_volt=" + str(df["batt_volt"][d]) + "," +
        "eng_temp=" + str(df["eng_temp"][d]) + "," +
        "air_temp=" + str(df["air_temp"][d]) + "," +
        "fuel_total_can=" + str(df["fuel_total_can"][d]) + "," +
        "fuel_level_can=" + str(df["fuel_level_can"][d]) + "," +
        "odom_can=" + str(df["odom_can"][d]) + " " +
        str(int(df["time"][d])) \
        for d in range(len(df))
        ]

output = open('output.txt', 'a')
for item in lines:
    output.write("%s\n" % item)
    #print(item)
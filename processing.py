import pandas as pd
from scipy.stats import t
from datetime import datetime
from StrDef import StrDef

n = int(StrDef.CONST_STAT_TIME / StrDef.CONST_SLEEP_TIMER)  # samples_collected_per_hour

rts_parse = lambda x: datetime.strptime(x, '%d/%H:%M:%S')
ts_parse = lambda x: datetime.strptime(x, '%H:%M:%S')

CONST_DATE_STARTS = "15/"

def get_confidence_interval(mean, std_dev, n):
    lower_cutoff = t.ppf(0.025, n - 1, loc=mean, scale=std_dev)  # =>  99.23452406698323
    upper_cutoff = t.ppf(0.975, n - 1, loc=mean, scale=std_dev)  # => 100.76547593301677
    return lower_cutoff, upper_cutoff

# std =float("7.11E-15")

# print(get_confidence_interval(mean=25.68, std_dev=std, n=n))

def get_stats():
    csv_file = "wirelessIQ.csv"
    df_all = pd.read_csv(csv_file, skipinitialspace=True, header=None,
                     names=["userid_t", "userid_v", "measure_t", "measure_v", "ts_t", "ts_v",
                            "rts_t", "rts_v", "msg_len_t", "msg_len_v"])
    df_all = df_all.drop(['userid_t', 'userid_v','ts_t', 'rts_t', 'msg_len_t'], axis=1)

    df_all= df_all[df_all["rts_v"].str.startswith(CONST_DATE_STARTS)] # TODO

    df_all['rts_v'] = pd.to_datetime(df_all['rts_v'], format='%d/%H:%M:%S')
    df_all = df_all[df_all["rts_v"] > pd.to_datetime('1900-01-15 17:35:00')] # TODO remove for fresh sample
    df_all['rts_v'] = df_all['rts_v'].dt.time
    df_all['ts_v'] = pd.to_datetime(df_all['ts_v'], format='%H:%M:%S').dt.time
    # df_all['ts_v'] = [time.time() for time in df_all['ts_v']]

    df_per_msg = df_all.groupby(['rts_v', 'msg_len_v'])

    msgs = list()

    for group_name, df in df_per_msg:
        msg_dict = dict()
        msg_dict['time'] = group_name[0].strftime('%H:%M:%S')
        msg_dict['msg_length'] = group_name[1]

        std_dev_light = df[df["measure_t"].str.contains(StrDef.ST_LIGHT_SDV)]["measure_v"].values[0]
        std_dev_temp = df[df["measure_t"].str.contains(StrDef.ST_TEMPERATURE_SDV)]["measure_v"].values[0]
        std_dev_air_quality = df[df["measure_t"].str.contains(StrDef.ST_AIR_QUALITY_SDV)]["measure_v"].values[0]
        mean_light = df[df["measure_t"].str.contains(StrDef.ST_LIGHT_AVG)]["measure_v"].values[0]
        mean_temp = df[df["measure_t"].str.contains(StrDef.ST_TEMPERATURE_AVG)]["measure_v"].values[0]
        mean_air_quality = df[df["measure_t"].str.contains(StrDef.ST_AIR_QUALITY_AVG)]["measure_v"].values[0]
        max_temp = df[df["measure_t"].str.contains(StrDef.ST_TEMPERATURE_MAX)]["measure_v"].values[0]
        worst_air_quality = df[df["measure_t"].str.contains(StrDef.ST_AIR_QUALITY_WORST)]["measure_v"].values[0]

        msg_dict['temp_ci_low'], msg_dict['temp_ci_high'] = get_confidence_interval(mean_temp, std_dev_temp, n)
        msg_dict['air_quality_ci_low'], msg_dict['air_quality_ci_high'] = get_confidence_interval(mean_air_quality, std_dev_air_quality, n)
        msg_dict['light_ci_low'], msg_dict['light_ci_high'] = get_confidence_interval(mean_light, std_dev_light, n)

        msg_dict['mean_light'] = mean_light
        msg_dict['mean_air_quality'] = mean_air_quality
        msg_dict['mean_temp'] = mean_temp
        msg_dict['max_temp'] = max_temp
        msg_dict['worst_air_quality'] = worst_air_quality

        msgs.append(msg_dict)

    print(msgs)

# #
# def process_temperature():
#     csv_file = "wirelessIQ.csv"
#     df = pd.read_csv(csv_file, header=None,
#                      names=["usertopic", "userid", "measuretopic", "measurevalue", "tstopic", "tsvalue",
#                             "rts", "rtsvalue", "msleng", "msl"])
#     # print(df)
#     filtered_df1 = df[df["measuretopic"].str.contains("light_low")]
#     # print(filtered_df1)
#     filtered_df = filtered_df1.loc[:, ["measurevalue"]]
#
#     print(filtered_df)
#     print(filtered_df.mean())
# #

get_stats()
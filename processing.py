import pandas as pd

def process_temperature():
    csv_file = "wirelessIQ.csv"
    df = pd.read_csv(csv_file, header=None,
                     names=["usertopic", "userid", "measuretopic", "measurevalue", "tstopic", "tsvalue",
                            "rts", "rtsvalue", "msleng", "msl"])
    # print(df)
    filtered_df1 = df[df["measuretopic"].str.contains("light_low")]
    # print(filtered_df1)
    filtered_df = filtered_df1.loc[:, ["measurevalue"]]

    print(filtered_df)
    print(filtered_df.mean())

# userid, wirelessIQ, light_h1, 10.279329608938548, sample_timestamp, 17:19:19, received timestamp, 13/14:19:28, Message length, 558

process_temperature()
import time
from datetime import datetime, timedelta

import paho.mqtt.client as mqtt
import util
import sensor_api as sapi
import smbus

from StrDef import StrDef
from timer_wp import timer
import numpy as np

# WirelessIQ Parameters
CONST_SLEEP_TIMER = 2
CONST_KEEP_ALIVE = 60
CONST_STAT_TIME = 60  # 3600

# The callback for when the client receives a CONNACK response from the server.

client = mqtt.Client()
client.on_connect = util.on_connect
client.on_message = util.on_message

userid = util.userid

print(util.server)
client.connect(util.server, 1883, keepalive=CONST_KEEP_ALIVE)

# intialize sensors, so we can get data out
bus = smbus.SMBus(1)  # Rev 2 Pi uses 1
sensor = sapi.BH1750(bus)
bme680_sensor = sapi.sensor_bme680()  # Temperature, and Humidity sensor
sgp30_sensor = sapi.sensor_sgp30()  # Air quality sensor

array_sensor_keys = [
    StrDef.SEN_TEMPERATURE
    # , StrDef.SEN_HUMIDITY
    # , StrDef.SEN_PRESSURE
    , StrDef.SEN_AIR_QUALITY
    , StrDef.SEN_LIGHT_LOW
    , StrDef.SEN_LIGHT_HIGH1
    , StrDef.SEN_LIGHT_HIGH2
]

array_stat_keys = [
    StrDef.ST_TEMPERATURE_AVG
    , StrDef.ST_TEMPERATURE_SDV
    , StrDef.ST_TEMPERATURE_MAX
    , StrDef.ST_AIR_QUALITY_AVG
    , StrDef.ST_AIR_QUALITY_SDV
    , StrDef.ST_AIR_QUALITY_WORST
    , StrDef.ST_LIGHT_AVG
    , StrDef.ST_LIGHT_SDV
    , StrDef.ST_ARR_WINDOW_STATUS
    , StrDef.ST_ARTIFICIAL_LIGHT_STATUS
]


######################### Logic for furter programming #######################

def np_array_init_and_fill(size, val):
    a = np.empty(size)
    a.fill(val)
    return a


class SensorDataCollection:
    def __init__(self):
        self.counter = 0
        # self.arr_size = 5
        self.arr_size = 60  # int(CONST_STAT_TIME / CONST_SLEEP_TIMER)  # Collections per hour
        self.extra_counter = 0
        self.__reset_values()

    def __reset_values(self):
        # Temperature, pressure and humidty - BME680
        self.data_temp = np_array_init_and_fill(self.arr_size, 0)
        self.timestamps_temp = [0] * self.arr_size

        # self.data_pressure = np_array_init_and_fill(self.arr_size, 0)
        # self.timestamps_pressure = np_array_init_and_fill(self.arr_size, 0)
        #
        # self.data_humidity = np_array_init_and_fill(self.arr_size, 0)
        # self.timestamps_humidity = np_array_init_and_fill(self.arr_size, 0)

        # Air quality - SGP30
        self.data_airquality = np_array_init_and_fill(self.arr_size, 0)
        self.timestamps_airquality = [0] * self.arr_size

        # Light - BH1750
        self.data_lowres = np_array_init_and_fill(self.arr_size, 0)
        self.timestamps_lowres = [0] * self.arr_size

        self.data_highres = np_array_init_and_fill(self.arr_size, 0)
        self.timestamps_highres = [0] * self.arr_size
        self.data_highres2 = np_array_init_and_fill(self.arr_size, 0)
        self.timestamps_highres2 = [0] * self.arr_size

        self.stat_window_status = list()
        self.stat_light_status = list()

        self.stat_window_status_ts = list()
        self.stat_light_status_ts = list()

    def collect_temperature(self):
        # Temperature sample in celcius
        temp_sample, ts_temp = bme680_sensor.get_temp()
        # print(temp_sample, ts_temp)
        self.data_temp[self.counter] = temp_sample
        self.timestamps_temp[self.counter] = ts_temp
        return 0

    # @timer
    # def collect_humidity(self):
    #     # Humidity sample
    #     humidity_sample, ts_humid = bme680_sensor.get_humidity()
    #     self.data_humidity[self.counter] = humidity_sample
    #     self.timestamps_humidity[self.counter] = ts_humid
    #     return 0
    #
    # @timer
    # def collect_pressure(self):
    #     # Pressure sample
    #     pressure_sample, ts_pressure = bme680_sensor.get_pressure()
    #     self.data_pressure[self.counter] = pressure_sample
    #     self.timestamps_pressure[self.counter] = ts_pressure
    #     return 0

    def collect_air_quality(self):
        # air quality (CO2)
        airqual_sample, ts_qual = sgp30_sensor.get_sample()
        self.data_airquality[self.counter] = airqual_sample
        self.timestamps_airquality[self.counter] = ts_qual
        return 0

    def collect_light(self):
        # Light samples Lx
        sample, ts = sensor.measure_low_res()
        self.data_lowres[self.counter] = sample
        self.timestamps_lowres[self.counter] = ts

        sample, ts = sensor.measure_high_res()
        self.data_highres[self.counter] = sample
        self.timestamps_highres[self.counter] = ts
        sample, ts = sensor.measure_high_res2()
        self.data_highres2[self.counter] = sample
        self.timestamps_highres2[self.counter] = ts
        sensor.set_sensitivity((sensor.mtreg + 10) % 255)
        return 0

    def collect_window_status(self):
        open_status = self.counter % 2
        # TODO Calculate instead of above. Return 1 or 0 for open close status (value must be int/float)
        if len(self.stat_window_status) > 1 and open_status == self.stat_window_status[-1]:
            return 0
        ts = sapi.get_timestamp()  # TODO Add timestamp from original calculation
        self.stat_window_status.append(open_status)
        self.stat_window_status_ts.append(ts)
        return 0

    def collect_light_status(self):
        open_status = (self.counter + 1) % 2
        # TODO Calculate instead of above. Return 1 or 0 for open close status (value must be int/float)
        if len(self.stat_light_status) > 1 and open_status == self.stat_light_status[-1]:
            return 0
        ts = sapi.get_timestamp()  # TODO Add timestamp from original calculation
        self.stat_light_status.append(open_status)
        self.stat_light_status_ts.append(ts)
        return 0

    def periodical_stats(self):
        time.sleep(CONST_SLEEP_TIMER)  # TODO when to sleep
        et_start = sapi.get_timestamp()
        self.collect_temperature()
        # r_humidity, et_humidity = self.collect_humidity()
        # r_pressure, et_pressure = self.collect_pressure()
        self.collect_air_quality()
        self.collect_light()
        self.collect_window_status()
        self.collect_light_status()
        # print("et_start, et_temp, et_air_quality, et_light, et_window_status, et_light_status, et_end")
        # print(et_start, et_temp, et_air_quality, et_light, et_window_status, et_light_status, sapi.get_timestamp())

        self.counter += 1

        if self.counter == self.arr_size:
            self.counter = 0

            # StrDef.SEN_TEMPERATURE
            # , StrDef.SEN_HUMIDITY
            # , StrDef.SEN_PRESSURE
            # , StrDef.SEN_AIR_QUALITY
            # , StrDef.SEN_LIGHT_LOW
            # , StrDef.SEN_LIGHT_HIGH1
            # , StrDef.SEN_LIGHT_HIGH2

            # array_timestamps_full = [
            #     self.timestamps_temp
            #     , self.timestamps_humidity
            #     , self.timestamps_pressure
            #     , self.timestamps_airquality
            #     , self.timestamps_lowres
            #     , self.timestamps_highres
            #     , self.timestamps_highres2
            # ]

            array_timestamps = [
                [self.timestamps_temp[0]]
                # , [self.timestamps_humidity[0]]
                # , [self.timestamps_pressure[0]]
                , [self.timestamps_airquality[0]]
                , [self.timestamps_lowres[0]]
                , [self.timestamps_highres[0]]
                , [self.timestamps_highres2[0]]
            ]

            # TODO numpy to list conversion?
            array_sensor_values = [
                self.data_temp
                # , self.data_humidity
                # , self.data_pressure
                , self.data_airquality
                , self.data_lowres
                , self.data_highres
                , self.data_highres2
            ]

            data_temp_max_index = self.data_temp.argmax(axis=0)
            data_co2_max_index = self.data_airquality.argmax(axis=0)

            # StrDef.ST_TEMPERATURE_AVG
            # , StrDef.ST_TEMPERATURE_MAX
            # , StrDef.ST_AIR_QUALITY_AVG
            # , StrDef.ST_AIR_QUALITY_WORST
            # , StrDef.ST_LIGHT_AVG
            # , StrDef.ST_ARR_WINDOWN_STATUS
            # , StrDef.ST_ARTIFICIAL_LIGHT_STATUS

            array_stat_values = [
                [self.data_temp.mean()]
                , [self.data_temp.std()]
                , [self.data_temp[data_temp_max_index]]
                , [self.data_airquality.mean()]
                , [self.data_airquality.std()]
                , [self.data_airquality[data_co2_max_index]]
                , [self.data_highres.mean()]  # TODO which light measure to use?
                , [self.data_highres.std()]
                , self.stat_window_status
                , self.stat_light_status
            ]

            array_stat_ts = [
                [self.timestamps_temp[0]]
                , [self.timestamps_temp[0]]
                , [self.timestamps_temp[data_temp_max_index]]
                , [self.timestamps_airquality[0]]
                , [self.timestamps_airquality[0]]
                , [self.timestamps_airquality[data_co2_max_index]]
                , [self.timestamps_highres[0]]  # TODO which light measure to use?
                , [self.timestamps_highres[0]]
                , self.stat_window_status_ts
                , self.stat_light_status_ts
            ]

            data = util.prepare_payload(array_sensor_keys, array_sensor_values, array_timestamps)
            util.send_topics(data, userid, client)

            stat_data = util.prepare_payload(array_stat_keys, array_stat_values, array_stat_ts)
            util.send_topics(stat_data, userid, client)

            print("______")
            print(array_stat_keys, array_stat_values, array_stat_ts)

            self.__reset_values()

    # while 1:
    #     dt_period_end = datetime.now() + timedelta(minutes=1) # TODO correlate with CONST_STAT_TIME
    #     while datetime.now() < dt_period_end:
    #         sensing.periodical_stats()


# TODO search and remove print() commands values
# TODO Remove unnecessary sensor collection
# Opt : send min:second and infer hour from received time : sensor_api.py: get_timestamp():

sensing = SensorDataCollection()

while 1:
    sensing.periodical_stats()

client.loop_forever()

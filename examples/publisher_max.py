import time
import paho.mqtt.client as mqtt
import util
import sensor_api as sapi
import smbus






# The callback for when the client receives a CONNACK response from the server.


client = mqtt.Client()
client.on_connect = util.on_connect
client.on_message = util.on_message


print(util.server)
client.connect(util.server,1883,60)



# intialize sensors, so we can get data out 
bus = smbus.SMBus(1)  # Rev 2 Pi uses 1
sensor = sapi.BH1750(bus)
bme680_sensor = sapi.sensor_bme680()  # Temperature, and Humidity sensor
sgp30_sensor = sapi.sensor_sgp30() # Air quality sensor



counter = 0
userid=util.userid
arr_size = 6
sensor1 = "light_low"
sensor2 = "light_high"
sensor3 = "light_high2"
extra_counter=0
data1 = [0] * arr_size
timestamps1 = [0] * arr_size
data2 = [0] * arr_size
timestamps2 = [0] * arr_size
data3 = [0] * arr_size
timestamps3 = [0] * arr_size
while(1):

    time.sleep(1)

    sample,ts = sensor.measure_low_res()
    data1[counter] = sample
    timestamps1[counter] = ts

    sample, ts = sensor.measure_high_res()
    data2[counter] = sample
    timestamps2[counter] = ts
    sample, ts = sensor.measure_high_res2()
    data3[counter] = sample
    timestamps3[counter] = ts
    sensor.set_sensitivity((sensor.mtreg + 10) % 255)

    counter+=1

    if counter == arr_size:
        extra_counter+=1
        counter = 0
        #Taking max of low_res and sending it
        max_sample=max(data1)
        index = data1.index(max_sample)
        
        sample_ts = [timestamps1[index]]
        max_sample = [str(max_sample)]
        data=util.prepare_payload([sensor1],[max_sample],[sample_ts])
        util.send_topics(data,userid,client)
        data1 = [0] * arr_size
        timestamps1 = [0] * arr_size
        data2 = [0] * arr_size
        timestamps2 = [0] * arr_size
        data3 = [0] * arr_size
        timestamps3 = [0] * arr_size
        print("sent max sample")
        if extra_counter == 10:
            exit()

        

    


client.loop_forever()

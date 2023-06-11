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


#example of getting max sample observed every minute seconds
counter = 0
arr_size = 6
sensor1 = "light_high"
userid=util.userid
extra_counter=0
data_light1 = [0] * arr_size
timestamps_light1 = [0] * arr_size
light_high_threshold=90


while(1):

    time.sleep(1)
    sample, ts = sensor.measure_high_res()
    data_light1[counter%arr_size] = round(sample,2)
    sensor.set_sensitivity((sensor.mtreg + 10) % 255)

    timestamps_light1[counter%arr_size] = ts
    counter+=1

    if int(sample) > light_high_threshold:
        print(data_light1[counter%arr_size], light_high_threshold)
        extra_counter+=1
        counter = 0

        data=util.prepare_payload([sensor1], [data_light1], [timestamps_light1])
        util.send_topics(data,userid,client)

    if extra_counter == 8:
        exit()
        

    
client.loop_forever()

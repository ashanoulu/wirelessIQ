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

######################### Logic for furter programming #######################

counter = 0
arr_size = 5
userid=util.userid
extra_counter=0

# Temperature, pressure and humidty - BME680

counter = 0
arr_size = 6
sensor1 = "lighthigh"
sensor2= "temphigh2"
userid=util.userid
extra_counter=0

data_highres = [0] * arr_size
timestamps_highres = [0] * arr_size
data_highres2 = [0] * arr_size
timestamps_highres2 = [0] * arr_size

while(1):

    time.sleep(1)


    sample, ts = sensor.measure_high_res()
    data_highres[counter] = sample
    timestamps_highres[counter] = ts

    sample, ts = sensor.measure_high_res2()
    data_highres2[counter] = sample
    timestamps_highres2[counter] = ts
    sensor.set_sensitivity((sensor.mtreg + 10) % 255)


    counter+=1

    if counter == arr_size:
        extra_counter+=1
        counter = 0

        data=util.prepare_payload([sensor1, sensor2], [data_highres, data_highres2], [[timestamps_highres[0]], [timestamps_highres2]])
        util.send_topics(data,userid,client)
        data_light = [0] * arr_size
        timestamps_light = [0] * arr_size
        data_temp = [0] * arr_size
        timestamps_temp = [0] * arr_size
        if extra_counter == 10:
            exit()

        

    
client.loop_forever()

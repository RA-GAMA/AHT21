  # importa los móduos de manera independiente, en caso de requerir un objeto global
from machine import Pin, SoftI2C
from aht21 import Aht21
  # declara el objeto del protocolo I2C global
i2c = SoftI2C(sda=Pin(21),scl=Pin(22))
sensor = Aht21(i2c)
  # considera que al comandar una lectura del atributo de temperatura o humedad, el sensor realizará una nueva medición y sus respectivos tiempos de espera
while True:
  temperatura = sensor.temperatura
  humedad = sensor.humedad
  print('Temperatura = {:00.02f}°C\nHumedad = {:00.02f}%'.format(temperatura,humedad))

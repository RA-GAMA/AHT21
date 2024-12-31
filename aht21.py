'''Módulo de control para sensor AHT21
RA-GAMA 2024.
'''

from machine import Pin, SoftI2C
from time import sleep_ms as esperar

class Aht21:
#=========================================== DICCIONARIOS =============================================
    registros = {'reset':0x1b,      # Registro de reinicio forzado (OFF-ON)
        'suave':0xba,               # Registro de reinicio suave.    
        'modo':0x1c,                # Registro del modo de operación
        'leer':0x1e,                # Registro para leer los valores de medición (sin medir de nuevo)
        'medir':0xac,               # Registro para medir de nuevo y re-escribir valores de medicion
        'estado':0x27,              # Registro del estado del sensor
        'inicio':0xbe,              # Registro de inicio del sensor
             }
        # modos de operación posibles para el registro de configuración
    modos = {'dormido':0x00,        # establece el arhorro de energía, (no mide)
            'normal':0x80,   # toma la medición cuando se solicita
            'continuo':0x81  # toma la medición de manera contínua
            } 
        # resolución de la medición del sensor.
    resoluciones = {'normal':0x00,  # Temperatura = [+/- 0.1°C] | Humedad = [+/- 0.1 %]
                    'alta':0x08     # Temperatura = [+/-0.01°C] | Humedad = [+/-0.024%]
                    }
#______________________________________________________________________________________________________
    
    def __init__(self,_i2c:SoftI2C=None,_dir:int=0x38,_res:int=resoluciones['alta']):
        '''inicia un nuevo objeto de control
        _i2c = Protocolo I2C
        _dir = Dirección del I2C
        '''
        self.direccion = _dir   # Dirección del sensor
        if _i2c == None:        # Crea un puerto I2C si no fue dado
            self.i2c = SoftI2C(sda=Pin(21),scl=Pin(22)) 
        else:
            self.i2c = _i2c     # establece el puerto i2c
        self.reset()            # re-establece el sensor
        self.iniciar(_res)      # inicia el sensor
        esperar(10)             # milisegundos
    
    def iniciar(self,_res:int=resoluciones['alta']):
        '''inicia el sensor en la resolución dada o cambia la resolución de medición
            _res = resolución de medición
        '''
        self.escribir([self.registros['inicio'],    # Registro de inicio
                       _res,                        # Resolución deseada
                       0x00])                       # completa el arreglo de 3 valores
    
    def reinicio(self,_suave:bool=False):
        '''Re-inicia el sensor.
        _suave = Reinicia sin apagar el sensor.
        '''
        self.escribir(self.registros['suave' if _suave else 'reset'])
    
    def escribir(self,_data):
        '''escribe datos al sensor
        _ data = datos a enviar => Estructura: [0x0,0x1,0x2]
        '''
        self.i2c.writeto(self.direccion,bytearray(_data))
    
    def medir(self):
        ''' mide la temperatura y humedad del ambiente'''
        self.escribir([0xac,0x33,0x00])
        esperar(80)         #/ milisegundos
        data = self.i2c.readfrom(self.direccion,6)
        self._hum = ((data[1]<<12)|     # mueve el primer valor 12 ceros a la izquierda
                     (data[2]<<4)|      # mueve el segundo valor 4 bits a la izquierda
                     (data[3]>>4))*100/1048576
        self._temp = (((data[3] & 0x0f)<<16) | (data[4]<<8) | data[5])*200/1045876 - 50
            # Verifica la validéz de los datos, revisando el flag de redundancia.
        self.ver_estado()
            # Reintenta la medición en caso de que la medición no sea válida.
        reintentos = 0
        while not self.valido:
                # rompe el ciclo si ha fallado la medición 3 veces seguidas
            if reintentos>3: break
                # reintenta la medición si no se ha alcanzado el límite de 3 veces
            reintentos+=1   #/ aumenta el contador de reintentos
            self.medir()    #/ toma la medición del sensor

    def ver_estado(self):
        '''interpreta el byte del estado del sensor'''
        v = '{:08b}'.format(self.i2c.readfrom_mem(self.direccion,0x27,1)[0])
            # calibración del sensor
        self.calibrado = v>>7&0x01
            # Ocupación del sensor
        self.ocupado = v>>6&0x01
            # redundancia (validez de valores)
        self.valido = v>>2&0x01
    
    def __getattr__(self,_nombre:str):
        '''devuelve valores que no han sido declarados
        _nombre = nombre de atributo (variable) buscado
        '''
        _tlist = ['t','temp','temperatura','temperature']
        _hlist = ['h','hum','humidity','humedad']
        if _nombre in _tlist: self.medir(); return self._temp
        elif _nombre in _hlist: self.medir(); return self._hum
        elif _nombre == 'calibrado': self.ver_estado; return self.calibrado
        elif _nombre == 'ocupado': self.ver_estado; return self.ocupado
        elif _nombre == 'valido': self.ver_estado; return self.valido

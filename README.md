# AHT21

Este módulo permite la medición y comunicación con el sensor AHT21 con un módulo
micropython de manera sencilla.

===========================      TIEMPOS DE ESPERA       ===========================

 - El arranque toma al menos 100ms antes de la medición.
 - La medición, cuando no es configurada de manera contínua, toma 80ms.
____________________________________________________________________________________
=========================== NUMERACIÓN DE BITS DE 1 BYTE ===========================

        MSB ----------------- LSB
        [b7,b6,b5,b4,b3,b2,b1,b0] = 1 Byte
____________________________________________________________________________________

===========================      PROCESO DE MEDICIÓN      ===========================
Para leer los valores de medición, es necesario:

    0 - Energizar el sensor: En caso de hacer el paso 0, continuar hasta el paso 3.
        > Este proceso puede realizarse por medio de una salida digital.
        > Se debe esperar 20ms de reinicio
        > Se debe esperar otros 80ms de medición de datos. (activado automático
        -
    1 - Ordenar que mida los valores:
        > Escribir 2 bytes específicos al registro correspondiente.
       
    2 - Esperar que los valores se actualicen:
        > Esperar al menos 80 milisegundos, lo que tarda en medir valores.
        
    3 - Leer los valores actualizados
        > leer 7 bytes de información, clasificados de la siguiente manera:
            ¬ Byte_0        = Byte de estado
            ¬ Bytes_1,2,3   = Medición de humedad       (2.5 bytes = 20 bits)
            ¬ Bytes_3,4,5   = Medición de temperatura   (2.5 bytes = 20 bits)
            ¬ Byte_6        = Byte de redundancia
        
    4 - Interpretar los valores leídos
        > Byte de estado: 
         Se usan los primeros 3 bits para identificar errores.
            bit_7 = Error de temperatura    (1 = Error)
            bit_6 = Error de humedad        (1 = Error)
            bit_5 = Error de comunicación   (1 = Error)
        > Humedad:
         Se usan los siguientes 2.5 bytes de información, de modo que posea 20 bits.
            [Byte_1 + Byte_2 + 4MSB_Byte_3]
        > Temperatura:
         Se usan los siguientes 2.5 bytes de información, de modo que posea 20 bits.
            [4LSB_Byte_3 + Byte_4 + Byte_5]
        > Byte de redundancia:
         Se usa para verificar la veracidad de los datos transmitidos.
____________________________________________________________________________________

===========================      ORDEN DE MEDICIÓN       ===========================

Se lleva a cabo al enviar 2 valores específicos al registro correspondiente:

    - Los valores son [0X33,0X00]
    - El registro es el [0XAC]
    
    Colocar el registro primero, en caso de enviar todo en 1 solo arreglo:
        > [0XAC,0X33,0X00]
____________________________________________________________________________________

===========================       ORDEN DE RESET         ===========================

Para reiniciar el sensor, sin desenergizarlo, enviar el comando [0xBA].
____________________________________________________________________________________

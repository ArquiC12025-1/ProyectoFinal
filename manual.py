from machine import Pin, PWM
import time
import neopixel
import network
from umqttsimple import MQTTClient


# Pines de motores
M1_IN1 = Pin(18, Pin.OUT)
M1_IN2 = Pin(19, Pin.OUT)
M2_IN1 = Pin(26, Pin.OUT)
M2_IN2 = Pin(25, Pin.OUT)
M3_IN1 = Pin(33, Pin.OUT)
M3_IN2 = Pin(32, Pin.OUT)
M4_IN1 = Pin(23, Pin.OUT)
M4_IN2 = Pin(22, Pin.OUT)

# PWM
ENA1 = PWM(Pin(4), freq=1000)
ENB1 = PWM(Pin(5), freq=1000)
ENA2 = PWM(Pin(12), freq=1000)
ENB2 = PWM(Pin(13), freq=1000)
VELOCIDAD = 900
ENA1.duty(VELOCIDAD)
ENB1.duty(VELOCIDAD)
ENA2.duty(VELOCIDAD)
ENB2.duty(VELOCIDAD)

# Servo
servo = PWM(Pin(2), freq=50)

# NeoPixel
np = neopixel.NeoPixel(Pin(15), 16)

def animar_leds():
    colores = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    for j in range(16):
        for i in range(16):
            np[i] = colores[(i + j) % len(colores)]
        np.write()
        time.sleep(0.05)

def leds_verde():
    for i in range(16):
        np[i] = (0, 255, 0)
    np.write()

def leds_apagar():
    for i in range(16):
        np[i] = (0, 0, 0)
    np.write()

def detener():
    M1_IN1.off(); M1_IN2.off()
    M2_IN1.off(); M2_IN2.off()
    M3_IN1.off(); M3_IN2.off()
    M4_IN1.off(); M4_IN2.off()

def movimiento_base(funcion, codigo):
    funcion()
    time.sleep(0.3)
    detener()

def adelante():
    M1_IN1.on(); M1_IN2.off()
    M2_IN1.on(); M2_IN2.off()
    M3_IN1.on(); M3_IN2.off()
    M4_IN1.on(); M4_IN2.off()

def atras():
    M1_IN1.off(); M1_IN2.on()
    M2_IN1.off(); M2_IN2.on()
    M3_IN1.off(); M3_IN2.on()
    M4_IN1.off(); M4_IN2.on()

def adelante_derecha():
    M1_IN1.on(); M1_IN2.off()
    M3_IN1.on(); M3_IN2.off()
    M2_IN1.off(); M2_IN2.off()
    M4_IN1.off(); M4_IN2.off()

def adelante_izquierda():
    M2_IN1.on(); M2_IN2.off()
    M4_IN1.on(); M4_IN2.off()
    M1_IN1.off(); M1_IN2.off()
    M3_IN1.off(); M3_IN2.off()

def atras_derecha():
    M1_IN1.off(); M1_IN2.off()
    M3_IN1.off(); M3_IN2.off()
    M2_IN1.off(); M2_IN2.on()
    M4_IN1.off(); M4_IN2.on()

def atras_izquierda():
    M1_IN1.off(); M1_IN2.on()
    M3_IN1.off(); M3_IN2.on()
    M2_IN1.off(); M2_IN2.off()
    M4_IN1.off(); M4_IN2.off()

def disparar():
    print("Disparo")
    leds_verde()
    servo.duty(125)
    time.sleep(0.5)
    servo.duty(25)
    animar_leds()



# Menú de consola
acciones = {
    '1': (adelante, 1),
    '2': (atras, 2),
    '3': (adelante_derecha, 3),
    '4': (adelante_izquierda, 4),
    '5': (atras_derecha, 5),
    '6': (atras_izquierda, 6),
    '99': (disparar, 99),
    '0': (detener, 0)
}

print("\n Controles disponibles:")
print("1: Adelante\n2: Atrás\n3: Adelante derecha\n4: Adelante izquierda")
print("5: Atrás derecha\n6: Atrás izquierda\n99: Disparar\n0: Detener")

while True:
    cmd = input("Ingresa comando: ").strip()
    if cmd in acciones:
        funcion, cod = acciones[cmd]
        if cod == 99:
            funcion()
        elif cod == 0:
            funcion()
            cliente.publish(MQTT_METRICA, b'0')
        else:
            movimiento_base(funcion, cod)
    else:
        print("Comando inválido.")

import network
import time
from machine import Pin, PWM
from umqttsimple import MQTTClient

# Configuración WiFi
SSID = 'ARIAS_SUAR'
PASSWORD = '10190910'

# Configuración del broker MQTT
MQTT_BROKER = 'test.mosquitto.org'
MQTT_CLIENT_ID = 'carritoESP32'
MQTT_TOPIC = b'carrito/control'

# Pines de motores
M1_IN1 = Pin(18, Pin.OUT)
M1_IN2 = Pin(19, Pin.OUT)
M2_IN1 = Pin(26, Pin.OUT)
M2_IN2 = Pin(25, Pin.OUT)
M3_IN1 = Pin(33, Pin.OUT)
M3_IN2 = Pin(32, Pin.OUT)
M4_IN1 = Pin(23, Pin.OUT)
M4_IN2 = Pin(22, Pin.OUT)

# Pines PWM para velocidad
ENA1 = PWM(Pin(4), freq=1000)
ENB1 = PWM(Pin(5), freq=1000)
ENA2 = PWM(Pin(12), freq=1000)
ENB2 = PWM(Pin(13), freq=1000)

VELOCIDAD = 900
ENA1.duty(VELOCIDAD)
ENB1.duty(VELOCIDAD)
ENA2.duty(VELOCIDAD)
ENB2.duty(VELOCIDAD)

# Servo para disparo (ej. pin 15)
servo = PWM(Pin(15), freq=50)

# Funciones de movimiento

def detener():
    M1_IN1.off(); M1_IN2.off()
    M2_IN1.off(); M2_IN2.off()
    M3_IN1.off(); M3_IN2.off()
    M4_IN1.off(); M4_IN2.off()

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
    print("Disparo activado")
    servo.duty(125)  # Aproximadamente 180°
    time.sleep(0.6)
    servo.duty(25)   # Aproximadamente 0°
    print("Servo restablecido")

# Conexión WiFi

def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        print("Conectando a WiFi...")
        time.sleep(1)
    print("Conectado a WiFi:", wlan.ifconfig())

# Callback para comandos MQTT

def callback(topic, msg):
    comando = msg.decode()
    print("Comando recibido:", comando)

    if comando == 'adelante': adelante()
    elif comando == 'atras': atras()
    elif comando == 'adelante_derecha': adelante_derecha()
    elif comando == 'adelante_izquierda': adelante_izquierda()
    elif comando == 'atras_derecha': atras_derecha()
    elif comando == 'atras_izquierda': atras_izquierda()
    elif comando == 'disparar': disparar()
    elif comando == 'detener': detener()

# Iniciar
conectar_wifi()
cliente = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)
cliente.set_callback(callback)
cliente.connect()
cliente.subscribe(MQTT_TOPIC)
print("Conectado a MQTT y escuchando en:", MQTT_TOPIC)

# Loop principal
while True:
    cliente.check_msg()
    time.sleep(0.1)

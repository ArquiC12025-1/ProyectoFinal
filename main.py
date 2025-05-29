from machine import Pin, PWM
import time
import neopixel
import network
from umqttsimple import MQTTClient

# --- Configuración MQTT ---
MQTT_BROKER = 'test.mosquitto.org'
MQTT_PORT = 1883
MQTT_CLIENT_ID = 'carritoESP32'

# --- Pines de motores y PWM ---
M1_IN1 = Pin(18, Pin.OUT); M1_IN2 = Pin(19, Pin.OUT)
M2_IN1 = Pin(26, Pin.OUT); M2_IN2 = Pin(25, Pin.OUT)
M3_IN1 = Pin(33, Pin.OUT); M3_IN2 = Pin(32, Pin.OUT)
M4_IN1 = Pin(23, Pin.OUT); M4_IN2 = Pin(22, Pin.OUT)

ENA1 = PWM(Pin(4), freq=1000); ENB1 = PWM(Pin(5), freq=1000)
ENA2 = PWM(Pin(12), freq=1000); ENB2 = PWM(Pin(13), freq=1000)

VELOCIDAD = 900  # Valor inicial por defecto
ENA1.duty(VELOCIDAD); ENB1.duty(VELOCIDAD)
ENA2.duty(VELOCIDAD); ENB2.duty(VELOCIDAD)

# --- Servo y NeoPixel ---
servo = PWM(Pin(2), freq=50)
np = neopixel.NeoPixel(Pin(15), 16)

def animar_leds():
    colores = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
    for j in range(16):
        for i in range(16):
            np[i] = colores[(i + j) % len(colores)]
        np.write()
        time.sleep(0.1)

def leds_verde():
    for i in range(16):
        np[i] = (0, 255, 0)
    np.write()

def leds_apagar():
    for i in range(16):
        np[i] = (0, 0, 0)
    np.write()

# --- Movimiento ---
def detener():
    print("Detener")
    M1_IN1.off(); M1_IN2.off()
    M2_IN1.off(); M2_IN2.off()
    M3_IN1.off(); M3_IN2.off()
    M4_IN1.off(); M4_IN2.off()

def movimiento_base(funcion):
    print("Ejecutando:", funcion.__name__)
    funcion()
    time.sleep(0.3)
    detener()

def adelante():
    print("Adelante")
    M1_IN1.on(); M1_IN2.off()
    M2_IN1.on(); M2_IN2.off()
    M3_IN1.on(); M3_IN2.off()
    M4_IN1.on(); M4_IN2.off()

def atras():
    print("Atrás")
    M1_IN1.off(); M1_IN2.on()
    M2_IN1.off(); M2_IN2.on()
    M3_IN1.off(); M3_IN2.on()
    M4_IN1.off(); M4_IN2.on()

def adelante_derecha():
    print("Adelante derecha")
    M1_IN1.on(); M1_IN2.off()
    M3_IN1.on(); M3_IN2.off()
    M2_IN1.off(); M2_IN2.off()
    M4_IN1.off(); M4_IN2.off()

def adelante_izquierda():
    print("Adelante izquierda")
    M2_IN1.on(); M2_IN2.off()
    M4_IN1.on(); M4_IN2.off()
    M1_IN1.off(); M1_IN2.off()
    M3_IN1.off(); M3_IN2.off()

def atras_derecha():
    print("Atrás derecha")
    M1_IN1.off(); M1_IN2.off()
    M3_IN1.off(); M3_IN2.off()
    M2_IN1.off(); M2_IN2.on()
    M4_IN1.off(); M4_IN2.on()

def atras_izquierda():
    print("Atrás izquierda")
    M1_IN1.off(); M1_IN2.on()
    M3_IN1.off(); M3_IN2.on()
    M2_IN1.off(); M2_IN2.off()
    M4_IN1.off(); M4_IN2.off()

def disparar():
    print("Disparo")
    leds_verde()
    servo.duty(125)
    time.sleep(0.3)
    servo.duty(25)
    print("Servo restablecido")
    animar_leds()

# --- Conexión WiFi ---
def conectar_wifi():
    ssid = 'motorola edge 30 neo_2855'
    password = 'felipe123'
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    print("Conectando al WiFi...")
    for i in range(10):
        if wlan.isconnected():
            print("Conectado a WiFi:", wlan.ifconfig())
            return
        time.sleep(1)
    raise RuntimeError("No se pudo conectar a WiFi")

# --- Callback MQTT ---
def callback(topic, msg):
    global VELOCIDAD
    try:
        comando = msg.decode().strip()
        print("Comando MQTT recibido en", topic.decode(), ":", comando)

        if topic == b'carrito/potencia':
            nueva_velocidad = int(comando)
            if 100 <= nueva_velocidad <= 1023:
                VELOCIDAD = nueva_velocidad
                ENA1.duty(VELOCIDAD); ENB1.duty(VELOCIDAD)
                ENA2.duty(VELOCIDAD); ENB2.duty(VELOCIDAD)
                print("Potencia actualizada a:", VELOCIDAD)
            else:
                print("Potencia fuera de rango:", nueva_velocidad)

        elif topic == b'carrito/control' and comando == '100':
            disparar()
        elif comando == '0':
            detener()
            leds_apagar()
        else:
            valor = int(comando)
            if valor == 10:
                movimiento_base(adelante)
            elif valor == -10:
                movimiento_base(atras)
            elif valor == 3:
                movimiento_base(adelante_derecha)
            elif valor == 4:
                movimiento_base(adelante_izquierda)
            elif valor == 5:
                movimiento_base(atras_derecha)
            elif valor == 6:
                movimiento_base(atras_izquierda)

    except Exception as e:
        print("Error interpretando comando:", e)

# --- Inicialización ---
print("Iniciando conexión WiFi y MQTT...")
conectar_wifi()

cliente = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
cliente.set_callback(callback)
cliente.connect()
print("Conectado al broker MQTT")

# --- Suscripción a los tópicos ---
cliente.subscribe(b'carrito/control')
cliente.subscribe(b'carrito/avance')
cliente.subscribe(b'carrito/otros')
cliente.subscribe(b'carrito/potencia')  # 🆕 Suscribimos a potencia
print("Suscrito a: control, avance, otros, potencia")

# --- Loop principal ---
print("Esperando mensajes...")
while True:
    cliente.check_msg()
    time.sleep(0.1)

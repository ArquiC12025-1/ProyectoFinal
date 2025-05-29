import network
import time

wlan = network.WLAN(network.STA_IF)
wlan.active(False)   # Reinicia por si acaso
time.sleep(1)
wlan.active(True)
time.sleep(1)


nets = wlan.scan()

if not nets:
    print("No se detectaron redes. Verifica la cobertura.")
else:
    print("Redes WiFi disponibles:")
    for net in nets:
        ssid = net[0].decode()
        rssi = net[3]
        print(f"{ssid} (Señal: {rssi} dBm)")

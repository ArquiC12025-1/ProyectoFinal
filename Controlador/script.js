const broker = 'wss://test.mosquitto.org:8081/mqtt';
const topicControl = 'carrito/control';
const topicStatus = 'carrito/status';
const topicAvance = 'carrito/avance';
const topicDatos = 'carrito/datos';
const topicPotencia = 'carrito/potencia';

const client = mqtt.connect(broker);
let avanceTotal = 0;

client.on('connect', function () {
  console.log('Conectado al broker MQTT');
  document.getElementById("status").textContent = "Conectado al broker MQTT";
  document.getElementById("status").style.color = "green";
  client.subscribe(topicStatus);
});

client.on('message', function (topic, message) {
  if (topic === topicStatus) {
    const msg = message.toString();
    document.getElementById("status").textContent = "ℹEstado: " + msg;
    document.getElementById("status").style.color =
      msg === '99' ? "orange" : (msg === '0' ? "red" : "blue");
  }
});

function validarPotencia() {
  const val = parseInt(document.getElementById("potencia").value);
  const error = document.getElementById("potencia-error");
  if (isNaN(val) || val < 100 || val > 1023) {
    error.textContent = "Valor fuera del rango permitido (100-1023)";
  } else {
    error.textContent = "";
  }
}

function enviar(valor) {
  const potencia = parseInt(document.getElementById("potencia").value);
  const errorDiv = document.getElementById("potencia-error");

  if (isNaN(potencia) || potencia < 100 || potencia > 1023) {
    errorDiv.textContent = "Corrige la potencia antes de enviar comandos.";
    return;
  } else {
    errorDiv.textContent = "";
  }

  client.publish(topicPotencia, potencia.toString());

  let topic;
  if (valor === '10' || valor === '-10') {
    avanceTotal += parseInt(valor);
    topic = topicAvance;
    client.publish(topicDatos, avanceTotal.toString());
    client.publish('carrito/otros', valor);
  } else if (valor === '100') {
    topic = topicControl;
    client.publish(topic, valor);
  } else {
    topic = 'carrito/otros';
    client.publish(topic, valor);
  }

  console.log(`Enviado: ${valor}`);
  document.getElementById("status").textContent = `Enviado: ${valor}`;
  document.getElementById("status").style.color = "blue";

  if (valor !== '0' && valor !== '99') {
    setTimeout(() => {
      client.publish(topic, '0');
      document.getElementById("status").textContent = "Enviado: detener";
      document.getElementById("status").style.color = "red";
    }, 300);
  }
}

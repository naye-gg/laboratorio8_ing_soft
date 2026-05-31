import pika
import sys
import os

# Credenciales y host por variables de entorno (no hardcodear secretos).
credenciales = pika.PlainCredentials(
    os.environ.get("RABBITMQ_USER", "students"),
    os.environ.get("RABBITMQ_PASSWORD", ""),
)
parametros = pika.ConnectionParameters(
    os.environ.get("RABBITMQ_HOST", "localhost"), 5672, "/", credenciales
)


def main():
    conexion = pika.BlockingConnection(parametros)
    canal = conexion.channel()

    # 2. Declarar la cola (por si el consumidor se ejecuta antes que el productor)
    nombre_cola = "laboratorio_1"
    canal.queue_declare(queue=nombre_cola, durable=True)

    # 3. Definir qué hacer cuando llega un mensaje
    def callback(ch, method, properties, body):
        print(f" [x] Mensaje recibido: {body.decode()}")

    # 4. Configurar el consumo de la cola
    canal.basic_consume(queue=nombre_cola, on_message_callback=callback, auto_ack=True)

    print(f' [*] Esperando mensajes en la cola "{nombre_cola}". Presiona CTRL+C para salir.')
    canal.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n [*] Saliendo del consumidor...")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

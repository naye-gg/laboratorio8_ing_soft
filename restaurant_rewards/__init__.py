"""Programa de recompensas de restaurantes.

Solucion basada en Arquitectura Hexagonal (puertos y adaptadores) y
Arquitectura Orientada a Eventos (EDA). El paquete se organiza en tres
capas con dependencias que apuntan siempre hacia el dominio:

- ``domain``: reglas de negocio puras (sin dependencias de infraestructura).
- ``application``: casos de uso que orquestan el dominio a traves de puertos.
- ``infrastructure``: adaptadores concretos (RabbitMQ, persistencia, etc.).
"""

__version__ = "1.0.0"

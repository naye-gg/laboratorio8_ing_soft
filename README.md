# Programa de Recompensas de Restaurantes

[![Quality Gate Status](https://sonarqube.ingsoftware.lat/api/project_badges/measure?project=Nayeli_Guerrero_t1&metric=alert_status&token=sqb_f0bb5e2e43df596f4af25b266e875927ab7464f6)](https://sonarqube.ingsoftware.lat/dashboard?id=Nayeli_Guerrero_t1)

> CS3081 - Ingeniería de Software · Tarea 8 — Buen diseño: Cohesión y Acoplamiento

Sistema de fidelización que convierte el consumo en restaurantes afiliados en
**puntos y cashback**, usando **Arquitectura Orientada a Eventos (EDA)** sobre
**RabbitMQ** y **Arquitectura Hexagonal** (puertos y adaptadores).

## Arquitectura

```
restaurant_rewards/
├── domain/           # Núcleo: modelo, eventos, política y PUERTOS (sin infraestructura)
├── application/      # Casos de uso (orquestación)
├── infrastructure/   # Adaptadores: RabbitMQ, persistencia, serialización, config
└── apps/             # Composition root: productor y consumidor ejecutables
```

Detalle completo en [`docs/ARQUITECTURA.md`](docs/ARQUITECTURA.md) y diagrama de
casos de uso en [`docs/casos_de_uso.puml`](docs/casos_de_uso.puml).

## Requisitos

- Python 3.10+
- RabbitMQ accesible (las credenciales del laboratorio vienen por defecto)

## Instalación

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Ejecución

Configura las credenciales por variables de entorno (recomendado):

```bash
export RABBITMQ_HOST=<host_del_broker>      # p. ej. el servidor del curso
export RABBITMQ_PORT=5672
export RABBITMQ_USER=<usuario>
export RABBITMQ_PASSWORD=<password>         # nunca lo subas al repositorio
export RABBITMQ_VHOST=/
```

**Consumidor** (sistema de recompensas) en una terminal:

```bash
python -m restaurant_rewards.apps.consumer_app
```

**Productor** (restaurante registra una cena) en otra terminal:

```bash
python -m restaurant_rewards.apps.producer_app \
    --card 4111111111111111 --restaurant REST-001 --amount 120.50
```

## Pruebas y cobertura

```bash
pytest
```

Genera `coverage.xml` y un reporte en consola. Cobertura actual: **99%**
(mínimo exigido: 85%).

## Estrategia de ramas (Git Flow)

El repositorio sigue un flujo de tres ramas de larga duración:

| Rama | Propósito | Despliegue |
|---|---|---|
| `main` | Código estable y liberado (producción). Solo recibe merges desde `staging`. | Producción |
| `staging` | Pre-producción / QA. Integra `dev` para pruebas de aceptación y análisis de Sonar antes de liberar. | Staging |
| `dev` | Integración del desarrollo diario. Recibe los merges de las ramas `feature/*`. | Desarrollo |

Flujo de trabajo:

```
feature/*  ──merge──▶  dev  ──merge──▶  staging  ──merge──▶  main
                       (integración)    (QA / Sonar)         (release)
```

- Cada nueva funcionalidad se desarrolla en una rama `feature/<nombre>` creada desde `dev`.
- `main` y `staging` se mantienen protegidas; los cambios entran solo vía Pull Request.
- El análisis de SonarQube y la verificación de cobertura ≥85% se ejecutan en `staging` antes de promover a `main`.

## Análisis de calidad (SonarQube)

1. En `sonar-project.properties`, `sonar.projectKey` debe coincidir con el Project key
   creado en SonarQube.
2. Exporta tu token (no se versiona): `export SONAR_TOKEN=<tu_token>`.
3. Ejecuta las pruebas para generar `coverage.xml` y lanza el análisis:

```bash
export SONAR_TOKEN=<tu_token>
pytest
sonar-scanner            # toma SONAR_TOKEN del entorno
```

Atributos evaluados: Reliability, Security, Maintainability y Duplications.

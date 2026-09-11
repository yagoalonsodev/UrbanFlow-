# 🚇 UrbanFlow — Real-Time Urban Mobility Data Platform

Plataforma de ingeniería de datos **end-to-end** orientada al análisis de movilidad urbana y transporte público en tiempo real.

El proyecto integra diferentes fuentes de datos y combina **procesamiento batch y streaming**, permitiendo ingerir, transformar, validar, almacenar y analizar información de transporte de forma automatizada.

El objetivo principal es construir una arquitectura similar a la que podría utilizarse en un entorno profesional de ingeniería de datos, utilizando tecnologías como **Python, Apache Kafka, Apache Spark, Apache Airflow, PostgreSQL, MinIO/S3, Docker y AWS**.

---

## 🎯 Objetivos del proyecto

UrbanFlow tiene como objetivos:

- Integrar diferentes fuentes de datos.

- Construir pipelines de datos automatizados.

- Implementar procesos ETL/ELT.

- Procesar eventos en tiempo real mediante Apache Kafka.

- Utilizar Apache Spark para procesamiento batch y streaming.

- Construir un Data Lake.

- Diseñar un Data Warehouse mediante un modelo dimensional.

- Implementar controles de calidad de datos.

- Automatizar procesos mediante Apache Airflow.

- Generar métricas y datos preparados para analítica.

- Crear dashboards para visualizar el estado de la red de transporte.

- Aplicar buenas prácticas de desarrollo, testing y CI/CD.

- Diseñar una arquitectura preparada para su despliegue en cloud.

---

# 🏗️ Arquitectura

UrbanFlow está compuesto por dos pipelines principales:

### Pipeline Batch

Procesa información histórica procedente de archivos y APIs.

```text

┌─────────────────────┐

│ CSV / GTFS / APIs   │

└──────────┬──────────┘

           │

           ▼

┌─────────────────────┐

│      Python         │

│     Ingestion       │

└──────────┬──────────┘

           │

           ▼

┌─────────────────────┐

│     Data Lake       │

│      Raw Zone       │

└──────────┬──────────┘

           │

           ▼

┌─────────────────────┐

│      Apache         │

│       Spark         │

│   Transformations   │

└──────────┬──────────┘

           │

           ▼

┌─────────────────────┐

│    Data Quality     │

└──────────┬──────────┘

           │

           ▼

┌─────────────────────┐

│   Data Warehouse    │

│     PostgreSQL      │

└─────────────────────┘

```

### Pipeline Streaming

Procesa eventos de transporte prácticamente en tiempo real.

```text

                    ┌──────────────────┐

                    │  API / Generador │

                    │     de eventos   │

                    └────────┬─────────┘

                             │

                             ▼

                    ┌──────────────────┐

                    │ Python Producer   │

                    └────────┬─────────┘

                             │

                             ▼

                    ┌──────────────────┐

                    │      Kafka       │

                    │                  │

                    │ transport-events │

                    └────────┬─────────┘

                             │

                             ▼

                    ┌──────────────────┐

                    │      Spark       │

                    │    Streaming     │

                    └────────┬─────────┘

                             │

                    ┌────────┴─────────┐

                    ▼                  ▼

              ┌───────────┐      ┌────────────┐

              │  MinIO /  │      │ PostgreSQL │

              │    S3     │      │            │

              └───────────┘      └─────┬──────┘

                                       │

                                       ▼

                                ┌─────────────┐

                                │  Metabase   │

                                └─────────────┘

```

---

# ⚡ Procesamiento en tiempo real

Uno de los principales objetivos de UrbanFlow es implementar un pipeline de procesamiento de eventos en tiempo real.

El sistema recibe continuamente eventos representando el estado de vehículos de transporte.

Ejemplo de evento:

```json

{

  "event_id": "evt_982341",

  "vehicle_id": "BUS_1842",

  "line_id": "H12",

  "station_id": "ST_032",

  "timestamp": "2026-09-10T17:45:32",

  "latitude": 41.3874,

  "longitude": 2.1686,

  "delay_seconds": 127,

  "occupancy": 0.82

}

```

El evento sigue el siguiente recorrido:

```text

Fuente de datos

      ↓

Python Producer

      ↓

Apache Kafka

      ↓

Spark Structured Streaming

      ↓

Validación

      ↓

Transformación

      ↓

Almacenamiento

      ↓

Analytics

```

Kafka actúa como sistema de transmisión y distribución de eventos, mientras que Spark Structured Streaming se encarga de procesarlos a medida que llegan.

---

# 📡 Fuentes de datos

UrbanFlow está diseñado para poder trabajar con diferentes fuentes:

- APIs REST.

- GTFS.

- GTFS-Realtime.

- Archivos CSV.

- Datos históricos.

- Generador de eventos para pruebas y desarrollo.

El generador de eventos permite mantener el sistema funcionando incluso cuando una fuente externa no está disponible.

De esta forma, el pipeline puede probarse completamente de manera local.

---

# 🚌 Modelo de datos

Cada evento representa el estado de un vehículo en un momento determinado.

Los principales atributos son:

| Campo | Descripción |

|---|---|

| `event_id` | Identificador único del evento |

| `vehicle_id` | Identificador del vehículo |

| `line_id` | Línea de transporte |

| `station_id` | Estación o parada |

| `timestamp` | Fecha y hora del evento |

| `latitude` | Latitud |

| `longitude` | Longitud |

| `delay_seconds` | Retraso en segundos |

| `occupancy` | Nivel de ocupación |

---

# 📨 Apache Kafka

Kafka se utiliza como plataforma de transmisión de eventos.

## Topics principales

### `transport-events`

Topic principal donde se publican los eventos de transporte.

```text

Python Producer

      │

      ▼

transport-events

      │

      ▼

Spark Streaming

```

### `transport-alerts`

Topic destinado a eventos que cumplen determinadas condiciones de alerta.

Por ejemplo:

```text

delay_seconds > 600

```

o:

```text

occupancy > 0.95

```

### `transport-errors`

Topic utilizado para eventos que no superan las validaciones.

---

# 🔥 Procesamiento con Apache Spark

Spark Structured Streaming consume los eventos publicados en Kafka.

El pipeline realiza:

1. Lectura de eventos.

2. Parseo del JSON.

3. Aplicación del esquema.

4. Validación.

5. Limpieza.

6. Transformación.

7. Cálculo de métricas.

8. Detección de anomalías.

9. Persistencia de resultados.

Entre las métricas calculadas se encuentran:

- Retraso medio.

- Retraso máximo.

- Ocupación media.

- Número de vehículos activos.

- Número de eventos procesados.

- Eventos por minuto.

- Número de incidencias.

- Líneas con mayor retraso.

---

# 🚨 Sistema de alertas

UrbanFlow incorpora reglas para detectar situaciones anómalas.

## Retraso crítico

```text

delay_seconds > 600

```

Genera una alerta de retraso crítico.

## Vehículo saturado

```text

occupancy > 0.95

```

Genera una alerta de ocupación elevada.

## Retraso anómalo

```text

delay_seconds > historical_average * 2

```

Permite detectar retrasos significativamente superiores al comportamiento habitual.

Las alertas se envían a:

```text

transport-alerts

```

---

# 🪣 Data Lake

Para el almacenamiento de datos se utiliza **MinIO** durante el desarrollo local.

MinIO proporciona almacenamiento compatible con el modelo de objetos de Amazon S3.

La estructura del Data Lake será:

```text

urbanflow-data/

├── raw/

│   └── transport/

│       └── year=2026/

│           └── month=09/

│               └── day=10/

│

├── processed/

│   └── transport/

│       └── year=2026/

│           └── month=09/

│               └── day=10/

│

├── curated/

│

└── errors/

```

Los datos procesados se almacenarán preferentemente en formato **Parquet**.

---

# 🧹 Calidad de datos

La plataforma incorpora diferentes controles de calidad.

### Identificadores

```text

event_id no puede ser NULL

event_id debe ser único

```

### Coordenadas

```text

-90 <= latitude <= 90

-180 <= longitude <= 180

```

### Ocupación

```text

0 <= occupancy <= 1

```

### Retraso

```text

delay_seconds >= 0

```

### Timestamp

Los timestamps deben cumplir el formato esperado y representar fechas válidas.

---

# 🏢 Data Warehouse

Los datos preparados se almacenan en PostgreSQL utilizando un modelo dimensional.

UrbanFlow utiliza un **Star Schema**.

```text

                         ┌───────────────┐

                         │   dim_date    │

                         └───────┬───────┘

                                 │

                                 │

┌───────────────┐        ┌───────▼────────┐       ┌────────────────┐

│ dim_vehicle   │───────►│ fact_transport │◄──────│  dim_station   │

└───────────────┘        └───────┬────────┘       └────────────────┘

                                 │

                     ┌───────────┴───────────┐

                     │                       │

              ┌──────▼──────┐        ┌──────▼──────┐

              │   dim_time  │        │   dim_line  │

              └─────────────┘        └─────────────┘

```

## Dimensiones

- `dim_date`

- `dim_time`

- `dim_vehicle`

- `dim_station`

- `dim_line`

## Tabla de hechos

- `fact_transport_events`

La granularidad de la tabla de hechos será:

> Una fila representa un evento correspondiente al estado de un vehículo en un instante determinado.

---

# 📊 Analytics

El Data Warehouse permitirá realizar consultas analíticas como:

### Retraso medio por línea

```sql

SELECT

    l.line_name,

    AVG(f.delay_seconds) AS avg_delay

FROM fact_transport_events f

JOIN dim_line l

    ON f.line_id = l.line_id

GROUP BY l.line_name

ORDER BY avg_delay DESC;

```

### Ocupación media

```sql

SELECT

    l.line_name,

    AVG(f.occupancy) AS avg_occupancy

FROM fact_transport_events f

JOIN dim_line l

    ON f.line_id = l.line_id

GROUP BY l.line_name;

```

### Evolución temporal del retraso

```sql

SELECT

    [d.date](http://d.date),

    AVG(f.delay_seconds) AS avg_delay

FROM fact_transport_events f

JOIN dim_date d

    ON [f.date](http://f.date)_id = [d.date](http://d.date)_id

GROUP BY [d.date](http://d.date)

ORDER BY [d.date](http://d.date);

```

---

# ⏰ Apache Airflow

Airflow será utilizado para la orquestación de los procesos batch.

El DAG principal tendrá una estructura similar a:

```text

extract_data

      ↓

validate_data

      ↓

store_raw_data

      ↓

spark_transform

      ↓

data_quality

      ↓

load_warehouse

      ↓

generate_metrics

```

Airflow permitirá:

- Programar ejecuciones.

- Gestionar dependencias.

- Reintentar tareas fallidas.

- Registrar logs.

- Monitorizar pipelines.

- Automatizar procesos ETL.

El procesamiento streaming mediante Kafka funcionará de manera independiente del DAG batch.

---

# 🐳 Docker

Todos los componentes principales del proyecto estarán disponibles mediante Docker.

El objetivo es poder iniciar el entorno completo con:

```bash

docker compose up -d

```

Servicios previstos:

```text

├── urbanflow-producer

├── kafka

├── spark

├── postgres

├── minio

├── airflow

└── metabase

```

Esto permite reproducir el entorno de desarrollo sin necesidad de instalar manualmente cada tecnología.

---

# 📈 Dashboard

Los datos almacenados en el Data Warehouse serán utilizados para crear un dashboard de movilidad urbana.

## UrbanFlow Mobility Analytics

Principales KPIs:

```text

Vehículos activos

Eventos procesados

Retraso medio

Ocupación media

Alertas críticas

```

Visualizaciones previstas:

- Retraso medio por línea.

- Evolución del retraso.

- Ocupación por línea.

- Vehículos activos.

- Eventos procesados por minuto.

- Estaciones con mayor actividad.

- Alertas generadas.

- Distribución de retrasos.

---

# 🧪 Testing

El proyecto contará con tests automatizados mediante `pytest`.

Se probarán principalmente:

```text

✓ Ingestión de datos

✓ Validación de eventos

✓ Transformaciones

✓ Reglas de calidad

✓ Detección de duplicados

✓ Procesamiento de eventos

✓ Reglas de alertas

```

Ejemplos de casos:

```text

✓ Evento válido aceptado

✓ Coordenadas inválidas rechazadas

✓ Ocupación superior a 100% rechazada

✓ Retraso negativo rechazado

✓ Eventos duplicados detectados

✓ Eventos incompletos rechazados

```

---

# 🔄 CI/CD

El proyecto utilizará GitHub Actions para automatizar las comprobaciones del código.

Pipeline:

```text

Git Push

   │

   ▼

GitHub Actions

   │

   ├── Tests

   ├── Lint

   ├── Type checking

   └── Docker Build

```

El objetivo es garantizar que los cambios introducidos en el repositorio no rompan los componentes existentes.

---

# ☁️ Arquitectura Cloud

Una vez finalizada la arquitectura local, se diseñará una versión orientada a AWS.

Arquitectura prevista:

```text

                     ┌──────────────┐

                     │     API      │

                     └──────┬───────┘

                            │

                            ▼

                     ┌──────────────┐

                     │ Kinesis / MSK│

                     └──────┬───────┘

                            │

                            ▼

                     ┌──────────────┐

                     │   Amazon S3  │

                     └──────┬───────┘

                            │

                            ▼

                     ┌──────────────┐

                     │ AWS Glue     │

                     └──────┬───────┘

                            │

                            ▼

                     ┌──────────────┐

                     │  Redshift    │

                     └──────┬───────┘

                            │

                            ▼

                     ┌──────────────┐

                     │  Analytics   │

                     └──────────────┘

```

La arquitectura local con MinIO permitirá trabajar con una aproximación compatible con S3 antes de realizar el despliegue en AWS.

---

# 🛠️ Tecnologías

## Lenguajes

- Python

- SQL

## Data Engineering

- Apache Kafka

- Apache Spark

- Spark Structured Streaming

- Apache Airflow

- ETL / ELT

- Data Lake

- Data Warehouse

- Dimensional Modeling

## Bases de datos

- PostgreSQL

- SQL

## Almacenamiento

- MinIO

- Amazon S3

## Cloud

- AWS

- Amazon S3

- AWS Glue

- Amazon Redshift

- Kinesis / Amazon MSK

## DevOps

- Docker

- Docker Compose

- Git

- GitHub Actions

## Testing y calidad

- Pytest

- Ruff

- Mypy

## Analytics

- Metabase

---

# 📁 Estructura del proyecto

```text

urbanflow/

│

├── [README.md](http://README.md)

│

├── docs/

│   ├── [architecture.md](http://architecture.md)

│   ├── [data-model.md](http://data-model.md)

│   └── [decisions.md](http://decisions.md)

│

├── architecture/

│   ├── architecture.png

│   └── star-schema.png

│

├── producer/

│   ├── src/

│   ├── tests/

│   ├── Dockerfile

│   └── requirements.txt

│

├── streaming/

│   ├── src/

│   ├── tests/

│   └── Dockerfile

│

├── batch/

│   ├── src/

│   └── tests/

│

├── airflow/

│   └── dags/

│       └── urbanflow_[pipeline.py](http://pipeline.py)

│

├── spark/

│   ├── streaming/

│   └── batch/

│

├── sql/

│   ├── ddl/

│   ├── dimensions/

│   ├── facts/

│   └── analytics/

│

├── data/

│   └── sample/

│

├── tests/

│

├── dashboard/

│

├── docker-compose.yml

├── Dockerfile

├── requirements.txt

├── .env.example

├── .gitignore

│

└── .github/

    └── workflows/

        └── ci.yml

```

---

# 🚀 Instalación

## Requisitos

Antes de comenzar se recomienda tener instalado:

- Docker

- Docker Compose

- Git

- Python 3.12 o superior

No es necesario instalar Kafka, Spark, PostgreSQL, Airflow o MinIO directamente en el sistema, ya que se ejecutarán mediante Docker.

---

## 1. Clonar el repositorio

```bash

git clone [https://github.com/yagoalonsodev/urbanflow.git](https://github.com/yagoalonsodev/urbanflow.git)

cd urbanflow

```

## 2. Crear variables de entorno

```bash

cp .env.example .env

```

Configurar las variables necesarias en `.env`.

## 3. Iniciar los servicios

```bash

docker compose up -d

```

## 4. Comprobar los contenedores

```bash

docker compose ps

```

## 5. Consultar los logs

```bash

docker compose logs -f

```

---

# ⚡ Ejecución del pipeline en tiempo real

Una vez iniciados los servicios:

```text

1. El Producer obtiene/genera eventos

                 ↓

2. Publica eventos en Kafka

                 ↓

3. Kafka almacena y distribuye los eventos

                 ↓

4. Spark Structured Streaming los consume

                 ↓

5. Se validan y transforman

                 ↓

6. Los datos se almacenan

                 ↓

7. PostgreSQL recibe las métricas

                 ↓

8. Metabase muestra los resultados

```

El sistema deberá poder mantenerse funcionando continuamente y procesar nuevos eventos sin necesidad de ejecutar manualmente el pipeline completo.

---

# 📌 Roadmap

## Fase 1 — Preparación

- [ ] Crear estructura del proyecto.

- [ ] Configurar Git.

- [ ] Configurar Docker.

- [ ] Crear documentación inicial.

## Fase 2 — Ingestion

- [ ] Implementar Producer Python.

- [ ] Integrar API/GTFS.

- [ ] Crear generador de eventos.

- [ ] Implementar validación inicial.

- [ ] Añadir logging.

## Fase 3 — Kafka

- [ ] Configurar Kafka.

- [ ] Crear topics.

- [ ] Implementar Producer.

- [ ] Implementar Consumer.

- [ ] Configurar Consumer Groups.

- [ ] Gestionar errores.

## Fase 4 — Streaming

- [ ] Configurar Spark.

- [ ] Implementar Structured Streaming.

- [ ] Consumir eventos Kafka.

- [ ] Transformar eventos.

- [ ] Calcular métricas.

- [ ] Implementar detección de anomalías.

## Fase 5 — Data Lake

- [ ] Configurar MinIO.

- [ ] Crear Raw Zone.

- [ ] Crear Processed Zone.

- [ ] Crear Curated Zone.

- [ ] Implementar almacenamiento Parquet.

- [ ] Particionar datos por fecha.

## Fase 6 — Data Warehouse

- [ ] Diseñar modelo dimensional.

- [ ] Crear dimensiones.

- [ ] Crear tabla de hechos.

- [ ] Implementar procesos de carga.

- [ ] Crear consultas analíticas.

- [ ] Optimizar consultas.

## Fase 7 — Data Quality

- [ ] Implementar validaciones.

- [ ] Detectar duplicados.

- [ ] Detectar valores NULL.

- [ ] Validar rangos.

- [ ] Crear informes de calidad.

- [ ] Gestionar datos rechazados.

## Fase 8 — Airflow

- [ ] Configurar Airflow.

- [ ] Crear DAG.

- [ ] Automatizar ingestion.

- [ ] Automatizar transformaciones.

- [ ] Automatizar data quality.

- [ ] Automatizar carga del DWH.

## Fase 9 — Analytics

- [ ] Configurar Metabase.

- [ ] Crear KPIs.

- [ ] Crear gráficos.

- [ ] Crear dashboard.

- [ ] Analizar tendencias.

## Fase 10 — Testing

- [ ] Tests unitarios.

- [ ] Tests de integración.

- [ ] Tests de calidad de datos.

- [ ] Tests del Producer.

- [ ] Tests del procesamiento.

## Fase 11 — CI/CD

- [ ] GitHub Actions.

- [ ] Ejecutar tests automáticamente.

- [ ] Lint.

- [ ] Type checking.

- [ ] Docker build.

## Fase 12 — Cloud

- [ ] Diseñar arquitectura AWS.

- [ ] Migrar Data Lake a S3.

- [ ] Evaluar AWS Glue.

- [ ] Evaluar Redshift.

- [ ] Evaluar Kinesis/MSK.

- [ ] Documentar arquitectura cloud.

---

# 📚 Principales conceptos aprendidos

Durante el desarrollo del proyecto se trabajarán conceptos fundamentales de ingeniería de datos:

- ETL.

- ELT.

- Batch Processing.

- Stream Processing.

- Event-driven architecture.

- Message brokers.

- Apache Kafka.

- Producer / Consumer.

- Consumer Groups.

- Data Lake.

- Data Warehouse.

- Star Schema.

- Dimensional Modeling.

- Data Quality.

- Data Validation.

- Data Partitioning.

- Parquet.

- Apache Spark.

- Spark Structured Streaming.

- Apache Airflow.

- Docker.

- CI/CD.

- Cloud Computing.

- AWS.

- SQL Analytics.

---

# 🎯 Objetivo profesional

UrbanFlow ha sido diseñado como un proyecto de portfolio para demostrar conocimientos prácticos de **Ingeniería de Datos**, incluyendo el diseño de arquitecturas, integración de fuentes, construcción de pipelines ETL/ELT, procesamiento batch y streaming, almacenamiento de datos, calidad, orquestación, análisis y cloud.

El proyecto busca reproducir, a pequeña escala, problemas y arquitecturas habituales en entornos profesionales de datos.

---

# 👨‍💻 Autor

**Yago Alonso**

Estudiante de Desarrollo de Aplicaciones Multiplataforma (DAM) y desarrollador interesado en **Data Engineering, backend, cloud y sistemas de datos**.

---

## ⭐ Estado del proyecto

🚧 **En desarrollo**

El proyecto se desarrollará progresivamente, incorporando cada componente de la arquitectura de forma independiente antes de integrarlo en el pipeline completo.

---

## Resultados del análisis GTFS de TMB

El análisis se realizó sobre la extracción `data/raw/tmb/2026-09-10/extracted` y está documentado de forma reproducible en [el notebook de análisis](notebooks/gtfs_analysis.ipynb). Se analizaron `agency.txt`, `routes.txt`, `trips.txt`, `stops.txt`, `stop_times.txt` y `calendar.txt`.

### Volumen del feed

| Dataset | Registros | Columnas |
| --- | ---: | ---: |
| `agency` | 1 | 5 |
| `routes` | 116 | 7 |
| `trips` | 60.537 | 7 |
| `stops` | 3.445 | 9 |
| `stop_times` | 1.391.617 | 5 |
| `calendar` | 4 | 10 |

La agencia es TMB, con zona horaria `Europe/Madrid`. El calendario contiene cuatro servicios: dos laborables y dos de fin de semana, con vigencias entre el 9 de septiembre de 2026 y el 27 de marzo de 2027.

### Oferta de transporte y actividad programada

| `route_type` | Medio | Rutas |
| ---: | --- | ---: |
| 3 | Autobús | 105 |
| 1 | Metro | 10 |
| 7 | Funicular/teleférico | 1 |

Las cinco rutas con más viajes programados son las líneas de metro L5 (4.160), L1 (2.370), L3 (2.284), L4 (2.173) y L2 (2.078). El resto del top 20 lo completan las rutas `1.104.1` (1.865), `1.94.1` (1.856), `1.91.1` (1.796), `1.101.1` (1.782), `1.11.1` (1.413), `2.219.3070` (1.193), `2.24.2840` (1.174), `2.220.2999` (1.090), `2.22.3082` (1.077), `2.229.3024` (863), `2.212.2997` (840), `2.214.3012` (804), `2.208.3476` (794), `2.211.3019` (743) y `2.210.3078` (720).

### Calidad e integridad de datos

No se encontraron filas completamente duplicadas en ninguno de los seis datasets. Tampoco hay paradas sin coordenadas ni referencias rotas en las relaciones principales:

| Comprobación | Registros no válidos |
| --- | ---: |
| `trips.route_id` sin ruta existente | 0 |
| `stop_times.stop_id` sin parada existente | 0 |
| `stop_times.trip_id` sin viaje existente | 0 |
| Paradas sin latitud o longitud | 0 |

Los nulos se concentran en campos opcionales o en horarios parciales:

| Dataset | Campo | Nulos | Interpretación |
| --- | --- | ---: | --- |
| `stops` | `stop_url` | 3.445 | Campo opcional no informado. |
| `stops` | `parent_station` | 2.776 | Solo aplica cuando la parada depende de una estación. |
| `stops` | `wheelchair_boarding` | 139 | Accesibilidad no informada. |
| `stop_times` | `arrival_time` | 764.691 | Horario no publicado en esa parada. |
| `stop_times` | `departure_time` | 764.691 | Horario no publicado en esa parada. |

Los horarios ausentes no se imputan: GTFS permite que se interpolen a partir de las paradas con hora publicada cuando el caso de uso lo requiera.

### Transformaciones aplicadas

El pipeline conserva los datos Raw y trabaja sobre una copia. Aplica limpieza de nombres de columna y texto, convierte coordenadas y `stop_sequence` a tipo numérico, elimina duplicados, evita `stop_id` repetidos y descarta filas sin identificadores o sin coordenadas.

Además, después de eliminar espacios, las cadenas vacías se normalizan a `NA`. Esto permite que la regla de eliminación de identificadores las detecte correctamente. En la extracción analizada no se encontraron identificadores vacíos tras esa normalización y ninguna transformación eliminó registros.

| Dataset | Registros iniciales | Registros finales | Eliminados |
| --- | ---: | ---: | ---: |
| `agency` | 1 | 1 | 0 |
| `routes` | 116 | 116 | 0 |
| `trips` | 60.537 | 60.537 | 0 |
| `stops` | 3.445 | 3.445 | 0 |
| `stop_times` | 1.391.617 | 1.391.617 | 0 |
| `calendar` | 4 | 4 | 0 |

En conjunto, el feed está listo para la siguiente etapa de procesamiento. Los controles de transformación quedan como salvaguarda ante futuras descargas con valores vacíos, tipos no normalizados o duplicados.

---

## 📄 Licencia

Este proyecto se desarrolla con fines educativos y de portfolio.

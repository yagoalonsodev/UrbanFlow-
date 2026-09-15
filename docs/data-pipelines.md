# UrbanFlow — Pipelines de datos

## 1. Introducción

UrbanFlow dispone de dos pipelines principales:

1. Pipeline batch para datos GTFS estáticos.
2. Pipeline streaming para datos GTFS-RT.

Ambos pipelines terminan integrándose en el almacenamiento y Data Warehouse de UrbanFlow.

---

# 2. Pipeline Batch

## 2.1 Flujo

```text
TMB
 ↓
download_gtfs
 ↓
validate_data
 ↓
transform_gtfs
 ↓
data_quality
 ↓
validate_processed_snapshot
 ↓
upload_minio
 ↓
load_postgres
 ↓
load_dimensional
```

El pipeline está orquestado mediante Apache Airflow.

---

## 2.2 Descarga

El proceso de descarga obtiene el dataset GTFS proporcionado por TMB.

Antes de procesar los datos se comprueba que la descarga sea válida.

Se realizan comprobaciones sobre:

- Existencia del archivo.
- Formato ZIP.
- Integridad de la descarga.
- Contenido esperado.

---

## 2.3 Análisis exploratorio

El proyecto incluye un notebook para realizar análisis exploratorio de los datos GTFS.

El análisis permite conocer:

- Estructura de los datasets.
- Número de registros.
- Columnas disponibles.
- Valores nulos.
- Distribución de los datos.
- Relaciones entre datasets.

También se incluye una comparación entre procesamiento con Pandas y procesamiento con Spark.

---

## 2.4 Transformación

Los datos GTFS se transforman utilizando PySpark.

El procesamiento prepara los datasets para su almacenamiento y posterior carga en PostgreSQL.

Los datos procesados se almacenan en formato Parquet.

---

## 2.5 Calidad de datos

Antes de cargar los datos en el Data Warehouse se ejecutan controles de calidad.

Estos controles permiten detectar errores en:

- Estructura.
- Valores.
- Relaciones.
- Registros.
- Datos procesados.

Si las validaciones no se superan, el pipeline debe detenerse para evitar introducir datos incorrectos en las siguientes etapas.

---

## 2.6 MinIO

Los datos procesados se almacenan en MinIO.

El almacenamiento permite conservar diferentes etapas del procesamiento:

```text
Raw
Processed
```

Esto proporciona una separación entre los datos originales y los datos transformados.

---

## 2.7 PostgreSQL

Una vez validados los datos, se cargan en PostgreSQL.

La base de datos contiene las tablas originales del modelo GTFS:

```text
agency
calendar
calendar_dates
routes
stops
stop_times
trips
```

También contiene tablas relacionadas con el modelo dimensional:

```text
dim_route
dim_service
dim_stop
fact_trip
fact_stop_time
```

---

# 3. Pipeline Streaming

## 3.1 Flujo

```text
TMB GTFS-RT
     ↓
Python Producer
     ↓
Kafka
     ↓
Spark Structured Streaming
     ↓
PostgreSQL
```

---

## 3.2 Productor

El productor obtiene información GTFS-RT de TMB.

Los eventos se publican en Kafka.

El productor utiliza la dirección interna:

```text
kafka:9093
```

cuando se ejecuta dentro de Docker.

---

## 3.3 Kafka

Kafka actúa como sistema de mensajería.

Los principales topics utilizados por UrbanFlow son:

```text
gtfs-realtime
transport-alerts
transport-errors
```

Esto permite separar los datos normales de transporte, alertas y errores.

---

## 3.4 Spark Structured Streaming

Spark Structured Streaming consume los mensajes de Kafka y procesa los eventos en tiempo real.

El objetivo es transformar los eventos GTFS-RT y prepararlos para su almacenamiento en PostgreSQL.

---

## 3.5 PostgreSQL

Los datos de tiempo real procesados se almacenan en:

```text
realtime_bus_arrivals
```

Esta tabla permite consultar información actualizada de las llegadas de autobuses.

---

# 4. Data Warehouse

UrbanFlow combina los datasets GTFS con información de tiempo real.

La estructura puede representarse como:

```text
                 PostgreSQL
                     │
        ┌────────────┴────────────┐
        │                         │
    GTFS estático             GTFS-RT
        │                         │
        ▼                         ▼
   Modelo dimensional    realtime_bus_arrivals
        │
        ▼
    Analítica
```

---

# 5. Analítica

Las consultas analíticas se almacenan en:

```text
sql/dimensional_analytics.sql
```

Estas consultas permiten analizar los datos del modelo dimensional.

Los resultados pueden ser utilizados por Metabase para generar visualizaciones y dashboards.

---

# 6. Orquestación

Airflow controla la ejecución del pipeline batch.

La arquitectura de ejecución es:

```text
Airflow
   │
   ├── Download
   ├── Validation
   ├── Transformation
   ├── Quality
   ├── MinIO
   ├── PostgreSQL
   └── Dimensional Model
```

Esto permite centralizar la ejecución y controlar las dependencias entre tareas.

---

# 7. Tests

El proyecto incluye tests relacionados con el pipeline de ingestión y transformación.

Los tests permiten comprobar que las principales etapas del procesamiento funcionan correctamente.

También existe una suite específica para las guardrails del agente.

---

# 8. CI

GitHub Actions se utiliza para automatizar comprobaciones del proyecto.

El workflow permite ejecutar automáticamente determinadas validaciones cuando se producen cambios en el repositorio.

El objetivo es detectar errores antes de integrar cambios en la rama principal.
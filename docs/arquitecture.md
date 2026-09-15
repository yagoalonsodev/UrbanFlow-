# UrbanFlow — Arquitectura

## 1. Introducción

UrbanFlow es una plataforma de ingeniería de datos orientada al análisis de movilidad urbana.

El proyecto utiliza datos de transporte público de Barcelona procedentes principalmente de TMB y combina procesamiento batch, procesamiento en tiempo real, almacenamiento de datos, analítica y un agente basado en inteligencia artificial.

La arquitectura está diseñada para reproducir un flujo de datos completo:

```text
Fuentes de datos
      │
      ├── GTFS estático
      │
      └── GTFS-RT
            │
            ▼
      Ingesta de datos
            │
      ┌─────┴─────┐
      │           │
    Batch      Streaming
      │           │
      ▼           ▼
    Spark       Kafka
      │           │
      ▼           ▼
   MinIO       Spark Streaming
      │           │
      └─────┬─────┘
            ▼
       PostgreSQL
            │
      ┌─────┴─────┐
      │           │
   Analítica    Agente IA
      │           │
      ▼           ▼
   Metabase    LangGraph
                  │
                Ollama
```

---

## 2. Componentes principales

### TMB

TMB proporciona los datos de transporte público utilizados por UrbanFlow.

Se utilizan dos tipos principales de información:

- Datos GTFS estáticos.
- Datos GTFS-RT en tiempo real.

Los datos estáticos contienen información como líneas, rutas, paradas, viajes, calendarios y horarios.

Los datos GTFS-RT contienen información dinámica relacionada con el estado actual del transporte.

---

## 3. Ingesta

La ingesta se realiza mediante Python.

El proceso de ingesta se encarga de:

- Descargar los datos.
- Validar los archivos recibidos.
- Comprobar la integridad del ZIP.
- Preparar los datos para su posterior procesamiento.
- Gestionar las rutas de los datasets.

Los datos originales se consideran datos **Raw** y se almacenan en MinIO.

---

## 4. Procesamiento Batch

El procesamiento batch utiliza Apache Spark y PySpark.

El flujo principal es:

```text
GTFS
 ↓
Ingesta
 ↓
Validación
 ↓
Transformación
 ↓
Spark
 ↓
Data Quality
 ↓
Parquet
 ↓
MinIO
 ↓
PostgreSQL
```

Apache Airflow se utiliza para orquestar este flujo.

---

## 5. Procesamiento Streaming

Para los datos GTFS-RT se utiliza una arquitectura de streaming.

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

Kafka actúa como sistema de mensajería entre el productor y el procesamiento.

Los datos procesados se almacenan principalmente en la tabla:

```text
realtime_bus_arrivals
```

También se utilizan topics para gestionar diferentes tipos de mensajes y errores.

---

## 6. Almacenamiento

### MinIO

MinIO funciona como Data Lake compatible con S3.

Se utiliza para almacenar los datos en diferentes etapas del procesamiento.

La separación principal es:

```text
Raw
 ↓
Processed
```

Esto permite conservar los datos originales y almacenar por separado los datos transformados.

### PostgreSQL

PostgreSQL funciona como Data Warehouse de UrbanFlow.

Contiene tanto los datasets GTFS procesados como las tablas dimensionales y los datos de tiempo real.

Entre las tablas utilizadas se encuentran:

- `agency`
- `calendar`
- `calendar_dates`
- `routes`
- `stops`
- `stop_times`
- `trips`
- `dim_route`
- `dim_service`
- `dim_stop`
- `fact_stop_time`
- `fact_trip`
- `realtime_bus_arrivals`

---

## 7. Modelo dimensional

UrbanFlow incorpora un modelo dimensional para facilitar las consultas analíticas.

El modelo utiliza tablas de dimensiones y tablas de hechos.

Ejemplos:

```text
dim_route
dim_service
dim_stop
```

y:

```text
fact_trip
fact_stop_time
```

Este modelo permite realizar consultas sobre rutas, servicios, paradas, viajes y horarios.

---

## 8. Calidad de datos

El proyecto incorpora diferentes validaciones para detectar problemas en los datos.

Las validaciones se ejecutan durante el pipeline y permiten comprobar aspectos como:

- Existencia de archivos.
- Integridad de los datos.
- Estructura esperada.
- Valores nulos.
- Consistencia entre tablas.
- Correcta generación de los datos procesados.

El objetivo es evitar que datos incorrectos lleguen al Data Warehouse.

---

## 9. Analítica

Los datos almacenados en PostgreSQL se utilizan para realizar consultas analíticas.

Los resultados pueden visualizarse mediante Metabase.

La arquitectura analítica es:

```text
PostgreSQL
     ↓
SQL
     ↓
Consultas analíticas
     ↓
Metabase
```

También existe un notebook para el análisis exploratorio del dataset GTFS.

---

## 10. Agente de inteligencia artificial

UrbanFlow incorpora un agente construido con LangGraph.

El agente puede consultar información del sistema y utilizar PostgreSQL como fuente de datos.

La arquitectura es:

```text
Usuario
   ↓
LangGraph Agent
   ↓
Tools
   ↓
PostgreSQL
```

El modelo de lenguaje utilizado actualmente es Ollama ejecutándose de forma nativa en macOS.

```text
LangGraph
    ↓
Ollama
    ↓
llama3.2
```

LangSmith se utiliza para visualizar y monitorizar el funcionamiento del agente.

---

## 11. Observabilidad

LangSmith permite observar las ejecuciones del agente y analizar sus trazas.

La arquitectura de desarrollo actual utiliza:

```text
LangSmith Studio
       ↓
Cloudflare Tunnel
       ↓
urbanflow.controlall.es
       ↓
LangGraph Agent
       ↓
Ollama / PostgreSQL
```

El endpoint público del agente se encuentra detrás de Cloudflare Tunnel.

---

## 12. Infraestructura

La mayor parte de la infraestructura se ejecuta mediante Docker Compose.

Los principales servicios son:

- PostgreSQL
- MinIO
- Kafka
- Spark Streaming
- Airflow
- Metabase
- LangGraph Agent
- Producer GTFS-RT

Ollama se ejecuta de forma nativa en el equipo de desarrollo.

---

## 13. Resumen de tecnologías

| Área | Tecnología |
|---|---|
| Lenguaje | Python |
| Procesamiento | Apache Spark / PySpark |
| Orquestación | Apache Airflow |
| Streaming | Apache Kafka |
| Streaming Processing | Spark Structured Streaming |
| Data Lake | MinIO |
| Data Warehouse | PostgreSQL |
| BI | Metabase |
| IA | LangGraph + Ollama |
| Modelo LLM | llama3.2 |
| Observabilidad IA | LangSmith |
| Contenedores | Docker / Docker Compose |
| CI | GitHub Actions |
| Exposición externa | Cloudflare Tunnel |
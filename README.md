# 🚇 UrbanFlow — Real-Time Urban Mobility Data Platform

Plataforma de **Data Engineering end-to-end** orientada al análisis de movilidad urbana y transporte público de Barcelona.

UrbanFlow integra fuentes **GTFS y GTFS-Realtime de TMB** y combina procesamiento **batch y streaming**, almacenamiento en Data Lake, Data Warehouse dimensional, calidad de datos, orquestación, analítica y un agente de IA capaz de consultar el estado de la plataforma.

El proyecto está diseñado como una arquitectura reproducible mediante Docker y orientada a demostrar conocimientos prácticos de **Data Engineering, Big Data, Cloud, DevOps y AI Agents**.

---

## 🎯 Objetivos

UrbanFlow busca implementar una plataforma completa capaz de:

- Integrar datos GTFS y GTFS-Realtime.
- Construir pipelines batch automatizados.
- Procesar eventos de transporte en tiempo real.
- Utilizar Apache Kafka como sistema de streaming.
- Utilizar Apache Spark para procesamiento distribuido.
- Construir un Data Lake basado en MinIO/S3.
- Construir un Data Warehouse en PostgreSQL.
- Implementar un modelo dimensional Star Schema.
- Aplicar controles de Data Quality.
- Orquestar procesos mediante Apache Airflow.
- Crear analítica y dashboards con Metabase.
- Implementar un agente de IA con LangGraph.
- Utilizar Ollama como LLM local.
- Integrar observabilidad y trazabilidad mediante LangSmith.
- Exponer el agente mediante un endpoint público protegido por Cloudflare Tunnel.
- Automatizar comprobaciones mediante GitHub Actions.
- Mantener una arquitectura preparada para una futura migración a AWS.

---

# 🏗️ Arquitectura

UrbanFlow está compuesto por cuatro bloques principales:

```text
                         ┌──────────────────────┐
                         │       TMB API        │
                         │   GTFS / GTFS-RT     │
                         └──────────┬───────────┘
                                    │
                     ┌──────────────┴──────────────┐
                     │                             │
                     ▼                             ▼
              ┌─────────────┐              ┌─────────────┐
              │    BATCH    │              │  STREAMING  │
              │   Python    │              │   Python    │
              └──────┬──────┘              └──────┬──────┘
                     │                            │
                     ▼                            ▼
              ┌─────────────┐              ┌─────────────┐
              │    MinIO    │              │    Kafka    │
              │  Data Lake  │              └──────┬──────┘
              └──────┬──────┘                     │
                     │                            ▼
                     ▼                     ┌─────────────┐
              ┌─────────────┐              │    Spark    │
              │    Spark    │              │  Streaming  │
              └──────┬──────┘              └──────┬──────┘
                     │                            │
                     └──────────────┬─────────────┘
                                    │
                                    ▼
                            ┌───────────────┐
                            │  PostgreSQL   │
                            │ Data Warehouse│
                            └───────┬───────┘
                                    │
                       ┌────────────┴────────────┐
                       │                         │
                       ▼                         ▼
                ┌─────────────┐          ┌─────────────┐
                │  Metabase   │          │ LangGraph   │
                │  Analytics  │          │    Agent    │
                └─────────────┘          └──────┬──────┘
                                                │
                                                ▼
                                         ┌─────────────┐
                                         │   Ollama    │
                                         │ llama3.2     │
                                         └─────────────┘
```

---

# 📦 Pipeline Batch

El pipeline batch procesa snapshots GTFS de TMB.

```text
TMB GTFS
   ↓
Python ingestion
   ↓
Raw Data Lake
   ↓
Spark transformations
   ↓
Data Quality
   ↓
Processed Parquet
   ↓
MinIO
   ↓
PostgreSQL
   ↓
Dimensional Model
   ↓
Analytics
```

El DAG principal de Airflow es:

```text
urbanflow_batch
```

y ejecuta las diferentes fases del procesamiento:

```text
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

---

# ⚡ Pipeline Streaming

El pipeline streaming procesa llegadas de autobuses mediante GTFS-Realtime.

```text
TMB GTFS-RT
     ↓
Python Producer
     ↓
Apache Kafka
     ↓
Spark Structured Streaming
     ↓
Validation
     ↓
Transformation
     ↓
PostgreSQL
     ↓
Metabase / Analytics
```

El Producer normaliza los eventos antes de publicarlos en Kafka.

Ejemplo:

```json
{
  "timestamp": 1789387200,
  "destination": "Centre",
  "line": "H12",
  "route_id": "2.12.123",
  "stop": "1234",
  "time_in_minutes": 4,
  "time_in_seconds": 240,
  "text_ca": "4 min"
}
```

---

# 📨 Apache Kafka

Kafka actúa como sistema de mensajería y distribución de eventos.

## `gtfs-realtime`

Topic principal de llegadas de autobuses.

```text
Python Producer
      ↓
gtfs-realtime
      ↓
Spark Structured Streaming
```

## `transport-alerts`

Topic utilizado para eventos que cumplen reglas de alerta.

Por ejemplo:

```text
time_in_seconds > 600
```

genera una alerta:

```text
critical_arrival_wait
```

con severidad:

```text
critical
```

## `transport-errors`

Topic utilizado para eventos rechazados por errores de validación.

Esto permite separar:

```text
Eventos válidos
      ↓
Pipeline principal

Eventos inválidos
      ↓
transport-errors
```

---

# 🔥 Apache Spark

Spark se utiliza tanto en procesamiento batch como streaming.

## Batch

Se utiliza para:

- Lectura de datasets GTFS.
- Transformación.
- Limpieza.
- Normalización.
- Validación.
- Generación de datasets procesados.
- Escritura en Parquet.

## Streaming

Spark Structured Streaming consume eventos desde Kafka y realiza:

- Parseo JSON.
- Aplicación de esquemas.
- Validación.
- Transformación.
- Cálculo de métricas.
- Detección de eventos relevantes.
- Persistencia en PostgreSQL.

---

# 🪣 Data Lake

MinIO proporciona el almacenamiento de objetos utilizado durante el desarrollo local.

La arquitectura es compatible conceptualmente con Amazon S3.

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

Los datasets procesados utilizan principalmente formato:

```text
Parquet
```

Los snapshots se particionan por:

```text
year / month / day
```

---

# 🧹 Data Quality

UrbanFlow incorpora controles de calidad en diferentes fases del pipeline.

Entre ellos:

- Validación de identificadores.
- Validación de timestamps.
- Validación de coordenadas.
- Validación de referencias entre datasets.
- Detección de duplicados.
- Detección de valores nulos.
- Validación de rangos.
- Validación de snapshots procesados.
- Separación de eventos inválidos.

En GTFS se comprueban, entre otras relaciones:

```text
trips.route_id → routes.route_id

stop_times.stop_id → stops.stop_id

stop_times.trip_id → trips.trip_id
```

---

# 🏢 Data Warehouse

Los datos históricos se almacenan en PostgreSQL mediante un **Star Schema**.

```text
                    dim_route
                        │
                        │
dim_service ─────── fact_trip ─────── dim_stop
                        │
                        │
                  fact_stop_time
```

## Dimensiones

```text
dim_route
dim_stop
dim_service
```

## Hechos

```text
fact_trip
fact_stop_time
```

Las tablas utilizan surrogate keys para establecer las relaciones dimensionales.

El grain de `fact_trip` es un registro por viaje y snapshot.

El grain de `fact_stop_time` es un registro por parada de un viaje y snapshot.

---

# 📊 Analytics

El Data Warehouse permite realizar consultas analíticas sobre:

- Viajes.
- Rutas.
- Paradas.
- Tipos de transporte.
- Servicios.
- Evolución temporal.
- Llegadas en tiempo real.

Ejemplo:

```sql
SELECT
    r.route_short_name,
    COUNT(f.trip_key) AS total_viajes
FROM fact_trip f
JOIN dim_route r
    ON f.route_key = r.route_key
GROUP BY r.route_key, r.route_short_name
ORDER BY total_viajes DESC
LIMIT 10;
```

---

# 📈 Metabase

Metabase se utiliza como capa de visualización.

El dashboard incluye información histórica y realtime.

Principales indicadores:

```text
Total de viajes
Total de rutas
Total de paradas
Viajes por tipo de transporte
Top de rutas
Top de paradas
Llegadas GTFS-RT
Llegadas por línea
Últimas llegadas
```

---

# ⏰ Apache Airflow

Airflow se utiliza como sistema de orquestación del pipeline batch.

Actualmente el entorno incluye:

```text
Airflow API Server
Airflow Scheduler
Airflow DAG Processor
Airflow Triggerer
Airflow PostgreSQL
```

Airflow permite:

- Ejecutar DAGs.
- Gestionar dependencias.
- Reintentar tareas.
- Registrar logs.
- Monitorizar ejecuciones.
- Automatizar el pipeline batch.

El streaming funciona independientemente del DAG batch.

---

# 🤖 Agente de IA con LangGraph

UrbanFlow incorpora un agente de IA basado en **LangGraph**.

El agente permite consultar información real de UrbanFlow utilizando PostgreSQL como fuente de datos.

Arquitectura:

```text
LangSmith Studio
       │
       ▼
LangGraph Agent Server
       │
       ▼
UrbanFlow Agent
       │
       ├──────────────► PostgreSQL
       │
       ▼
     Ollama
       │
       ▼
   llama3.2
```

El agente utiliza:

- LangGraph.
- LangGraph Agent Server.
- Ollama.
- PostgreSQL.
- SQL read-only.
- Persistencia mediante `thread_id`.
- Guardrails.
- LangSmith Studio.

El modelo utilizado actualmente es:

```text
llama3.2
```

---

# 🧠 Ollama

Ollama se ejecuta **nativamente en macOS**, fuera de Docker.

El agente Docker se conecta al servicio mediante:

```text
http://host.docker.internal:11434
```

Variable de configuración:

```text
OLLAMA_MODEL=llama3.2
```

Esto permite mantener el modelo local y evitar depender de una API externa para las inferencias.

---

# 🔐 Seguridad del agente

El agente está diseñado para realizar consultas de solo lectura.

Se aplican controles para evitar:

- `INSERT`
- `UPDATE`
- `DELETE`
- `DROP`
- múltiples sentencias SQL
- comentarios SQL maliciosos
- acceso a tablas inexistentes

Las respuestas se basan en:

1. El contexto disponible.
2. El esquema real de UrbanFlow.
3. Los resultados obtenidos mediante las herramientas permitidas.

---

# 🔭 LangSmith

LangSmith se utiliza para trabajar con el agente mediante Studio y para observar las ejecuciones.

La arquitectura actual permite utilizar:

```text
LangSmith Studio
       ↓
Public Agent URL
       ↓
Cloudflare Tunnel
       ↓
LangGraph Server
       ↓
UrbanFlow Agent
```

El endpoint público actual es:

```text
https://urbanflow.controlall.es
```

Health check:

```text
GET /ok
```

El endpoint devuelve:

```json
{
  "ok": true
}
```

---

# ☁️ Cloudflare Tunnel

El servidor LangGraph local se expone mediante Cloudflare Tunnel.

```text
Internet
   ↓
urbanflow.controlall.es
   ↓
Cloudflare
   ↓
Cloudflare Tunnel
   ↓
localhost:2024
   ↓
LangGraph Agent Server
```

El túnel permite utilizar el agente desde LangSmith sin desplegar todavía toda la plataforma en AWS.

---

# 🐳 Docker

La infraestructura principal se ejecuta mediante Docker Compose.

Servicios principales:

```text
urbanflow-agent
urbanflow-airflow-apiserver
urbanflow-airflow-dag-processor
urbanflow-airflow-postgres
urbanflow-airflow-scheduler
urbanflow-airflow-triggerer
urbanflow-kafka
urbanflow-metabase
urbanflow-metabase-postgres
urbanflow-minio
urbanflow-postgres
urbanflow-producer
urbanflow-spark-streaming
```

El entorno puede iniciarse con:

```bash
docker compose up -d
```

Comprobar servicios:

```bash
docker compose ps
```

---

# 🧪 Testing y calidad

El proyecto utiliza:

- Pytest.
- Ruff.
- Mypy.
- Python compile checks.
- Docker Compose validation.
- Docker image builds.

Las comprobaciones principales del CI incluyen:

```text
Python compilation
      ↓
Ruff
      ↓
Mypy
      ↓
Docker Compose validation
      ↓
Docker image build
```

El repositorio incluye un `.env.example` con valores de prueba para que GitHub Actions pueda validar Docker Compose sin exponer las credenciales reales del entorno local.

El archivo real:

```text
.env
```

permanece fuera del repositorio.

---

# 🔄 GitHub Actions

UrbanFlow utiliza GitHub Actions para ejecutar automáticamente las comprobaciones del proyecto.

El workflow se ejecuta sobre cambios del repositorio y comprueba:

```text
✓ Python
✓ Ruff
✓ Mypy
✓ Docker Compose
✓ Docker build
```

El entorno CI genera automáticamente un `.env` temporal a partir de:

```text
.env.example
```

Esto evita almacenar secretos reales en GitHub.

---

# 📡 Fuentes de datos

UrbanFlow trabaja principalmente con datos de TMB:

### GTFS

Información estática de:

- Agencias.
- Rutas.
- Viajes.
- Paradas.
- Stop times.
- Calendarios.

### GTFS-Realtime

Información dinámica de:

- Llegadas estimadas.
- Líneas.
- Rutas.
- Paradas.
- Destinos.
- Tiempos estimados.

---

# 📊 Análisis GTFS

El análisis exploratorio del feed GTFS de TMB se encuentra en:

```text
notebooks/gtfs_analysis.ipynb
```

La extracción analizada contiene:

| Dataset | Registros |
|---|---:|
| `agency` | 1 |
| `routes` | 116 |
| `trips` | 60.537 |
| `stops` | 3.445 |
| `stop_times` | 1.391.617 |
| `calendar` | 4 |

El análisis también comprueba integridad referencial, duplicados, valores nulos y consistencia de los datasets.

---

# 📁 Estructura del proyecto

```text
UrbanFlow/
│
├── agent/
│   ├── graph.py
│   └── ...
│
├── dags/
│   └── urbanflow_batch.py
│
├── ingestion/
│
├── processing/
│
├── streaming/
│
├── utils/
│
├── sql/
│   ├── schema.sql
│   ├── dimensional_schema.sql
│   ├── analytics.sql
│   ├── dimensional_analytics.sql
│   └── metabase_dashboard.sql
│
├── tests/
│
├── notebooks/
│   └── gtfs_analysis.ipynb
│
├── docs/
│   ├── agent.md
│   ├── arquitecture.md
│   ├── data-pipelines.md
│   └── installation.md
│
├── data/
│   ├── raw/
│   └── processed/
│
├── docker-compose.yml
├── Dockerfile
├── langgraph.json
├── requirements.txt
├── pytest.ini
├── .env.example
└── .github/
    └── workflows/
        └── ci.yml
```

---

# 🚀 Instalación

## Requisitos

- Docker.
- Docker Compose.
- Git.
- Python 3.12+.
- Ollama si se quiere utilizar el agente localmente.

No es necesario instalar directamente Kafka, Spark, PostgreSQL, Airflow, MinIO o Metabase.

---

## 1. Clonar el repositorio

```bash
git clone https://github.com/yagoalonsodev/UrbanFlow-.git

cd UrbanFlow-
```

---

## 2. Crear el entorno virtual

```bash
python3 -m venv .venv

source .venv/bin/activate
```

---

## 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 4. Crear `.env`

```bash
cp .env.example .env
```

Editar `.env` y añadir las credenciales reales de TMB y las variables necesarias para el entorno local.

**Nunca subir `.env` al repositorio.**

---

## 5. Iniciar UrbanFlow

```bash
docker compose up -d
```

Comprobar:

```bash
docker compose ps
```

---

# 🤖 Ejecutar el agente

Ollama debe estar ejecutándose de forma nativa en macOS.

Comprobar el modelo:

```bash
curl -s http://localhost:11434/api/tags
```

El modelo utilizado actualmente es:

```text
llama3.2
```

El Agent Server está disponible localmente en:

```text
http://localhost:2024
```

Health check:

```bash
curl http://localhost:2024/ok
```

---

# 🌐 LangSmith

El agente puede utilizarse desde LangSmith Studio mediante:

```text
https://urbanflow.controlall.es
```

La URL pública apunta mediante Cloudflare Tunnel al servidor LangGraph local.

---

# 🗺️ Roadmap

## Completado

- [x] Ingestion GTFS.
- [x] Transformación GTFS.
- [x] Data Quality.
- [x] Data Lake con MinIO.
- [x] Procesamiento Parquet.
- [x] PostgreSQL.
- [x] Modelo dimensional.
- [x] Consultas analíticas.
- [x] Kafka.
- [x] Producer GTFS-RT.
- [x] Spark Structured Streaming.
- [x] Eventos realtime.
- [x] Sistema de errores.
- [x] Sistema de alertas.
- [x] Métricas realtime.
- [x] Metabase.
- [x] Airflow.
- [x] Tests.
- [x] Ruff.
- [x] Mypy.
- [x] GitHub Actions.
- [x] Docker Compose.
- [x] LangGraph.
- [x] Ollama local.
- [x] PostgreSQL tools.
- [x] Guardrails del agente.
- [x] LangSmith Studio.
- [x] Cloudflare Tunnel.
- [x] Endpoint público del agente.
- [x] Documentación técnica.

## Próximas fases

- [ ] Migración del Data Lake a Amazon S3.
- [ ] Evaluación de AWS Glue.
- [ ] Evaluación de Redshift.
- [ ] Evaluación de Kinesis / MSK.
- [ ] Despliegue cloud completo.
- [ ] Optimización de costes y recursos.
- [ ] Release final.

---

# ☁️ Arquitectura AWS futura

La arquitectura local está preparada conceptualmente para una futura migración:

```text
TMB API
   ↓
Kinesis / MSK
   ↓
Amazon S3
   ↓
AWS Glue / Spark
   ↓
Amazon Redshift
   ↓
Analytics
```

MinIO se utiliza localmente como alternativa compatible con el paradigma de almacenamiento de objetos de S3.

La infraestructura AWS **todavía no forma parte del despliegue actual**.

---

# 🛠️ Tecnologías

### Data Engineering

- Python.
- SQL.
- Apache Kafka.
- Apache Spark.
- Spark Structured Streaming.
- Apache Airflow.
- ETL / ELT.
- Data Lake.
- Data Warehouse.
- Dimensional Modeling.

### Storage & Databases

- PostgreSQL.
- MinIO.
- Parquet.
- Amazon S3.

### AI

- LangGraph.
- LangSmith.
- Ollama.
- LLMs.
- SQL Agent.
- Guardrails.

### Analytics

- Metabase.

### DevOps

- Docker.
- Docker Compose.
- Git.
- GitHub.
- GitHub Actions.
- Cloudflare Tunnel.

### Quality

- Pytest.
- Ruff.
- Mypy.

---

# 🎓 Objetivo profesional

UrbanFlow ha sido desarrollado como un proyecto de portfolio para demostrar la capacidad de diseñar e implementar una plataforma moderna de **Data Engineering end-to-end**.

El proyecto combina:

```text
Data Ingestion
      +
Batch Processing
      +
Stream Processing
      +
Data Lake
      +
Data Warehouse
      +
Data Quality
      +
Orchestration
      +
Analytics
      +
CI/CD
      +
AI Agent
```

La arquitectura reproduce, a pequeña escala, componentes y problemas habituales en plataformas profesionales de datos.

---

# 👨‍💻 Autor

**Yago Alonso**

Data / AI Developer orientado a:

- Data Engineering.
- Python.
- Big Data.
- Cloud.
- LLMs.
- AI Agents.
- Backend.

GitHub:

```text
https://github.com/yagoalonsodev
```

---

# 📄 Licencia

Proyecto desarrollado con fines educativos y de portfolio.
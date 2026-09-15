# UrbanFlow — Instalación y ejecución

## 1. Requisitos

Para ejecutar UrbanFlow se necesitan:

- macOS, Linux o un entorno compatible.
- Python 3.
- Docker.
- Docker Compose.
- Git.
- Apache Spark.
- Ollama.
- Una cuenta de LangSmith para utilizar las herramientas de observabilidad del agente.

---

## 2. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd UrbanFlow
```

---

## 3. Entorno virtual de Python

Crear el entorno virtual:

```bash
python3 -m venv .venv
```

Activarlo:

```bash
source .venv/bin/activate
```

Las dependencias Python necesarias deben instalarse según la configuración del proyecto.

---

## 4. Variables de entorno

UrbanFlow utiliza variables de entorno para configurar los diferentes servicios.

El archivo `.env` debe mantenerse fuera del repositorio.

Entre las variables utilizadas por el agente se encuentran:

```env
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3.2
LANGSMITH_API_KEY=<API_KEY>
```

La API key de LangSmith es un secreto y nunca debe subirse a Git.

---

## 5. Ollama

Ollama se ejecuta actualmente de forma nativa en macOS.

Comprobar que está disponible:

```bash
curl -s http://localhost:11434/api/tags
```

Comprobar el modelo:

```bash
ollama list
```

El modelo utilizado por defecto es:

```text
llama3.2
```

El contenedor del agente accede al Ollama del host mediante:

```text
http://host.docker.internal:11434
```

---

## 6. Docker Compose

Para iniciar la infraestructura:

```bash
docker compose up -d
```

Comprobar los contenedores:

```bash
docker compose ps
```

Los principales servicios de UrbanFlow se ejecutan mediante Docker.

---

## 7. Comprobar PostgreSQL

PostgreSQL se encuentra disponible en el puerto configurado para el proyecto.

Para acceder al contenedor:

```bash
docker compose exec postgres psql -U urbanflow -d urbanflow
```

---

## 8. Comprobar MinIO

MinIO proporciona el almacenamiento de objetos utilizado como Data Lake.

La interfaz web está disponible en el puerto configurado por Docker Compose.

---

## 9. Comprobar Kafka

Kafka se utiliza para el procesamiento GTFS-RT.

Los productores y consumidores internos utilizan la red Docker.

El producer utiliza:

```text
kafka:9093
```

Mientras que el acceso desde el host utiliza el puerto:

```text
9092
```

---

## 10. Airflow

Airflow orquesta el pipeline batch.

El proceso general es:

```text
Descarga
 ↓
Validación
 ↓
Transformación
 ↓
Data Quality
 ↓
MinIO
 ↓
PostgreSQL
```

La interfaz web de Airflow se encuentra disponible en el puerto configurado en Docker Compose.

---

## 11. Metabase

Metabase se utiliza para consultar y visualizar los datos almacenados en PostgreSQL.

La interfaz está disponible mediante el puerto configurado para el servicio.

---

## 12. LangGraph Agent

El agente se ejecuta dentro de Docker.

El servidor LangGraph utiliza el puerto:

```text
2024
```

Comprobar el servidor:

```bash
curl http://localhost:2024/ok
```

La respuesta esperada es:

```json
{"ok":true}
```

---

## 13. LangSmith Studio

LangSmith Studio se utiliza para interactuar con el agente y observar sus ejecuciones.

El proyecto utiliza:

```text
langgraph.json
```

con una configuración similar a:

```json
{
  "dependencies": ["."],
  "graphs": {
    "urbanflow_agent": "./agent/graph.py:graph"
  },
  "env": ".env"
}
```

El grafo principal es:

```text
urbanflow_agent
```

---

## 14. Cloudflare Tunnel

Durante el desarrollo, el agente puede exponerse mediante Cloudflare Tunnel.

El dominio utilizado es:

```text
https://urbanflow.controlall.es
```

El túnel redirige las peticiones hacia:

```text
http://localhost:2024
```

Por tanto:

```text
Internet
   ↓
Cloudflare
   ↓
urbanflow.controlall.es
   ↓
localhost:2024
   ↓
LangGraph Agent
```

---

## 15. Comprobación completa

Una vez iniciados todos los servicios, se recomienda comprobar:

```bash
docker compose ps
```

Después:

```bash
curl http://localhost:2024/ok
```

Y, si el túnel está activo:

```bash
curl https://urbanflow.controlall.es/ok
```

Ambos endpoints deben responder correctamente.

---

## 16. Seguridad

No se deben subir al repositorio:

- `.env`
- API keys.
- Contraseñas.
- Tokens.
- Credenciales de bases de datos.
- Credenciales de Cloudflare.

El repositorio debe contener únicamente configuraciones que puedan compartirse públicamente.
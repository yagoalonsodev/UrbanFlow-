# UrbanFlow — Agente de inteligencia artificial

## 1. Introducción

UrbanFlow incorpora un agente de inteligencia artificial basado en LangGraph.

El agente permite interactuar con los datos de movilidad almacenados en UrbanFlow y utilizar herramientas conectadas con PostgreSQL.

La arquitectura del agente combina:

- LangGraph.
- LangGraph Agent Server.
- Ollama.
- llama3.2.
- PostgreSQL.
- LangSmith.
- Cloudflare Tunnel.

---

# 2. Arquitectura

```text
                    Usuario
                       │
                       ▼
                 LangSmith Studio
                       │
                       ▼
              LangGraph Agent Server
                       │
             ┌─────────┴─────────┐
             │                   │
             ▼                   ▼
          Ollama             PostgreSQL
             │                   │
             ▼                   │
        llama3.2                 │
             │                   │
             └─────────┬─────────┘
                       ▼
                  Respuesta
```

---

# 3. LangGraph

El grafo principal del proyecto se encuentra en:

```text
agent/graph.py
```

El identificador utilizado para el agente es:

```text
urbanflow_agent
```

La configuración del grafo se define en:

```text
langgraph.json
```

Configuración:

```json
{
  "dependencies": ["."],
  "graphs": {
    "urbanflow_agent": "./agent/graph.py:graph"
  },
  "env": ".env"
}
```

---

# 4. Modelo de lenguaje

El modelo utilizado actualmente es:

```text
llama3.2
```

Se ejecuta mediante Ollama de forma nativa en macOS.

La URL utilizada por el agente dentro de Docker es:

```text
http://host.docker.internal:11434
```

Esto permite que el contenedor de LangGraph acceda al servicio Ollama que se está ejecutando en el equipo host.

---

# 5. Base de datos

El agente dispone de acceso a PostgreSQL mediante las herramientas definidas en:

```text
agent/database.py
```

Esto permite utilizar información real almacenada en UrbanFlow para responder a las consultas.

La base de datos contiene tanto información GTFS estática como datos de transporte en tiempo real.

---

# 6. Guardrails

El agente incorpora controles de seguridad mediante:

```text
agent/guardrails.py
```

Estos controles permiten limitar o validar determinadas interacciones antes de que sean procesadas por el modelo.

Las pruebas correspondientes se encuentran en:

```text
tests/test_agent_guardrails.py
```

---

# 7. Docker

El agente se ejecuta dentro de Docker.

El Dockerfile correspondiente se encuentra en:

```text
agent/Dockerfile
```

El servicio está definido en:

```text
docker-compose.yml
```

El servidor LangGraph utiliza el puerto:

```text
2024
```

Por tanto, desde el equipo local se puede comprobar con:

```bash
curl http://localhost:2024/ok
```

---

# 8. LangSmith

LangSmith se utiliza para:

- Interactuar con el agente.
- Visualizar ejecuciones.
- Analizar trazas.
- Observar el comportamiento del modelo.
- Facilitar la evaluación del agente.

La integración utiliza la variable:

```env
LANGSMITH_API_KEY=<API_KEY>
```

La API key debe mantenerse siempre como secreto.

---

# 9. LangSmith Studio

Durante el desarrollo, LangSmith Studio puede conectarse al Agent Server mediante el endpoint público:

```text
https://urbanflow.controlall.es
```

El dominio se encuentra protegido y publicado mediante Cloudflare.

La comunicación es:

```text
LangSmith Studio
       ↓
Cloudflare
       ↓
urbanflow.controlall.es
       ↓
Cloudflare Tunnel
       ↓
localhost:2024
       ↓
LangGraph Agent
```

---

# 10. Cloudflare Tunnel

El túnel permite acceder al servidor LangGraph desde Internet sin abrir directamente el puerto 2024 al exterior.

El servicio local:

```text
http://localhost:2024
```

se publica mediante:

```text
https://urbanflow.controlall.es
```

La configuración utiliza Cloudflare Tunnel y un registro DNS para el subdominio.

---

# 11. Flujo de una consulta

Cuando un usuario realiza una consulta:

```text
1. El usuario envía una pregunta.
           ↓
2. LangSmith Studio envía la petición.
           ↓
3. Cloudflare recibe la petición.
           ↓
4. Cloudflare Tunnel la dirige al Agent Server.
           ↓
5. LangGraph procesa el estado del agente.
           ↓
6. El agente puede consultar PostgreSQL.
           ↓
7. El agente utiliza Ollama.
           ↓
8. llama3.2 genera la respuesta.
           ↓
9. LangGraph devuelve la respuesta.
           ↓
10. LangSmith registra la ejecución.
```

---

# 12. Comprobación del agente

Comprobar que el servidor está activo:

```bash
curl http://localhost:2024/ok
```

Comprobar el endpoint público:

```bash
curl https://urbanflow.controlall.es/ok
```

Ambos deben devolver:

```json
{"ok":true}
```

---

# 13. Despliegue en LangSmith

El proyecto incluye configuración compatible con LangGraph CLI mediante:

```text
langgraph.json
```

El comando de despliegue es:

```bash
langgraph deploy
```

El despliegue gestionado depende de que la organización de LangSmith tenga habilitada la funcionalidad de Deployments.

El funcionamiento de LangSmith Studio conectado al Agent Server local no depende de este despliegue gestionado.

---

# 14. Seguridad

Las siguientes credenciales nunca deben almacenarse en Git:

```text
LANGSMITH_API_KEY
POSTGRES_PASSWORD
Credenciales de Cloudflare
Credenciales de MinIO
```

Las variables sensibles deben mantenerse en `.env` o en el sistema de gestión de secretos correspondiente.

El archivo `.env` debe estar incluido en `.gitignore`.

---

# 15. Archivos principales del agente

```text
agent/
├── Dockerfile
├── database.py
├── graph.py
└── guardrails.py

tests/
└── test_agent_guardrails.py

langgraph.json
```

---

# 16. Tecnologías

| Componente | Tecnología |
|---|---|
| Framework del agente | LangGraph |
| Agent Server | LangGraph |
| Modelo | llama3.2 |
| Runtime LLM | Ollama |
| Base de datos | PostgreSQL |
| Observabilidad | LangSmith |
| Interfaz | LangSmith Studio |
| Contenedores | Docker |
| Exposición externa | Cloudflare Tunnel |
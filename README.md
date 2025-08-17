# 📚 Biblioteca CLI – KeyDB (Redis) + redis-py

Aplicación de línea de comandos para gestionar una biblioteca personal usando **KeyDB/Redis** como almacenamiento **en memoria**. Cada libro se guarda como **JSON** bajo una clave única (`libro:<uuid>`), con operaciones CRUD rápidas mediante **redis-py**.

---

## 🚀 Características principales
- ➕ **Agregar libros** con título, autor, género y estado (`pendiente`, `leyendo`, `terminado`).
- ✏️ **Actualizar** cualquier campo del libro por su `id`.
- 🗑️ **Eliminar** un libro por `id`.
- 📋 **Listar** todos los libros.
- 🔎 **Buscar** por título, autor o género (coincidencia parcial, insensible a mayúsculas).
- 🚪 **Salir** de la aplicación.

---

## 🛠️ Tecnologías utilizadas
- Python 3.9+
- [KeyDB](https://docs.keydb.dev/) (compatible con protocolo Redis) **o** Redis
- [redis-py](https://redis.readthedocs.io/)
- Opcional: [python-dotenv](https://pypi.org/project/python-dotenv/)

---

## 📦 Instalación y configuración

### 1) Clonar el repositorio
```bash
git clone https://github.com/USUARIO/biblioteca-keydb-cli.git
cd biblioteca-keydb-cli
```

### 2) Crear entorno e instalar dependencias
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
```

### 3) Variables de entorno
Copia y edita el ejemplo:
```bash
cp .env.example .env
```
Variables disponibles:
```
KEYDB_HOST=localhost
KEYDB_PORT=6379
KEYDB_PASSWORD=
KEYDB_DB=0
KEY_PREFIX=libro
```

---

## 🗄️ Cómo ejecutar
```bash
python app.py
```

### Menú principal
```
=== Biblioteca (KeyDB/Redis) ===
1) Agregar nuevo libro
2) Actualizar información de un libro
3) Eliminar libro existente
4) Ver listado de libros
5) Buscar libros
6) Salir
```

---

## 📂 Estructura del proyecto
```
.
├── app.py
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
└── ejemplos
    └── libro_ejemplo.json
```

---

## 🧑‍💻 Código de la aplicación (`app.py`)
(Ver archivo `app.py` en este repositorio.)

---

## 🧪 Ejemplo de documento (`ejemplos/libro_ejemplo.json`)
```json
{
  "id": "a2f1f3f0-1a2b-4c5d-9e7f-123456789abc",
  "titulo": "El nombre del viento",
  "autor": "Patrick Rothfuss",
  "genero": "Fantasía",
  "estado": "pendiente",
  "creado_en": "2025-08-17T16:25:30.123456",
  "actualizado_en": "2025-08-17T16:25:30.123456"
}
```

---

## 📄 `.env.example`
```bash
KEYDB_HOST=localhost
KEYDB_PORT=6379
KEYDB_PASSWORD=
KEYDB_DB=0
KEY_PREFIX=libro
```

---

## 📦 `requirements.txt`
```txt
redis>=5.0,<6
python-dotenv>=1.0,<2
```

---

## 📝 Notas y buenas prácticas
- **KeyDB/Redis en local**: instala KeyDB o Redis y asegura que el puerto `6379` esté disponible.
  - KeyDB (Docker): `docker run -p 6379:6379 eqalpha/keydb`
  - Redis (Docker): `docker run -p 6379:6379 redis`
- **No subas** tu `.env` a GitHub; usa el `.gitignore` provisto.
- **Búsquedas**: se realizan en memoria; para grandes volúmenes considera mantener un índice (ej., Sets por género/autor).
- **Errores comunes**: `ConnectionError/TimeoutError` si el servidor no está activo o credenciales incorrectas; claves inexistentes devolverán `None` / `0` según operación.

---

## 📄 Licencia
MIT

# Trabajo Práctico Backend - Sistema de Prode Deportivo

Este es el backend para un sistema de pronósticos deportivos. Permite administrar usuarios, partidos del fixture, registrar los resultados reales, realizar predicciones y visualizar un ranking basado en los aciertos de cada usuario.

## Cómo configurar el proyecto de forma local

### Prerrequisitos
- Python 3.8+
- MySQL Server

### Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/yapu115/TP_Backend_IDS.git
   cd "Trabajo Practico Backend"
   ```

2. **Crear un entorno virtual:**
   ```bash
   python -m venv .venv
   ```

3. **Activar el entorno virtual:**
   - En Windows (PowerShell):
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   - En Linux/Mac:
     ```bash
     source .venv/bin/activate
     ```

4. **Instalar las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configurar la Base de Datos MySQL:**
   Debes ejecutar el script `initds_db.sql` en tu cliente de MySQL (phpMyAdmin, MySQL Workbench o consola) para crear la base de datos `prode` y sus tablas.
   
   También puedes usar la función integrada desde Python si llamas a `init_db()` desde el archivo `mysql_db.py`.

6. **Ejecutar la aplicación:**
   ```bash
   python app.py
   ```
   El servidor de desarrollo correrá por defecto en `http://127.0.0.1:5000/`.


## Endpoints Principales y Ejemplos de Uso

A continuación se listan ejemplos básicos utilizando peticiones JSON y cURL:

### Usuarios

#### 1. Obtener todos los usuarios (`GET /usuarios`)
```bash
curl -X GET http://127.0.0.1:5000/usuarios
```

#### 2. Crear un usuario (`POST /usuarios`)
```bash
curl -X POST http://127.0.0.1:5000/usuarios \
     -H "Content-Type: application/json" \
     -d '{"nombre": "Maria Lopez", "email": "maria@app.com"}'
```

#### 3. Editar un usuario (`PUT /usuarios/<id>`)
```bash
curl -X PUT http://127.0.0.1:5000/usuarios/1 \
     -H "Content-Type: application/json" \
     -d '{"nombre": "Admin Actualizado", "email": "admin_nuevo@prode.com"}'
```

### Partidos del Fixture

#### 4. Obtener partidos con paginación y filtros (`GET /partidos`)
Admite los parámetros `equipo`, `fecha`, `fase`, `_limit` y `_offset`.
```bash
curl -X GET "http://127.0.0.1:5000/partidos?equipo=Argentina&_limit=10&_offset=0"
```

#### 5. Crear un partido nuevo (`POST /partidos`)
Selecciona una de las fases: 'grupos', 'dieciseisavos', 'octavos', 'cuartos', 'semis', 'final'.
```bash
curl -X POST http://127.0.0.1:5000/partidos \
     -H "Content-Type: application/json" \
     -d '{
           "equipo_local": "Argentina",
           "equipo_visitante": "Uruguay",
           "fecha": "2026-06-25",
           "fase": "octavos"
         }'
```

#### 6. Registrar / Actualizar el resultado real del partido (`PUT /partidos/<id>/resultado`)
```bash
curl -X PUT http://127.0.0.1:5000/partidos/1/resultado \
     -H "Content-Type: application/json" \
     -d '{"goles_local": 2, "goles_visitante": 1}'
```

### Predicciones y Prode

#### 7. Hacer una predicción (`POST /partidos/<id>/prediccion`)
Registra la predicción de un usuario específico para un partido antes de que se juegue.
```bash
curl -X POST http://127.0.0.1:5000/partidos/1/prediccion \
     -H "Content-Type: application/json" \
     -d '{
           "id_usuario": 1,
           "local": 2,
           "visitante": 0
         }'
```

### Ranking

#### 8. Obtener tabla de posiciones (`GET /ranking`)
Calcula e imprime los puntos correspondientes (3 pts si acertó exacto, 1 punto si acertó al ganador). Soporta paginación.
```bash
curl -X GET "http://127.0.0.1:5000/ranking?_limit=10&_offset=0"
```
========================================================= PROYECTO: API DE GESTIÓN DE CITAS (FASTAPI)

Este documento explica la estructura, funcionamiento y despliegue
de la API de gestión de citas, cubriendo todos los entregables
de la práctica.

--- 1. FUNCIONALIDAD DE LA APLICACIÓN ---

La aplicación es una API RESTful construida con FastAPI que permite
realizar operaciones CRUD (Crear, Leer, Borrar) sobre citas médicas.
Utiliza SQLAlchemy para conectarse a una base de datos SQLite (citas.db).

La API expone los siguientes endpoints (rutas):

POST /api/citas

Descripción: Crea una nueva cita.

Input (JSON): {"paciente": "string", "fecha": "YYYY-MM-DDTHH:MM:SS", "motivo": "string"}

Output (JSON): La cita recién creada con su ID.


GET /api/citas

Descripción: Obtiene una lista de todas las citas.

Output (JSON): Una lista [ ] de objetos de citas.


GET /api/citas/{cita_id}

Descripción: Obtiene una cita específica por su ID.

Output (JSON): El objeto de la cita. Devuelve 404 si no se encuentra.


DELETE /api/citas/{cita_id}

Descripción: Borra una cita específica por su ID.

Output (JSON): Mensaje de confirmación. Devuelve 404 si no se encuentra.


--- 2. CÓMO EJECUTAR LA APLICACIÓN (LOCAL) ---

Para ejecutar la API en tu máquina local para desarrollo:

Abre una terminal (PowerShell o CMD) en la raíz del proyecto.

Crea y activa un entorno virtual de Python:
(Si no tienes la carpeta 'venv')

python -m venv venv
(Para activar)
.\venv\Scripts\Activate.ps1
(NOTA: Si da error en PowerShell, ejecuta primero: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass)

Instala todas las dependencias necesarias:

pip install -r requirements.txt

Ejecuta el servidor de desarrollo Uvicorn:

uvicorn app.main:app --reload

¡Listo! Abre tu navegador y ve a https://www.google.com/search?q=http://127.0.0.1:8000/docs
Allí verás la documentación interactiva de la API, donde podrás
probar todos los endpoints directamente, desplegando el endpoint que quieras utilizar, y seleccionando la opción try it out.

--- 3. CÓMO EJECUTAR LOS TESTS ---

El proyecto incluye una batería de pruebas unitarias y de integración
para verificar que todos los endpoints funcionan como se espera.

Asegúrate de tener el entorno virtual activado (ver paso 2 anterior).

Asegúrate de haber instalado las dependencias (ver paso 3 anterior).

Ejecuta el comando pytest en la terminal:

pytest

Pytest descubrirá y ejecutará automáticamente todos los tests en
la carpeta /tests.

(Opcional) Para un informe más detallado (verbose):

pytest -v

(Opcional) Para generar un informe de cobertura (Code Coverage):

pip install pytest-cov
pytest --cov=app --cov-report=html
(Esto crea una carpeta 'htmlcov'. Abre 'index.html' en tu navegador
para ver qué líneas de tu código han sido probadas).

--- 4. GIT HOOKS (AUTOMATIZACIÓN LOCAL) ---

El proyecto está configurado con Git Hooks para asegurar la calidad
del código antes de que se suba al repositorio. Los scripts se
encuentran en la carpeta /.githooks.

IMPORTANTE: Para activar estos hooks, ejecuta este comando UNA SOLA VEZ:

git config core.hooksPath .githooks

Los hooks configurados son:

pre-commit:

Se ejecuta ANTES de cada 'git commit'.

Tareas:

Formatea el código con 'black'.

Comprueba errores de estilo con 'flake8'.

Ejecuta 'pytest' para asegurar que no se ha roto nada.

Resultado: Si algo falla (formato, linting o tests), el commit SE ABORTA.

post-commit:

Se ejecuta DESPUÉS de un commit exitoso.

Tarea: Escribe un registro del commit (autor, hash) en el
archivo 'commit_history.log' para auditoría.

pre-push:

Se ejecuta ANTES de 'git push', como última barrera de seguridad.

Tarea: Vuelve a ejecutar 'pytest'.

Resultado: Si un test falla, el push SE ABORTA, evitando subir código roto.

post-push:

Se ejecuta DESPUÉS de un 'git push' exitoso.

Tarea: Muestra un mensaje de confirmación en la consola.

--- 5. PIPELINE CI/CD (GITHUB ACTIONS) ---

El archivo .github/workflows/ci.yml define el pipeline de
Integración Continua y Despliegue Continuo (CI/CD) que se ejecuta
en los servidores de GitHub.

Este pipeline se dispara automáticamente CADA VEZ que se hace un
'push' a la rama 'main' (o 'master').

El pipeline tiene dos trabajos (jobs) que se ejecutan en secuencia:

Job: "test-and-lint"

Tareas:

Configura un servidor Ubuntu.

Instala Python y las dependencias (usando la caché).

Ejecuta 'flake8' y 'black --check'.

Ejecuta 'pytest'.

Resultado: Si algún paso falla, el pipeline se detiene y
notifica el error.

Job: "build-and-push-docker"

Tareas:

SOLO se ejecuta si el job "test-and-lint" ha sido exitoso.

Inicia sesión en GitHub Container Registry (GHCR).

Construye la imagen Docker de la aplicación (usando el Dockerfile).

"Despliega" (publica) la imagen en el registro de contenedores
del repositorio, etiquetada con el hash del commit.


from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware
from app.features.auth.routes import auth_routes
from app.features.spots.routes import spots_routes
from app.features.users.routes import users_routes
from app.features.exits.routes import exits_routes
from app.features.tariffs.routes import tariffs_routes
from app.features.entries.routes import entries_routes
from app.features.parking.routes import parking_routes
from app.features.payments.routes import payments_routes
from app.features.floors.routes import floors_routes
from app.features.countries.routes import countries_routes

from app.core.database import get_connection
from app.core.redis import close_redis, init_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialización de recursos
    redis = await init_redis(app)
    await FastAPILimiter.init(redis)
    yield
    # Cierre de recursos
    await close_redis()

# Instancia principal de la app FastAPI
app = FastAPI(
    title="API con FastAPI y MySQL",
    description="Api para tracklinker",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Endpoint para probar conexión a la base de datos
@app.get("/ping-db")
def ping_db():
    connection = get_connection()
    if connection:
        connection.close()
        return {
            "status": "Conexion Exitosa a la base de datos"
        }
    else:
        return {
            "status": "Error al intentar conectarse a la base de datos"
        }


# Endpoint raíz para probar ejecución de la API
@app.get("/")
def root():
    return {
        "message": "API funcionando"
    }


# Rutas de autenticación
app.include_router(auth_routes.router)
# Rutas de usuarios
app.include_router(users_routes.router)
# Rutas de entradas
app.include_router(entries_routes.router)
# Rutas de salidas
app.include_router(exits_routes.router)
# Rutas de parking
app.include_router(parking_routes.router)
# Rutas de payments
app.include_router(payments_routes.router)
# Rutas de spots
app.include_router(spots_routes.router)
# Rutas de tariffs
app.include_router(tariffs_routes.router)
# Rutas de floors
app.include_router(floors_routes.router)
# Rutas de countries
app.include_router(countries_routes.router)

from importlib import import_module
from pkgutil import iter_modules
import signal
import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.database import client

app = FastAPI(
    default_response_class=JSONResponse,
    title="AuthMeAPI"
)

for _, name, ispackage in iter_modules(path=['src/routers'], prefix='src.routers.'):
    if not ispackage and not name.startswith('_'):
        module = import_module(name)
        app.include_router(module.router)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = round(time.time() - start_time, 5)
    response.headers["X-Process-Time"] = str(process_time)
    return response

async def handle_SIGINT(sig, frame):
    client.close()
    print(f'Gracefully closing database connection...')
    
signal.signal(signal.SIGINT, handle_SIGINT)
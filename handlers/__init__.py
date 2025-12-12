import pkgutil
import importlib
from aiogram import Router

from coingecko.coingecko_client import cg_client

global_router = Router()
client = cg_client

for module_info in pkgutil.iter_modules(__path__):
    module = importlib.import_module(f"{__name__}.{module_info.name}")

    if hasattr(module, "router"):
        global_router.include_router(module.router)
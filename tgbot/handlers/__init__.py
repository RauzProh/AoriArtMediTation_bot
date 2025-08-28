from .main_menu import main_menu_router
from .admin import admin_router
# from tgbot.handlers.admin import admin_router
from .helpers import helpers_router
from .scenario_update import scenario_router
from .access import access_router
from .mailing import router

routers_list = [
    router,
    scenario_router,
    admin_router,
    main_menu_router,
    helpers_router,
    access_router,
]

__all__ = [
    "routers_list",
]

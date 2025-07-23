from .throttling import ThrottlingMiddleware
from .role_access import RoleAccessMiddleware

def register_middlewares(dp):
    dp.middleware.setup(ThrottlingMiddleware())
    dp.middleware.setup(RoleAccessMiddleware())
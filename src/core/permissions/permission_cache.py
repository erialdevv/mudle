import json
from redis.asyncio import Redis
from repositories.roles.permissions import repo_get_permissions_by_rolid

_TTL_SECONDS = 3600


def _key(rol_id: int) -> str:
    return f"role:permissions:{rol_id}"


async def get_role_permissions(redis: Redis, conn, rol_id: int) -> dict:

    cached = await redis.get(_key(rol_id))
    if cached is not None:
        return json.loads(cached)

    result: dict = await repo_get_permissions_by_rolid(conn, p_rolid=rol_id)
    permissions: dict = dict(result["data"])

    await redis.set(_key(rol_id), json.dumps(permissions), ex=_TTL_SECONDS)

    return permissions


async def invalidate_role(redis: Redis, rol_id: int) -> None:
    await redis.delete(_key(rol_id))

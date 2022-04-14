import asyncpg
from simple_print import sprint

from settings import DATABASE_URI


async def get_user_by_monitor_id(monitor_id):
    sprint(f"get_user_by_monitor_id monitor_id={monitor_id}", c="yellow", s=1, p=1)

    conn = await asyncpg.connect(DATABASE_URI)
    user = None

    try:
        sql_query = f'SELECT * FROM "monitoring_monitor" WHERE id={monitor_id};'
        monitor = await conn.fetchrow(sql_query)
        created_by_id = monitor["created_by_id"]
        sql_query = f'SELECT * FROM "user_profile_userprofile" LEFT JOIN "auth_user" ON "user_profile_userprofile"."user_id"="auth_user"."id" WHERE "user_profile_userprofile"."id"={created_by_id};'
        user = await conn.fetchrow(sql_query)
    except Exception as e:
        sprint(e, c="red", s=1, p=1)
    finally:
        await conn.close()

    sprint(f"get_user_by_monitor_id user={user}", c="cyan", s=1, p=1)
    return user

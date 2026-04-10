from typing import cast

from aiopg import Pool
from psycopg2.extras import DictCursor

from database.models import ReturningResponse, Team, TeamMember

class TeamManager:
    def __init__(self, pool: Pool) -> None:
        self.pool: Pool = pool
        
    async def add_team(self, name: str, created_by: int) -> ReturningResponse[Team]:
        try:
            async with self.pool.acquire() as connection:
                async with connection.cursor(cursor_factory=DictCursor) as cursor:
                    await cursor.execute(
                        "INSERT INTO team (name, created_by) VALUES (%s, %s) RETURNING *",
                        (name, created_by)
                    )
                    result = await cursor.fetchone()
                    if result:
                        return {"success": True, "data": cast(Team, dict(result)), "error": None}
                    return {"success": False, "data": None, "error": "Failed to add team"}
        except Exception as e:
            return {"success": False, "data": None, "error": str(e)}
        
    async def remove_team(self, team_id: int) -> ReturningResponse[Team]:
        try:
            async with self.pool.acquire() as connection:
                async with connection.cursor(cursor_factory=DictCursor) as cursor:
                    await cursor.execute("DELETE FROM team WHERE team_id = %s RETURNING *", (team_id,))
                    result = await cursor.fetchone()
                    if result:
                        return {"success": True, "data": cast(Team, dict(result)), "error": None}
                    return {"success": False, "data": None, "error": "Team not found"}
        except Exception as e:
            return {"success": False, "data": None, "error": str(e)}
        
    async def edit_team(self, team_id: int, new_name: str) -> ReturningResponse[Team]:
        try:
            async with self.pool.acquire() as connection:
                async with connection.cursor(cursor_factory=DictCursor) as cursor:
                    await cursor.execute(
                        "UPDATE team SET name = %s WHERE team_id = %s RETURNING *",
                        (new_name, team_id)
                    )
                    result = await cursor.fetchone()
                    if result:
                        return {"success": True, "data": cast(Team, dict(result)), "error": None}
                    return {"success": False, "data": None, "error": "Team not found"}
        except Exception as e:
            return {"success": False, "data": None, "error": str(e)}
    
    async def add_member(self, team_id: int, nama: str, rank: str, jabatan: str, user_id: int | None) -> ReturningResponse[TeamMember]:
        try:
            async with self.pool.acquire() as connection:
                async with connection.cursor(cursor_factory=DictCursor) as cursor:
                    await cursor.execute(
                        "INSERT INTO team_member (team_id, nama, rank, jabatan, user_id) VALUES (%s, %s, %s, %s, %s) RETURNING *",
                        (team_id, nama, rank, jabatan, user_id)
                    )
                    result = await cursor.fetchone()
                    if result:
                        return {"success": True, "data": cast(TeamMember, dict(result)), "error": None}
                    return {"success": False, "data": None, "error": "Failed to add member"}
        except Exception as e:
            return {"success": False, "data": None, "error": str(e)}
    
    async def edit_member(self, member_id: int, team_id: int, nama: str, rank: str, jabatan: str, user_id: int | None) -> ReturningResponse[TeamMember]:
        try:
            async with self.pool.acquire() as connection:
                async with connection.cursor(cursor_factory=DictCursor) as cursor:
                    await cursor.execute(
                        "UPDATE team_member SET team_id = %s, nama = %s, rank = %s, jabatan = %s, user_id = %s WHERE id = %s RETURNING *",
                        (team_id, nama, rank, jabatan, user_id, member_id)
                    )
                    result = await cursor.fetchone()
                    if result:
                        return {"success": True, "data": cast(TeamMember, dict(result)), "error": None}
                    return {"success": False, "data": None, "error": "Member not found"}
        except Exception as e:
            return {"success": False, "data": None, "error": str(e)}
        
    async def remove_member(self, member_id: int) -> ReturningResponse[TeamMember]:
        try:
            async with self.pool.acquire() as connection:
                async with connection.cursor(cursor_factory=DictCursor) as cursor:
                    await cursor.execute("DELETE FROM team_member WHERE id = %s RETURNING *", (member_id,))
                    result = await cursor.fetchone()
                    if result:
                        return {"success": True, "data": cast(TeamMember, dict(result)), "error": None}
                    return {"success": False, "data": None, "error": "Member not found"}
        except Exception as e:
            return {"success": False, "data": None, "error": str(e)}
        
    async def member_login(self, member_id: int) -> ReturningResponse[TeamMember]:
        try:
            async with self.pool.acquire() as connection:
                async with connection.cursor(cursor_factory=DictCursor) as cursor:
                    await cursor.execute(
                        "UPDATE team_member SET last_login = NOW() WHERE id = %s RETURNING *",
                        (member_id,)
                    )
                    result = await cursor.fetchone()
                    if result:
                        return {"success": True, "data": cast(TeamMember, dict(result)), "error": None}
                    return {"success": False, "data": None, "error": "Member not found"}
        except Exception as e:
            return {"success": False, "data": None, "error": str(e)}
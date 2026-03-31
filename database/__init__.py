"""
Copyright © Krypton 2019-Present - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized Discord bot in Python

Version: 6.5.0
"""

import aiopg
from psycopg2.extras import DictCursor


class DatabaseManager:
    def __init__(self, *, pool: aiopg.Pool) -> None:
        self.pool = pool

    async def add_warn(
        self, user_id: int, server_id: int, moderator_id: int, reason: str
    ) -> int:
        """
        This function will add a warn to the database.

        :param user_id: The ID of the user that should be warned.
        :param reason: The reason why the user should be warned.
        """
        async with self.pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    "SELECT id FROM warns WHERE user_id=%s AND server_id=%s ORDER BY id DESC LIMIT 1",
                    (
                        user_id,
                        server_id,
                    ),
                )
                result = await cursor.fetchone()
                warn_id = result[0] + 1 if result is not None else 1
                await cursor.execute(
                    "INSERT INTO warns(id, user_id, server_id, moderator_id, reason) VALUES (%s, %s, %s, %s, %s)",
                    (
                        warn_id,
                        user_id,
                        server_id,
                        moderator_id,
                        reason,
                    ),
                )
            return warn_id

    async def remove_warn(self, warn_id: int, user_id: int, server_id: int) -> int:
        """
        This function will remove a warn from the database.

        :param warn_id: The ID of the warn.
        :param user_id: The ID of the user that was warned.
        :param server_id: The ID of the server where the user has been warned
        """
        async with self.pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    "DELETE FROM warns WHERE id=%s AND user_id=%s AND server_id=%s",
                    (
                        warn_id,
                        user_id,
                        server_id,
                    ),
                )
                await cursor.execute(
                    "SELECT COUNT(*) FROM warns WHERE user_id=%s AND server_id=%s",
                    (
                        user_id,
                        server_id,
                    ),
                )
                result = await cursor.fetchone()
                return result[0] if result is not None else 0

    async def get_warnings(self, user_id: int, server_id: int) -> list:
        """
        This function will get all the warnings of a user.

        :param user_id: The ID of the user that should be checked.
        :param server_id: The ID of the server that should be checked.
        :return: A list of all the warnings of the user.
        """
        async with self.pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    "SELECT user_id, server_id, moderator_id, reason, EXTRACT(EPOCH FROM created_at)::bigint, id FROM warns WHERE user_id=%s AND server_id=%s",
                    (
                        user_id,
                        server_id,
                    ),
                )
                result = await cursor.fetchall()
                return list(result)

    async def add_team_member(self, nama: str, rank: str, jabatan: str, user_id:int, guild_id: int) -> dict:
        """
        Fungsi ini akan menambahkan member ke dalam database
        :param user_id: user_id dari member discord
        :param nama: Nama member
        :param rank: Rank member
        :param jabatan: Jabatan User di team
        :return:
        """
        try:
            async with self.pool.acquire() as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute(
                        "INSERT INTO team_member(nama, rank, jabatan, user_id, guild_id) VALUES (%s, %s, %s, %s, %s)",
                        (
                            nama,
                            rank,
                            jabatan,
                            user_id,
                            guild_id
                        ),
                    )
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def remove_team_member(self, member_id: int) -> dict:
        """
        Fungsi untuk menghapus member di database
        :param member_id: Id member
        :return: None
        """
        try:
            async with self.pool.acquire() as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute(
                        "DELETE FROM team_member WHERE id=%s",
                        (
                            member_id,
                        ),
                    )
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def edit_team_member(self, member_id: int, nama: str, jabatan: str, user_id:int, rank: str, guild_id:int) -> dict:
        """
        Fungsi untuk mengedit member di database
        :param user_id: user_id member discord
        :param member_id: Id member di database
        :param nama: Nama Member
        :param rank: Rank Member di Game server marlin
        :param jabatan: Jabatan User di team
        :return: Dict yang berisi status sukses atau tidaknya edit member
        """
        try:
            async with self.pool.acquire() as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute(
                        "UPDATE team_member SET nama=%s, rank=%s, jabatan=%s, user_id=%s, guild_id=%s WHERE id=%s",
                        (
                            nama,
                            rank,
                            jabatan,
                            user_id,
                            guild_id,
                            member_id,
                        ),
                    )
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_team_member(self) -> dict:
        """
        Fungsi ini akan mengembalikan list dari user yang sudah disimpan

        :return: List semua member
        """
        async with self.pool.acquire() as connection:
            async with connection.cursor(cursor_factory=DictCursor) as cursor:
                await cursor.execute("SELECT * FROM team_member")
                result = await cursor.fetchall()
                return {'success': True, 'members': result}

    async def get_all_member_id(self) -> list:
        """
        Fungsi ini akan mengembalikan list dari id member yang sudah disimpan

        :return: List semua id member
        """
        async with self.pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT id, nama FROM team_member")
                return await cursor.fetchall()


    async def add_welcome_role(self, guild_id: int, role: int) -> dict:
        try:
            async with self.pool.acquire() as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute("SELECT guild_id FROM welcome_role WHERE guild_id = %s", (guild_id,))
                    result = await cursor.fetchone()

                    if result:
                        return {"success": False,
                                "duplicate": True,
                                "error": "Role untuk server ini sudah disetel. Gunakan update jika ingin mengubah."}

                    await cursor.execute("INSERT INTO welcome_role(guild_id, role_id) VALUES (%s, %s)",
                                         (guild_id, role))
                    return {"success": True,
                            "duplicate": False}
        except Exception as e:
            return {"success": False,"duplicate": False, "error": str(e)}

    async def edit_welcome_role(self, guild_id: int, role_id: int) -> dict:
        try:
            async with self.pool.acquire() as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute("UPDATE welcome_role SET role_id=%s WHERE guild_id=%s",
                                         (role_id, guild_id))
                    return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def remove_welcome_role(self, guild_id: int) -> dict:
        try:
            async with self.pool.acquire() as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute("DELETE FROM welcome_role WHERE guild_id=%s",
                                         (guild_id,))
                    return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_welcome_role(self, guild_id: int) -> dict:
        try:
            async with self.pool.acquire() as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute("SELECT role_id FROM welcome_role WHERE guild_id=%s",
                                         (guild_id,))
                    value = await cursor.fetchone()
                    return {"success": True,
                            "value": value[0]}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def add_bounty(self, user_id: int, target: str, reason: str, payout: int, required_kill: int) -> dict:
        try:
            async with self.pool.acquire() as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute("SELECT 1 FROM blacklisted_bounty WHERE user_id=%s", (user_id,))
                    if await cursor.fetchone():
                        return {"success": False,
                                "blacklisted": True,
                                "error": "user id ini di blacklist dari bounty"}

                    await cursor.execute("SELECT 1 FROM bounty WHERE user_id=%s AND active=true", (user_id,))
                    if await cursor.fetchone():
                        return {"success": False,
                                "duplicate": True,
                                "error": "Kamu sudah menambahkan bounty tunggu sampai bounty kamu tidak aktif"}

                    await cursor.execute("INSERT INTO bounty(user_id, target, reason, payout, required_kill) VALUES (%s, %s, %s, %s, %s)",
                                         (user_id, target, reason, payout, required_kill))
                    return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def edit_bounty(self, user_id: int, target: str, reason: str, payout: int, required_kill: int) -> dict:
        try:
            async with self.pool.acquire() as connection:
                async with connection.cursor(cursor_factory=DictCursor) as cursor:
                    data_lama = await cursor.execute("SELECT 1 FROM bounty WHERE user_id=%s AND active=true", (user_id,))
                    if not await cursor.fetchone():
                        return {"success": False,
                                "error": "Kamu tidak memiliki bounty aktif yang bisa diedit."}

                    await cursor.execute("UPDATE bounty SET target=%s, reason=%s, payout=%s, requied_kill=%s WHERE user_id=%s",
                                         (target, reason, payout, user_id, required_kill))

                    return {"success": True,"data_lama": data_lama}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def remove_bounty(self, user_id: int) -> dict:
        try:
            async with self.pool.acquire() as connection:
                async with connection.cursor(cursor_factory=DictCursor) as cursor:

                    # 1. Cari tahu ID bounty yang sedang aktif milik user ini
                    await cursor.execute(
                        "SELECT bounty_id, target FROM bounty WHERE user_id=%s AND active=true",
                        (user_id,)
                    )
                    row = await cursor.fetchone()

                    # PENGECEKAN WAJIB: Cegah error jika row kosong
                    if not row:
                        return {
                            "success": False,
                            "error": "Kamu tidak memiliki bounty aktif yang bisa dihapus."
                        }

                    bounty_id = row['bounty_id']
                    target = row['target']
                    # 2. Cek apakah bounty ini sudah diklaim
                    await cursor.execute(
                        "SELECT 1 FROM bounty_claim WHERE fk_bounty_id=%s",
                        (bounty_id,)
                    )
                    if await cursor.fetchone():
                        return {
                            "success": False,
                            "target": target,
                            "error": "Bounty ini sudah diklaim oleh seseorang dan tidak bisa dihapus!"
                        }

                    # 3. Hapus HANYA bounty spesifik tersebut (Sangat Aman)
                    await cursor.execute("DELETE FROM bounty WHERE bounty_id=%s", (bounty_id,))

                    return {"success": True}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_bounty_autocomplete(self, search_query: str):
        try:
            if not search_query:
                search_query = ""

            async with self.pool.acquire() as connection:
                async with connection.cursor(cursor_factory=DictCursor) as cursor:
                    sql = "SELECT bounty_id, target, payout, required_kill FROM bounty WHERE active=true AND target ILIKE %s LIMIT 10"
                    await cursor.execute(sql, (f"%{search_query}%",))

                    rows = await cursor.fetchall()
                    return {"success": True, "result": rows}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_bounty_by_id(self, bounty_id: int) -> dict:
        try:
            async with self.pool.acquire() as connection:
                async with connection.cursor(cursor_factory=DictCursor) as cursor:
                    await cursor.execute("SELECT * FROM bounty WHERE bounty_id=%s", (bounty_id,))
                    result = await cursor.fetchone()
                    return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_all_active_bounty_target(self):
        try:
            async with self.pool.acquire() as connection:
                async with connection.cursor(cursor_factory=DictCursor) as cursor:
                    await cursor.execute("SELECT target FROM bounty WHERE active=true")
                    result = await cursor.fetchall()
                    if result:
                        return {"success": True, "result": result}
                    return {"success": False}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def blacklist_bounty(self, user_id: int, blacklisted: bool) -> dict:
        try:
            async with self.pool.acquire() as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute(
                        "INSERT INTO blacklisted_bounty(user_id, blacklisted) VALUES (%s)",
                        (user_id, blacklisted)
                    )
                    return {"success": True, "blacklisted": blacklisted}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def claim_bounty(self, user_id: int, bounty_id: int, nickname_ingame: str) -> dict:
        try:
            async with self.pool.acquire() as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute(
                        "SELECT 1 FROM bounty_claim WHERE user_id=%s",
                        (user_id,)
                    )
                    if await cursor.fetchone():
                        return {
                            "success": False,
                            "error": "Kamu sudah mengklaim bounty, kamu tidak bisa mengklaim bounty lain sebelum menyelesaikan bounty yang sudah kamu klaim!"
                        }

                    await cursor.execute(
                        "INSERT INTO bounty_claim(user_id, fk_bounty_id, nickname_ingame) VALUES (%s, %s, %s)",
                        (user_id, bounty_id, nickname_ingame)
                    )
                    return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def unclaim_bounty(self, user_id: int) -> dict:
        try:
            async with self.pool.acquire() as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute(
                        "SELECT 1 FROM bounty_claim WHERE user_id=%s",
                        (user_id,)
                    )
                    row = await cursor.fetchone()
                    if not row:
                        return {
                            "success": False,
                            "error": "Kamu belum klaim bounty"
                        }

                    await cursor.execute(
                        "DELETE FROM bounty_claim WHERE user_id=%s",
                        (user_id,)
                    )
                    return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def add_kill_autocomplete(self, search_query: str):
        try:
            if not search_query:
                search_query = ""

            async with self.pool.acquire() as connection:
                async with connection.cursor(cursor_factory=DictCursor) as cursor:
                    sql = """
                          SELECT 
                              bounty.bounty_id AS bounty_id,
                              bounty.target AS target,
                              bounty.required_kill AS required_kill,
                              bounty_claim.nickname_ingame AS nickname_ingame,
                              bounty_claim.user_id AS user_id
                          FROM bounty
                                  JOIN bounty_claim
                                        ON bounty.bounty_id = bounty_claim.fk_bounty_id
                          WHERE bounty_claim.nickname_ingame ILIKE %s LIMIT 15"""
                    await cursor.execute(sql, (f"%{search_query}%",))
                    results = await cursor.fetchall()
                    return {"success": True, "result": results}
        except Exception as e:
            return {"success": False, "error": str(e)}


    async def add_kill_to_bounty(self, kill: int, user_id: int) -> dict:
        try:
            async with self.pool.acquire() as connection:
                async with connection.cursor(cursor_factory=DictCursor) as cursor:
                    # Kurangi required kill di postingan bounty
                    await cursor.execute(
                        "SELECT fk_bounty_id FROM bounty_claim WHERE user_id=%s",
                        (user_id,)
                    )
                    claim_row = await cursor.fetchone()
                    if not claim_row:
                        return {
                            "success": False,
                            "error": "User ini tidak memiliki klaim bounty aktif."
                        }
                    b_id = claim_row['fk_bounty_id']

                    # Update kill count dengan kill yang baru
                    await cursor.execute(
                        "UPDATE bounty_claim SET kill_count = kill_count + %s WHERE user_id = %s AND fk_bounty_id = %s",
                        (kill, user_id, b_id)
                    )

                    query_update = """
                                   UPDATE bounty
                                   SET required_kill = GREATEST(required_kill - %s, 0)
                                   WHERE bounty_id = %s RETURNING required_kill
                                   """
                    await cursor.execute(query_update, (kill, b_id))
                    res = await cursor.fetchone()

                    if not res:
                        return {
                            "success": False,
                            "error": "Data bounty tidak ditemukan."
                        }

                    remaining_kill = res['required_kill']

                    if remaining_kill <= 0:
                        # Set active = false karena target sudah habis terbunuh
                        await cursor.execute(
                            "UPDATE bounty SET active = false WHERE bounty_id = %s",
                            (b_id,)
                        )

                        # Opsional: Hapus data klaim setelah selesai
                        await cursor.execute("DELETE FROM bounty_claim WHERE user_id = %s", (user_id,))

                        return {
                            "success": True,
                            "completed": True,
                            "message": "Target telah tereliminasi sepenuhnya! Bounty Selesai."
                        }

                    return {
                        "success": True,
                        "completed": False,
                        "message": f"Kill berhasil dicatat! Sisa target yang harus dibunuh: {remaining_kill} lagi."
                    }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def set_bounty_settings(self, join_leave_channel: int, join_alert_channel: int, bounty_alert_channel: int, guild_id: int):
        try:
            async with self.pool.acquire() as connection:
                async with connection.cursor(cursor_factory=DictCursor) as cursor:
                    await cursor.execute(
                        "INSERT INTO bounty_settings(guild_id, join_leave_channel, join_alert_channel, bounty_alert_channel) VALUES (%s, %s, %s, %s) ON CONFLICT (guild_id) DO UPDATE SET join_leave_channel = EXCLUDED.join_leave_channel, join_alert_channel = EXCLUDED.join_alert_channel, bounty_alert_channel = EXCLUDED.bounty_alert_channel",
                        (guild_id, join_leave_channel, join_alert_channel, bounty_alert_channel)
                    )
                    return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def get_bounty_settings(self, guild_id: int) -> dict:
        try:
            async with self.pool.acquire() as connection:
                async with connection.cursor(cursor_factory=DictCursor) as cursor:
                    await cursor.execute("SELECT * FROM bounty_settings WHERE guild_id=%s", (guild_id,))
                    result = await cursor.fetchone()
                    if result:
                        return {"success": True, "result": result}
                    else:
                        return {"success": False, "result": None}
        except Exception as e:
            return {"success": False, "error": str(e)}
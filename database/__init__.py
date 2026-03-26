"""
Copyright © Krypton 2019-Present - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized Discord bot in Python

Version: 6.5.0
"""

import aiosqlite


class DatabaseManager:
    def __init__(self, *, connection: aiosqlite.Connection) -> None:
        self.connection = connection

    async def add_warn(
        self, user_id: int, server_id: int, moderator_id: int, reason: str
    ) -> int:
        """
        This function will add a warn to the database.

        :param user_id: The ID of the user that should be warned.
        :param reason: The reason why the user should be warned.
        """
        rows = await self.connection.execute(
            "SELECT id FROM warns WHERE user_id=? AND server_id=? ORDER BY id DESC LIMIT 1",
            (
                user_id,
                server_id,
            ),
        )
        async with rows as cursor:
            result = await cursor.fetchone()
            warn_id = result[0] + 1 if result is not None else 1
            await self.connection.execute(
                "INSERT INTO warns(id, user_id, server_id, moderator_id, reason) VALUES (?, ?, ?, ?, ?)",
                (
                    warn_id,
                    user_id,
                    server_id,
                    moderator_id,
                    reason,
                ),
            )
            await self.connection.commit()
            return warn_id

    async def remove_warn(self, warn_id: int, user_id: int, server_id: int) -> int:
        """
        This function will remove a warn from the database.

        :param warn_id: The ID of the warn.
        :param user_id: The ID of the user that was warned.
        :param server_id: The ID of the server where the user has been warned
        """
        await self.connection.execute(
            "DELETE FROM warns WHERE id=? AND user_id=? AND server_id=?",
            (
                warn_id,
                user_id,
                server_id,
            ),
        )
        await self.connection.commit()
        rows = await self.connection.execute(
            "SELECT COUNT(*) FROM warns WHERE user_id=? AND server_id=?",
            (
                user_id,
                server_id,
            ),
        )
        async with rows as cursor:
            result = await cursor.fetchone()
            return result[0] if result is not None else 0

    async def get_warnings(self, user_id: int, server_id: int) -> list:
        """
        This function will get all the warnings of a user.

        :param user_id: The ID of the user that should be checked.
        :param server_id: The ID of the server that should be checked.
        :return: A list of all the warnings of the user.
        """
        rows = await self.connection.execute(
            "SELECT user_id, server_id, moderator_id, reason, strftime('%s', created_at), id FROM warns WHERE user_id=? AND server_id=?",
            (
                user_id,
                server_id,
            ),
        )
        async with rows as cursor:
            result = await cursor.fetchall()
            result_list = []
            for row in result:
                result_list.append(row)
            return result_list

    async def add_team_member(self, nama: str, rank: str, jabatan: str) -> dict:
        """
        Fungsi ini akan menambahkan member ke dalam database
        :param nama: Nama member
        :param rank: Rank member
        :param jabatan: Jabatan User di team
        :return:
        """
        try:
            await self.connection.execute(
                "INSERT INTO team_member(nama, rank, jabatan) VALUES (?, ?, ?)",
                (
                    nama,
                    rank,
                    jabatan
                )
            )
            await self.connection.commit()
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
            await self.connection.execute(
                "DELETE FROM team_member WHERE id=?",
                (
                    member_id,
                )
            )
            await self.connection.commit()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def edit_team_member(self, member_id: int, nama: str, jabatan: str, rank: str) -> dict:
        """
        Fungsi untuk mengedit member di database
        :param member_id: Id member di database
        :param nama: Nama Member
        :param rank: Rank Member di Game server marlin
        :param jabatan: Jabatan User di team
        :return: Dict yang berisi status sukses atau tidaknya edit member
        """
        try:
            await self.connection.execute(
                "UPDATE team_member SET nama=?, rank=?, jabatan=? WHERE member_id=?",
                (
                    nama,
                    rank,
                    jabatan,
                    member_id
                )
            )
            await self.connection.commit()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}


    async def get_team_member(self) -> list:
        """
        Fungsi ini akan mengembalikan list dari user yang sudah disimpan

        :return: List semua member
        """
        async with self.connection.execute("SELECT nama, jabatan, rank FROM team_member") as cursor:
            return await cursor.fetchall()



    async def get_all_member_id(self) -> list:
        """
        Fungsi ini akan mengembalikan list dari id member yang sudah disimpan

        :return: List semua id member
        """
        async with self.connection.execute("SELECT id, nama FROM team_member") as cursor:
            return await cursor.fetchall()
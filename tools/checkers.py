import asyncio

import disnake
from disnake.ext.commands import Bot

from database.sql_config import cursor
from tools.logger import Log
import tools.tool
from database.db_req import DBRequests
from tools.draw_types import DrawTypes
class CurrentDrawChecker:
    def __init__(self, bot: Bot, every_seconds: float):
        self.every_seconds = every_seconds
        self.__bot = bot
        self.__current = tools.tool.get_current_draw()
        if self.__current["id"] is not None:
            self.__breaker = False
            self.draw_id = self.__current['id']
            self.draw_type = self.__current['type']
            self.draw_text = self.__current['text']
            self.draw_award = self.__current['award']
            self.draw_need = self.__current['need_count']
            self.draw_anno = self.__current['announcement']
        else:
            self.__breaker = True

    async def update_data(self):
        self.__current = tools.tool.get_current_draw()
        if self.__current["id"] is not None:
            self.breaker = False
            self.draw_id = self.__current['id']
            self.draw_type = self.__current['type']
            self.draw_text = self.__current['text']
            self.draw_award = self.__current['award']
            self.draw_need = self.__current['need_count']
            self.draw_anno = self.__current['announcement']
        else:
            self.breaker = True


    @property
    def breaker(self):
        Log.i("breaker.property", f"Property was called. Value: {self.__breaker}")
        return self.__breaker
    @breaker.setter
    def breaker(self, value: bool):
        self.__breaker = value
        Log.i("breaker.setter", f"Setter was called. Value: {value}")
        asyncio.create_task(self.set_check_loop())

    async def set_check_loop(self):
        Log.i("set_check_loop", f"Check loop was called with breaker value: {self.breaker}")
        every_seconds = self.every_seconds
        if self.breaker:
            Log.w("draw_check_loop", "Check process is broken")
            return
        draw_anno = await self.__bot.fetch_channel(int(self.__current['announcement']))
        if self.draw_type == 'text':
            winners = ()
            while len(winners) == 0 or (await DBRequests.get_text_draw_by_id(self.draw_id))[1][4] == 0:
                Log.i("draw_check_loop", f"Current draw time with id {self.draw_id}: {(await DBRequests.get_text_draw_by_id(self.draw_id))[1][3]}")
                await asyncio.sleep(every_seconds)
                cursor.execute(
                    "SELECT * FROM text_draws_members WHERE draw_id LIKE ? ORDER BY ? LIMIT ?",
                    [self.draw_id, int(self.draw_need), tools.tool.get_max_winners()])
                winners = cursor.fetchall()
                if (await DBRequests.get_text_draw_by_id(self.draw_id))[1][3] > every_seconds:
                    await DBRequests.update_text_draw_by_id(id=self.draw_id, time=-(every_seconds // 60), completed=False)
                else:
                    await DBRequests.update_text_draw_by_id(id=self.draw_id, time=-((await DBRequests.get_text_draw_by_id(self.draw_id))[1][3]), completed=True)
                    Log.s("draw_check_loop", "Current draw finished. ")
                    winners = await DBRequests.get_draw_winners(self.draw_id, DrawTypes.TEXT, self.draw_need)
                    break
            if len(winners) > 0 or self.breaker:
                    winners_str = ""
                    for w in winners:
                        await DBRequests.update_user_by_id(w[1], 1)
                        w_id = (await DBRequests.get_user_by_id(int(w[1])))[1]
                        w_wins = (await DBRequests.get_user_by_id(int(w[1])))[2]
                        w_count = w[2]
                        winners_str += f"\n:bust_in_silhouette: {(await self.__bot.fetch_user(int(w_id))).mention} | :trophy: {w_wins} | :speech_balloon: {w_count}"
                    await draw_anno.send(
                        embed=disnake.Embed(
                            title=f":tickets: Розыгрыш на награду \"{self.draw_award}\" завершен!",
                            description=f":fire: Участникам нужно было набрать {self.draw_need} сообщений в {(await self.__bot.fetch_channel(int((await DBRequests.get_text_draw_by_id(self.draw_id))[1][2]))).mention}. Победителями стали:\n\n{winners_str}",
                            color=disnake.Color.yellow()
                        )
                    )
                    tools.tool.set_current_draw(None, None, None, None, None, None, None)


        if self.draw_type == 'voice':
            winners = ()
            while len(winners) == 0 or not self.breaker:
                Log.i("draw_check_loop", f"Current draw time with id {self.draw_id}: {(await DBRequests.get_voice_draw_by_id(self.draw_id))[1][3]}")
                await asyncio.sleep(every_seconds)
                cursor.execute(
                    "SELECT * FROM voice_draws_members WHERE draw_id LIKE ? ORDER BY ? LIMIT ?",
                    [self.draw_id, int(self.draw_need), tools.tool.get_max_winners()])
                winners = cursor.fetchall()
                if (await DBRequests.get_voice_draw_by_id(self.draw_id))[1][3] > every_seconds:
                    await DBRequests.update_voice_draw_by_id(id=self.draw_id, time=-(every_seconds // 60), completed=False)
                else:
                    await DBRequests.update_voice_draw_by_id(id=self.draw_id, time=-((await DBRequests.get_voice_draw_by_id(self.draw_id))[1][3]), completed=True)
                    Log.s("draw_check_loop", "Current draw finished. ")
                    winners = await DBRequests.get_draw_winners(self.draw_id, DrawTypes.VOICE, self.draw_need)
                    self.breaker = True
            if len(winners) > 0 or self.breaker:
                    winners_str = ""
                    for w in winners:
                        await DBRequests.update_user_by_id(w[1], 1)
                        w_id = (await DBRequests.get_user_by_id(int(w[1])))[1]
                        w_wins = (await DBRequests.get_user_by_id(int(w[1])))[2]
                        w_count = w[2]
                        winners_str += f"\n:bust_in_silhouette: {(await self.__bot.fetch_user(int(w_id))).mention} | :trophy: {w_wins} | :speech_balloon: {w_count}"
                    await draw_anno.send(
                        embed=disnake.Embed(
                            title=f":tickets: Розыгрыш на награду \"{self.draw_award}\" завершен!",
                            description=f":fire: Участникам нужно было просидеть {self.draw_need} минут в {(await self.__bot.fetch_channel(int((await DBRequests.get_voice_draw_by_id(self.draw_id))[1][2]))).mention}. Победителями стали:\n\n{winners_str}",
                            color=disnake.Color.yellow()
                        )
                    )
                    tools.tool.set_current_draw(None, None, None, None, None, None, None)

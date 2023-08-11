import asyncio
import time
import disnake
from disnake.ext.commands import Bot
from tools.tool import *
from database.sql_config import cursor
from tools.logger import Log
import tools.tool
from database.db_req import DBRequests
from tools.draw_types import DrawTypes

class VoiceController:

    def __init__(self):
        self.__mem = {}

    @property
    def mem(self):
        return self.__mem

    async def reg(self, user_id: int):
        if user_id not in self.__mem:
            self.__mem[user_id] = {
                'start': None,
                'end': None
            }
    async def start(self, user_id: int, ignore_current_value: bool = False):
        await self.reg(user_id)
        if ignore_current_value is False:
            if self.__mem[user_id]['start'] is None:
                self.__mem[user_id]['start'] = time.time()
        elif ignore_current_value:
            self.__mem[user_id]['start'] = time.time()

    async def end(self, user_id: int, ignore_current_value: bool = False):
        await self.reg(user_id)
        if ignore_current_value is False:
            if self.__mem[user_id]['start'] is not None and self.__mem[user_id]['end'] is None:
                self.__mem[user_id]['end'] = time.time()
                return
            self.__mem[user_id]['start'] = time.time()
            self.__mem[user_id]['end'] = time.time()
        elif ignore_current_value:
            if self.__mem[user_id]['start'] is not None:
                self.__mem[user_id]['end'] = time.time()
                return
            self.__mem[user_id]['start'] = time.time()
            self.__mem[user_id]['end'] = time.time()

    async def compile_result(self, user_id: int, draw_id: int):
        await self.reg(user_id)
        start = self.__mem[user_id]['start']
        end = self.__mem[user_id]['end']
        if start is not None and end is not None:
            time_in_channel = int(end - start) // 60
            await DBRequests.update_voice_draw_member_by_id(user_id, draw_id, time_in_channel) if time_in_channel < int(
            get_current_draw()['need_count']) else await DBRequests.update_voice_draw_member_by_id(user_id, draw_id,int(get_current_draw()['need_count']))
            Log.i("compile_result", f"start: {start} | end: {end} | time in channel: {time_in_channel}")
        self.__mem[user_id]['start'] = None
        self.__mem[user_id]['end'] = None

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

    @property
    def breaker(self):
        Log.i("breaker.property", f"Property was called. Breaker value: {self.__breaker}")
        return self.__breaker

    @breaker.setter
    def breaker(self, value):
        self.__breaker = value
        Log.i("breaker.setter", f"Setter was called. Breaker value: {value}")
        asyncio.create_task(self.check_draw())


    async def update_data(self):
      while True:
        Log.i("update_data", f"Data updated with delay {self.every_seconds}")
        await asyncio.sleep(self.every_seconds)
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

    async def __stop_draw(self):
        set_current_draw(None, None, None, None, None, None, None)

    async def check_draw(self):
        if self.breaker:
            Log.w("check_draw", f"Check process is broken. Breaker value: {self.breaker}")
            return
        draw_anno = await self.__bot.fetch_channel(int(self.__current['announcement']))
        if self.draw_type == 'text':
            Log.i("check_draw",
                  f"Current draw time with id {self.draw_id}: {(await DBRequests.get_text_draw_by_id(self.draw_id))[1][3] * 60} seconds")
            cursor.execute(
                "SELECT * FROM text_draws_members WHERE draw_id LIKE ? AND messages_in_channel LIKE ? LIMIT ?",
                [self.draw_id, int(self.draw_need), tools.tool.get_max_winners()])
            winners = cursor.fetchall()
            Log.i('check_draw', f"Draw winners: {winners}")
            if ((await DBRequests.get_text_draw_by_id(self.draw_id))[1][3] * 60) > self.every_seconds:
                Log.i('check_draw',
                      f"time: {((await DBRequests.get_text_draw_by_id(self.draw_id))[1][3] * 60)} > {self.every_seconds}")
                await DBRequests.update_text_draw_by_id(id=self.draw_id, time=-(self.every_seconds // 60), completed=False)
            if ((await DBRequests.get_text_draw_by_id(self.draw_id))[1][3] * 60) <= self.every_seconds or len(winners) > 0:
                Log.i('check_draw',
                      f"time: {((await DBRequests.get_text_draw_by_id(self.draw_id))[1][3] * 60)} <= {self.every_seconds} or length of winners = {len(winners)} > 0")
                await DBRequests.update_text_draw_by_id(id=self.draw_id, time=-(
                (await DBRequests.get_text_draw_by_id(self.draw_id))[1][3]), completed=True)
                Log.s("draw_check_loop", "Current draw finished. ")
                winners = await DBRequests.get_draw_winners(self.draw_id, DrawTypes.TEXT, self.draw_need)
                channel = await self.__bot.fetch_channel(int((await DBRequests.get_text_draw_by_id(self.draw_id))[1][1]))
                winners_str = ""
                for w in winners:
                    await DBRequests.update_user_by_id(w[1], 1)
                    w_id = (await DBRequests.get_user_by_id(int(w[1])))[1][1]
                    w_wins = (await DBRequests.get_user_by_id(int(w[1])))[1][2]
                    w_count = w[2]
                    memb = await self.__bot.fetch_user(int(w_id))
                    winners_str += f"\n:bust_in_silhouette: {memb.mention} | :trophy: {w_wins} | :speech_balloon: {w_count}"
                    try:
                        embed = disnake.Embed(
                            title="Поздравляю! :piñata:",
                            description=f"Ты победил в розыгрыше на награду \"{self.draw_award}\", написав более, чем {w_count} сообщений в канале **{channel.name}** :)",
                            color=disnake.Color.yellow()
                        )
                        await memb.send(embed=embed)
                    except:
                        pass
                await draw_anno.send(
                    embed=disnake.Embed(
                        title=f":tickets: Розыгрыш на награду \"{self.draw_award}\" завершен!",
                        description=f":fire: Участникам нужно было набрать {int(self.draw_need)} сообщений в {channel.mention}. Победителями стали:\n\n{winners_str}",
                        color=disnake.Color.yellow()
                    )
                )
                await self.__stop_draw()
        if self.draw_type == 'voice':
            Log.i("check_draw",
                  f"Current draw time with id {self.draw_id}: {(await DBRequests.get_voice_draw_by_id(self.draw_id))[1][3] * 60} seconds")
            cursor.execute(
                "SELECT * FROM voice_draws_members WHERE draw_id LIKE ? AND time_in_channel LIKE ? LIMIT ?",
                [self.draw_id, int(self.draw_need), tools.tool.get_max_winners()])
            winners = cursor.fetchall()
            Log.i('check_draw', f"Draw winners: {winners}")
            if ((await DBRequests.get_voice_draw_by_id(self.draw_id))[1][3] * 60) > self.every_seconds:
                Log.i('check_draw', f"time: {((await DBRequests.get_voice_draw_by_id(self.draw_id))[1][3] * 60)} > {self.every_seconds}")
                await DBRequests.update_voice_draw_by_id(id=self.draw_id, time=-(self.every_seconds // 60), completed=False)
            if ((await DBRequests.get_voice_draw_by_id(self.draw_id))[1][3] * 60) <= self.every_seconds or len(winners) > 0:
                Log.i('check_draw',
                      f"time: {((await DBRequests.get_voice_draw_by_id(self.draw_id))[1][3] * 60)} <= {self.every_seconds} or length of winners = {len(winners)} > 0")
                await DBRequests.update_voice_draw_by_id(id=self.draw_id, time=-(
                (await DBRequests.get_voice_draw_by_id(self.draw_id))[1][3]), completed=True)
                Log.s("draw_check_loop", "Current draw finished. ")
                winners = await DBRequests.get_draw_winners(self.draw_id, DrawTypes.VOICE, self.draw_need)
                channel = await self.__bot.fetch_channel(int((await DBRequests.get_voice_draw_by_id(self.draw_id))[1][1]))
                winners_str = ""
                for w in winners:
                    await DBRequests.update_user_by_id(w[1], 1)
                    w_id = (await DBRequests.get_user_by_id(int(w[1])))[1][1]
                    w_wins = (await DBRequests.get_user_by_id(int(w[1])))[1][2]
                    w_count = w[2]
                    memb = await self.__bot.fetch_user(int(w_id))
                    winners_str += f"\n:bust_in_silhouette: {memb.mention} | :trophy: {w_wins} | :stopwatch: {w_count} мин."
                    try:
                        embed = disnake.Embed(
                            title="Поздравляю! :piñata:",
                            description=f"Ты победил в розыгрыше на награду \"{self.draw_award}\", просидев более, чем {w_count} мин. в голосовом канале **{channel.name}** с включенным микрофоном :)",
                            color=disnake.Color.yellow()
                        )
                        await memb.send(embed=embed)
                    except:
                        pass
                await draw_anno.send(
                    embed=disnake.Embed(
                        title=f":tickets: Розыгрыш на награду \"{self.draw_award}\" завершен!",
                        description=f":fire: Участникам нужно было просидеть {int(self.draw_need)} минут в голосовом канале {channel.mention} с вкл. микрофоном. Победителями стали:\n\n{winners_str}",
                        color=disnake.Color.yellow()
                    )
                )
                await self.__stop_draw()




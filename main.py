# -*- coding: utf-8 -*-
import time
import disnake
from disnake.ext import commands
from database.db_req import DBRequests
from tools.tool import *
from tools.logger import Log
from tools.extra import Extra
from tools.checkers import CurrentDrawChecker, VoiceController
import random
import datetime
import asyncio
from disnake.ui import Button
from disnake.enums import ButtonStyle, TextInputStyle
import json
from disnake import Embed
from disnake.utils import get

cont = input("При запуске данной программы будет запущен бот! (Нажмите Enter для продолжения))")

bot = commands.Bot(command_prefix="#", case_insensitive=True, intents=disnake.Intents.all())
bot.remove_command('help')

set_max_winners(100) #Максимальное количество человек, которые могут выиграть за раз

checker = CurrentDrawChecker(bot, 60) #Движок, который обновляет информацию о данных розыгрыша каждые N секунд
voice_ctrl = VoiceController()

voice_extra = Extra()
text_extra = Extra()

@bot.event
async def on_ready():
    Log.s("on_ready", "Connected to Discord API successfully")
    await DBRequests.init_database()
    game = disnake.Game(" Developed by @belgray")
    await bot.change_presence(status=disnake.Status.online, activity=game)
    await checker.update_data()


@bot.event
async def on_interaction(interaction):
    Log.i("on_interaction", f"Called interaction by {interaction.author} in channel {interaction.channel.name}")
    await DBRequests.insert_user(str(interaction.author.id), 0)

@bot.event
async def on_message(message):
    try:
        Log.i("on_message", f"Message by {message.author} in {message.channel.name} channel: {message.content}")
    except:
        pass
    await DBRequests.insert_user(str(message.author.id), 0)
    draw_id = get_current_draw()['id']
    if draw_id is not None and get_current_draw()['type'] == 'text':
        need = get_current_draw()['need_count']
        user_id = (await DBRequests.get_user_by_discord_id(str(message.author.id)))[1][0]
        reg = await DBRequests.get_text_draw_member_by_id(user_id, draw_id)
        if reg[0]:
            if reg[1][2] < int(need):
                await DBRequests.update_text_draw_member_by_id(user_id, draw_id, 1)


@bot.slash_command(
    name="chat",
    description = "Создать розыгрыш на количество сообщений, отпарвленных в текстовом канале"
)
async def chat(inter: disnake.ApplicationCommandInteraction, announcement: disnake.TextChannel = commands.Param(name="канал_для_объявления", description="Канал, в котором будет размещен текст розыгрыша"), channel: disnake.TextChannel = commands.Param(name="канал_розыгрыша", description="Канал, в котором нужно будет отправить определенное количество сообщений, чтобы победить")):
    if inter.author.id != inter.guild.owner.id:
        await inter.send(embed=create_error_embed("Только владелец этого чудесного сервера может вызвать данную команду"), ephemeral=True)
    await text_extra.put("announcement", int(announcement.id))
    await text_extra.put("channel", int(channel.id))
    if get_current_draw()["id"] != None:
        ui = disnake.ui.View()
        embed = Embed(
            title="На сервере уже проводится розыгрыш",
            description=f"На сервере уже проводится розыгрыш. Чтобы начать новый, нужно хотя бы принудительно завершить старый (победителем будет считаться пользователь, который ближе всех находится к победе)",
            color=disnake.Color.yellow()
        )
        ui.add_item(Button(
            label="Завершить розыгрыш",
            style=ButtonStyle.red,
            custom_id="stop_current_draw"
        ))
        return await inter.send(embed=embed, view=ui, ephemeral=True)

    modal = disnake.ui.Modal(
        custom_id = "text_modal",
        title="Создание чат розыгрыша",
        components=[
            disnake.ui.TextInput(
                custom_id="text_text",
                label="Текст объявления розыгрыша",
                required=True,
                min_length=5,
                max_length=2000,
                style=TextInputStyle.long
            ),
            disnake.ui.TextInput(
                custom_id="text_award",
                label="Награда победителю",
                required=True,
                min_length=1,
                max_length=2000,
                style=TextInputStyle.long
            ),
            disnake.ui.TextInput(
                custom_id="text_count",
                label="Написать сообщений (количество)",
                required=True,
                min_length=1,
                max_length=10,
                placeholder="9999999999",
                style=TextInputStyle.short
            ),
            disnake.ui.TextInput(
                custom_id="text_time",
                label="Длительность розыгрыша (минут)",
                required=True,
                min_length=1,
                max_length=15,
                placeholder="999999999999999",
                style=TextInputStyle.short
            ),
        ]
    )
    await inter.response.send_modal(modal=modal)


@bot.slash_command(
    name="voice",
    description="Создать розыгрыш на время, проведенное в голосовом канале"
)
async def voice(inter: disnake.ApplicationCommandInteraction, announcement: disnake.TextChannel = commands.Param(name="канал_для_объявления", description="Канал, в котором будет размещен текст розыгрыша"), channel: disnake.VoiceChannel = commands.Param(name="канал_розыгрыша", description="Канал, в котором нужно будет провести определенное время, чтобы победить")):
    if inter.author.id != inter.guild.owner.id:
        await inter.send(
            embed=create_error_embed("Только владелец этого чудесного сервера может вызвать данную команду"),
            ephemeral=True)
    await voice_extra.put("announcement", int(announcement.id))
    await voice_extra.put("channel", int(channel.id))
    if get_current_draw()["id"] != None:
        ui = disnake.ui.View()
        embed = Embed(
            title="На сервере уже проводится розыгрыш",
            description=f"На сервере уже проводится розыгрыш. Чтобы начать новый, нужно хотя бы принудительно завершить старый (победителем будет считаться пользователь, который ближе всех находится к победе)",
            color=disnake.Color.yellow()
        )
        ui.add_item(Button(
            label="Завершить розыгрыш",
            style=ButtonStyle.red,
            custom_id="stop_current_draw"
        ))
        return await inter.send(embed=embed, view=ui, ephemeral=True)

    modal = disnake.ui.Modal(
        custom_id = "voice_modal",
        title="Создание войс розыгрыша",
        components=[
            disnake.ui.TextInput(
                custom_id="voice_text",
                label="Текст объявления розыгрыша",
                required=True,
                min_length=5,
                max_length=2000,
                style=TextInputStyle.long
            ),
            disnake.ui.TextInput(
                custom_id="voice_award",
                label="Награда победителю",
                required=True,
                min_length=1,
                max_length=2000,
                style=TextInputStyle.long
            ),
            disnake.ui.TextInput(
                custom_id="voice_count",
                label="Провести в канале (минут)",
                required=True,
                min_length=1,
                max_length=10,
                placeholder="9999999999",
                style=TextInputStyle.short
            ),
            disnake.ui.TextInput(
                custom_id="voice_time",
                label="Длительность розыгрыша (минут)",
                required=True,
                min_length=1,
                max_length=15,
                placeholder="999999999999999",
                style=TextInputStyle.short
            ),
        ]
    )
    await inter.response.send_modal(modal=modal)


@bot.slash_command(
    name="leaderboard",
    description="Таблица лидеров текущего розыгрыша"
)
async def leaderboard(inter: disnake.ApplicationCommandInteraction):
    current = get_current_draw()
    leaders = await DBRequests.get_top_users_of_current_draw()
    if leaders is None:
        embed = Embed(
            title = ":thought_balloon: Таблица лидеров пуста",
            description = "На данный момент не проходит никакого розыгрыша.",
            color=disnake.Color.purple()
        )
        return await inter.send(embed=embed, ephemeral=True)
    if len(leaders) == 0:
        top_str = "\nНикто не учавствует в розыгрыше :("
    else:
        top_str = ""
    if current['type'] == 'voice':
        emg = ':loud_sound:'
        lbl = ':stopwatch: {} мин.'
    else:
        emg = ':hash:'
        lbl = ':speech_balloon: {}'

    for i in range(len(leaders)):
        u = leaders[i]
        db_u = await DBRequests.get_user_by_id(u[1])
        top_str += f"**{i+1}#** {(await bot.fetch_user(int(db_u[1][1]))).mention} | {lbl.format(u[2])}"

    await inter.send(
        embed=Embed(
            title=f"{emg} ТОП 30 участников в розыгрыше на \"{current['award']}\"",
            description=top_str,
            color=disnake.Color.purple()
        )
    )

@bot.slash_command(
    name="profile",
    description="Профиль пользователя"
)
async def profile(inter: disnake.ApplicationCommandInteraction, member: disnake.Member = commands.Param(name="участник", description="Участник сервера, о котором ты хочешь глянуть информацию", default=None)):
    if member == None:
        d = inter.author
        did = inter.author.id
    else:
        d = member
        did = member.id
    try:
        u = await DBRequests.get_user_by_discord_id(str(did))
        if u[0]:
            if get_current_draw()['id'] != None:
                if get_current_draw()['type'] == 'voice':
                    draw_u = await DBRequests.get_voice_draw_member_by_id(u[1][0], get_current_draw()['id'])
                    emg = ':loud_sound:'
                    lbl = ':stopwatch: `{} мин.`'
                else:
                    draw_u = await DBRequests.get_text_draw_member_by_id(u[1][0], get_current_draw()['id'])
                    emg = ':hash:'
                    lbl = ':speech_balloon: `{}`'
                embed = Embed(color=disnake.Color.purple())
                embed.set_author(name=d.name, icon_url=d.display_avatar)
                embed.add_field(name=":id: ID в базе бота", value=f"`{u[1][0]}`", inline=True)
                embed.add_field(name=":trophy: Побед", value=f"`{u[1][2]}`", inline=True)
                if draw_u[0]:
                    embed.description = f"> **{d.name}** учавствует в розыгрыше на \"{get_current_draw()['award']}\""
                    embed.add_field(name=f"{emg} Прогресс выполнения условия розыгрыша", value=lbl.format(draw_u[1][2]), inline=False)
            else:
                embed = Embed(color=disnake.Color.purple())
                embed.set_author(name=d.name, icon_url=d.display_avatar)
                embed.add_field(name=":id: ID в базе бота", value=f"`{u[1][0]}`", inline=False)
                embed.add_field(name=":trophy: Побед", value=f"`{u[1][2]}`", inline=False)

            await inter.send(embed=embed, ephemeral=True)
        else:
            await inter.send(embed=create_error_embed("Не получилось найти пользователя в базе данных :(\nПопробуй вызвать команду еще раз"), ephemeral=True)
    except Exception as e:
        await inter.send(
            embed=create_error_embed(f"Произошла неизвестная ошибка. Сообщение от интерпретатора: \n```{e}```"),
            ephemeral=True
        )



@bot.event
async def on_button_click(interaction):
    if interaction.component.custom_id == "stop_current_draw":
        current = get_current_draw()
        id = current['id']
        if id != None and current['type'] == 'voice':
            type = current['type']
            text = current['text']
            award = current['award']
            time = current['time']
            need = current['need_count']
            winners = await DBRequests.get_draw_winners(id, DrawTypes.TEXT if type == 'text' else DrawTypes.VOICE, need)
            anno = await bot.fetch_channel(current['announcement'])
            winners_str = ""
            for w in winners:
                await DBRequests.update_user_by_id(w[1], 1)
                w_id = (await DBRequests.get_user_by_id(int(w[1])))[1][1]
                w_wins = (await DBRequests.get_user_by_id(int(w[1])))[1][2]
                w_count = w[2]
                memb = await bot.fetch_user(int(w_id))
                winners_str += f"\n:bust_in_silhouette: {memb.mention} | :trophy: {w_wins} | :stopwatch: {w_count} мин."
                try:
                    embed = disnake.Embed(
                        title="Поздравляю! :piñata:",
                        description=f"Ты победил в розыгрыше на награду \"{award}\", просидев более, чем {w_count} мин. в голосовом канале с включенным микрофоном. Розыгрыш был принудительно завершен администратором сервера, но тем не менее ты молодец! :)",
                        color=disnake.Color.blurple()
                    )
                    await memb.send(embed=embed)
                except:
                    pass
            await anno.send(
                embed=disnake.Embed(
                    title=f":tickets: Розыгрыш на награду \"{award}\" принудительно завершен!",
                    description=f":fire: Победителями стали:\n\n{winners_str}",
                    color=disnake.Color.yellow()
                )
            )
            set_current_draw(None, None, None, None, None, None, None)
            await interaction.send(f"Успешно! Объявление о завершении розыгрыша сделано в {anno.mention}", ephemeral=True)
        if id != None and current['type'] == 'text':
            type = current['type']
            text = current['text']
            award = current['award']
            time = current['time']
            need = current['need_count']
            winners = await DBRequests.get_draw_winners(id, DrawTypes.TEXT if type == 'text' else DrawTypes.VOICE, need)
            anno = await bot.fetch_channel(current['announcement'])
            winners_str = ""
            for w in winners:
                await DBRequests.update_user_by_id(w[1], 1)
                w_id = (await DBRequests.get_user_by_id(int(w[1])))[1][1]
                w_wins = (await DBRequests.get_user_by_id(int(w[1])))[1][2]
                w_count = w[2]
                memb = await bot.fetch_user(int(w_id))
                winners_str += f"\n:bust_in_silhouette: {memb.mention} | :trophy: {w_wins} | :speech_balloon: {w_count}"
                try:
                    embed = disnake.Embed(
                        title="Поздравляю! :piñata:",
                        description=f"Ты победил в розыгрыше на награду \"{award}\", написав более, чем {w_count} сообщений в текстовом канале. Розыгрыш был принудительно завершен администратором сервера, но тем не менее ты молодец! :)",
                        color=disnake.Color.blurple()
                    )
                    await memb.send(embed=embed)
                except:
                    pass
            await anno.send(
                embed=disnake.Embed(
                    title=f":tickets: Розыгрыш на награду \"{award}\" принудительно завершен!",
                    description=f":fire: Победителями стали:\n\n{winners_str}",
                    color=disnake.Color.yellow()
                )
            )
            set_current_draw(None, None, None, None, None, None, None)
            await interaction.send(f"Успешно! Объявление о завершении розыгрыша сделано в {anno.mention}", ephemeral=True)

    if "vtp" in interaction.component.custom_id:
        draw_id = int(interaction.component.custom_id[3:])
        user_id = (await DBRequests.get_user_by_discord_id(str(interaction.author.id)))[1][0]
        if get_current_draw()['id'] == draw_id:
            reg = await DBRequests.insert_voice_draw_member(draw_id, user_id, 0)
            if reg[0]:
                await interaction.send('Отлично, ты теперь учавствуешь в конкурсе! А теперь, бегом выполнять условие, чтобы стать первым :)', ephemeral=True)
            else:
                await interaction.send(embed = create_error_embed('Ты уже учавствуешь в данном конкурсе'), ephemeral = True)
        else:
            await interaction.send(embed=create_error_embed('Данный розыгрыш уже не актуален :('), ephemeral=True)
    if "ttp" in interaction.component.custom_id:
        draw_id = int(interaction.component.custom_id[3:])
        user_id = (await DBRequests.get_user_by_discord_id(str(interaction.author.id)))[1][0]
        if get_current_draw()['id'] == draw_id:
            reg = await DBRequests.insert_text_draw_member(draw_id, user_id, 0)
            if reg[0]:
                await interaction.send('Отлично, ты теперь учавствуешь в конкурсе! А теперь, бегом выполнять условие, чтобы стать первым :)', ephemeral=True)
            else:
                await interaction.send(embed = create_error_embed('Ты уже учавствуешь в данном конкурсе'), ephemeral = True)
        else:
            await interaction.send(embed=create_error_embed('Данный розыгрыш уже не актуален :('), ephemeral=True)


@bot.event
async def on_voice_state_update(member, before, after):
    Log.i('on_voice_state_update', f"Event called by {member}")
    draw_id = get_current_draw()['id']
    if draw_id is not None and get_current_draw()['type'] == 'voice':
        user_id = (await DBRequests.get_user_by_discord_id(str(member.id)))[1][0]
        reg = await DBRequests.get_voice_draw_member_by_id(user_id, draw_id)
        if reg[0]:
            if after.self_mute is False and before.self_mute is True:
                await voice_ctrl.start(user_id)
            elif after.self_mute is True and before.self_mute is False:
                await voice_ctrl.end(user_id)
                await voice_ctrl.compile_result(user_id, draw_id)
            elif before.channel is None and after.channel is not None:
                if after.self_mute is False:
                    await voice_ctrl.start(user_id)
            elif before.channel is not None and after.channel is None:
                if before.self_mute is False:
                    await voice_ctrl.end(user_id)
                    await voice_ctrl.compile_result(user_id, draw_id)




@bot.event
async def on_modal_submit(interaction):
    if interaction.custom_id == "voice_modal":
        if get_current_draw()['id'] == None:
            text = interaction.text_values['voice_text']
            award = interaction.text_values['voice_award']
            try:
                count = float(interaction.text_values['voice_count'])
                time = float(interaction.text_values['voice_time'])
            except Exception as e:
                Log.e("on_modal_submit", str(e))
                return await interaction.send(embed = create_error_embed("Время розыгрыша и время проведения в голосовом канале должны являться числами и не содержать никаких букв и прочих символов!"), ephemeral = True)
            if count >= time:
                return await interaction.send(embed = create_error_embed("Количество времени розыгрыша должно быть больше количества времени в голосовом канале"), ephemeral = True)
            ui = disnake.ui.View()
            announcement = await voice_extra.fetch('announcement')
            anno = await bot.fetch_channel(announcement)
            channel = await voice_extra.fetch('channel')
            current = await DBRequests.insert_voice_draw(str(channel), count, time, False)
            set_current_draw(current[1], DrawTypes.VOICE, text, award, time, count, announcement)
            ui.add_item(Button(
                label="Принимаю участие!",
                style=ButtonStyle.blurple,
                custom_id=f"vtp{current[1]}"
            ))
            await anno.send(embed= await create_anno_embed(bot, text, award, time, count, DrawTypes.VOICE, channel), view=ui)
            await interaction.send("Успешно!", ephemeral=True)

    if interaction.custom_id == "text_modal":
        if get_current_draw()['id'] == None:
            text = interaction.text_values['text_text']
            award = interaction.text_values['text_award']
            try:
                count = float(interaction.text_values['text_count'])
                time = float(interaction.text_values['text_time'])
            except Exception as e:
                Log.e("on_modal_submit", str(e))
                return await interaction.send(embed = create_error_embed("Время розыгрыша и количество сообщений в текстовом канале должны являться целыми числами и не содержать никаких букв и прочих символов!"), ephemeral = True)
            ui = disnake.ui.View()
            announcement = await text_extra.fetch('announcement')
            anno = await bot.fetch_channel(announcement)
            channel = await text_extra.fetch('channel')
            current = await DBRequests.insert_text_draw(str(channel), count, time, False)
            set_current_draw(current[1], DrawTypes.TEXT, text, award, time, count, announcement)
            ui.add_item(Button(
                label="Принимаю участие!",
                style=ButtonStyle.blurple,
                custom_id=f"ttp{current[1]}"
            ))
            await anno.send(embed= await create_anno_embed(bot, text, award, time, count, DrawTypes.TEXT, channel), view=ui)
            await interaction.send("Успешно!", ephemeral=True)



@bot.event
async def on_command_error(ctx, error):
    await ctx.send(
        embed = Embed(
            title="Ой, произошла ошибка!",
            description=f"```{error}```",
            color=disnake.Color.red()
        )
    )
    raise error

@bot.event
async def on_slash_command_error(interaction, error):
    await interaction.send(
        embed = Embed(
            title="Ой, произошла ошибка!",
            description=f"```{error}```",
            color=disnake.Color.red()
        )
    )
    raise error

try:
    bot.run(get_bot_token())
except Exception as e:
    set_bot_token(None)
    raise e

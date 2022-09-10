import discord
from discord.ext import commands, tasks
from pickle import dump, load, HIGHEST_PROTOCOL
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from urllib.request import urlretrieve, install_opener, build_opener
from discord_components import DiscordComponents
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle
from quart import Quart, redirect, url_for, session, request, render_template, flash, jsonify
from quart_discord import DiscordOAuth2Session, requires_authorization, Unauthorized
from datetime import datetime
from io import BytesIO
from re import search
from sys import setrecursionlimit

setrecursionlimit(2000)

intents = discord.Intents.default()
intents.members = True
Dev_Token = "OTc4NDIyMzQ5ODYwODU5OTA1.GKZoIK.WNaObiwOKFa9J5MAatfRi-i2r40qaFNngXEsHY"
bot = commands.Bot(intents=intents, command_prefix="$", description="Testiiiiiing", case_insensitive=True, help_command=None)
opener = build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
install_opener(opener)
bal_schema = Image.open("schema.png")
rank_schema = Image.open("card.png")
progress = Image.open('progress.png').convert('RGB')

levels = {"1":100, "2":500, "3":1000, "4":1500, "5":2000, "6":6000, "7":6700, "8":7000,
          "9":9000, "10":10000, "11":15000, "12":20000, "13":37000, "14":40000, "15":45000, "16":50000, "17":55000,
          "18":60000, "19":66000, "20":80000}

class person:
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.lbinga = 0
        self.is_claimed = False
        self.day = 0
        self.invites = 0
        self.lvl = 1
        self.xp = 0
        self.mission = 1
        self.dashboard = False
        self.history = []

    def daily_claim(self):
        if self.day == 1: self.lbinga += 5; return 5
        elif self.day == 2: self.lbinga += 10; return 10
        elif self.day == 3: self.lbinga += 15; return 15
        elif self.day == 4: self.lbinga += 20; return 20
        elif self.day == 5: self.lbinga += 25; return 25
        elif self.day == 6: self.lbinga += 30; return 30
        else: self.day = 1; self.lbinga += 5; return 5

    def lvlup(self):
        if self.xp == levels["2"] and self.lvl == 1: self.lvl += 1
        elif self.xp == levels["3"] and self.lvl == 2: self.lvl += 1
        elif self.xp == levels["4"] and self.lvl == 3: self.lvl += 1
        elif self.xp == levels["5"] and self.lvl == 4: self.lvl += 1
        elif self.xp == levels["6"] and self.lvl == 5: self.lvl += 1
        elif self.xp == levels["7"] and self.lvl == 6: self.lvl += 1
        elif self.xp == levels["8"] and self.lvl == 7: self.lvl += 1
        elif self.xp == levels["9"] and self.lvl == 8: self.lvl += 1
        elif self.xp == levels["10"] and self.lvl == 9: self.lvl += 1
        elif self.xp == levels["11"] and self.lvl == 10: self.lvl += 1
        elif self.xp == levels["12"] and self.lvl == 11: self.lvl += 1
        elif self.xp == levels["13"] and self.lvl == 12: self.lvl += 1
        elif self.xp == levels["14"] and self.lvl == 13: self.lvl += 1
        elif self.xp == levels["15"] and self.lvl == 14: self.lvl += 1
        elif self.xp == levels["16"] and self.lvl == 15: self.lvl += 1
        elif self.xp == levels["17"] and self.lvl == 16: self.lvl += 1
        elif self.xp == levels["18"] and self.lvl == 17: self.lvl += 1
        elif self.xp == levels["19"] and self.lvl == 18: self.lvl += 1
        elif self.xp == levels["20"] and self.lvl == 19: self.lvl += 1


async def create_wallet(user):
    globals()["User_" + str(user.id)] = person(user.name, user.id)
    users.append(globals()["User_" + str(user.id)])

async def balance_graph(user, bal_schema):
    if "j" in user.name: degree = "VIP Member"
    else: degree = "Verified Member"
    urlretrieve(str(user.avatar_url).split("?")[0], f"temp/{user.id}.png")
    profile = Image.open(f"temp/{user.id}.png").resize((185, 185))
    schema = bal_schema.copy()
    img = ImageDraw.Draw(schema)
    img.text((445, 1155), str(user), fill =(255, 255, 255), font=ImageFont.truetype("arial.ttf", 100))
    img.text((480, 610), str(globals()['User_' + str(user.id)].lbinga) + " Binga", fill =(255, 255, 255), font=ImageFont.truetype("arial.ttf", 200))
    img.text((160, 310), degree, fill =((255, 255, 10) if "VIP" in degree else (255, 255, 255)), font=ImageFont.truetype("arial.ttf", 90))
    empty = schema.copy()
    empty.paste(profile, (198, 1118))
    empty.paste(schema, schema)
    arr = BytesIO()
    empty.save(arr, format='PNG')
    arr.seek(0)
    return arr

def size(xp, lvl_xp):
    if (len(str(xp)) == 3 or len(str(xp)) == 2) and len(str(lvl_xp)) == 3: return (705, 188)
    elif len(str(xp)) == 3 and len(str(lvl_xp)) == 4: return (693, 188)
    elif len(str(xp)) == 4 and len(str(lvl_xp)) == 4: return (675, 188)
    elif len(str(xp)) == 4 and len(str(lvl_xp)) == 5: return (660, 188)
    else: return (645, 188)

async def rank_graph(user, ctx, rank_schema, per, progress):
    async with ctx.typing():
        im = progress.copy()
        draw = ImageDraw.Draw(im)
        color = (98,211,245)
        beg, end = levels[str(per.lvl)], levels[str(per.lvl+1)]
        y, diam, x = 8, 34, int((((per.xp - beg) * 100) / (end - beg) * (590 - 1) / 100) + 1)
        draw.ellipse([x,y,x+diam,y+diam], fill=(98,211,245))
        ImageDraw.floodfill(im, xy=(14,24), value=(98,211,245), thresh=40)
        urlretrieve(str(user.avatar_url).split("?")[0], f"temp/{user.id}.png")
        profile = Image.open(f"temp/{user.id}.png").resize((182, 182))
        schema = rank_schema.copy()
        img = ImageDraw.Draw(schema)
        per_lvl = per.lvl + 1
        img.text((245, 70), str(user), fill =(255, 255, 255), font=ImageFont.truetype("arial.ttf", 35))
        img.text(size(per.xp, levels[str(per_lvl)]), str(f"{per.xp} / {levels[str(per_lvl)]}"), fill =(128, 128, 190), font=ImageFont.truetype("arial.ttf", 30))
        img.text((840, 73), str(per.lvl), fill =(128, 128, 190), font=ImageFont.truetype("arial.ttf", 30))
        img.text((356, 166), str([i.id for i in (QuickSort(users, "xjd")[::-1])].index(user.id)+1), fill =(255, 255, 255), font=ImageFont.truetype("arial.ttf", 60))
        empty = schema.copy()
        empty.paste(profile, (30, 45))
        empty.paste(schema, schema)
        empty.paste(im, (240, 115))
        empty.save(f"temp/rank_{user.id}.png")

def QuickSort(arr, p):
    elements = len(arr)
    if elements < 2: return arr
    if p == "b":
        CurrentP = 0 
        for i in range(1, elements):
            if arr[i].lbinga <= arr[0].lbinga:
                CurrentP += 1
                temp = arr[i]
                arr[i] = arr[CurrentP]
                arr[CurrentP] = temp
        temp = arr[0]
        arr[0] = arr[CurrentP] 
        arr[CurrentP] = temp 
        arr = QuickSort(arr[0:CurrentP], 0) + [arr[CurrentP]] + QuickSort(arr[CurrentP+1:elements], 0)
    else:
        CurrentP = 0 
        for i in range(1, elements):
            if arr[i].xp <= arr[0].xp:
                CurrentP += 1
                temp = arr[i]
                arr[i] = arr[CurrentP]
                arr[CurrentP] = temp
        temp = arr[0]
        arr[0] = arr[CurrentP]
        arr[CurrentP] = temp 
        arr = QuickSort(arr[0:CurrentP], 1) + [arr[CurrentP]] + QuickSort(arr[CurrentP+1:elements], 1)
    return arr


def isExsist(varx):
    try:
        globals()[varx].name = globals()[varx].name
        return True
    except KeyError:
        return False

def mention_exist(var):
    try:
        _ = var.mentions[0]
        return True
    except:
        return False

@tasks.loop(seconds=86400)
async def daily_loop():
    for user in users:
        if user.is_claimed == True:
            user.day += 1
            user.is_claimed = False
        else:
            user.day = 1
    for user in users:
        for l in range(1, len(levels)+1):
            if user.xp < levels[str(l)]:
                user.lvl = l-1
                break

# @tasks.loop(seconds=60)
# async def update_data():
#     with open("binga_users.pkl", 'wb') as outp:
#         dump(users, outp, HIGHEST_PROTOCOL)
#     print("DataBase Updated successfully.")

@bot.event
async def on_ready():
    if not daily_loop.is_running():
        await bot.change_presence(activity=discord.Game(name="MVC the future."))
        globals()["cmd_channels"] = [978426156325933156]
        globals()["users"] = []
        globals()["server"] = bot.guilds[0]
        # globals()["logs"] = bot.get_channel(962525997335453716)

        with open("binga_users.pkl", 'rb') as inp:
            old = load(inp)

        for member in server.members:
            user = member.id
            globals()["User_" + str(user)] = person(member.name, user)
            users.append(globals()["User_" + str(user)])

        TOTALID = [i.id for i in users]

        for usr in old:
            if not usr.id in TOTALID:
                globals()[f"User_{usr.id}"] = person(usr.name, usr.id)
                user = globals()[f"User_{usr.id}"]
                user.lbinga = usr.lbinga
                user.lvl = usr.lvl
                user.xp = usr.xp
                user.day = usr.day
                user.is_claimed = usr.is_claimed
                user.invites = usr.invites
                user.mission = usr.mission
                user.dashboard = False
                user.history = []
                users.append(globals()[f"User_{usr.id}"])
            else:
                globals()[f"User_{usr.id}"] = person(usr.name, usr.id)
                users.append(globals()[f"User_{usr.id}"])

        # for user in users:
        #     for usr in old:
        #         if user.id == usr.id:
        #             user.lbinga = usr.lbinga
        #             user.lvl = usr.lvl
        #             user.xp = usr.xp
        #             user.day = usr.day
        #             user.is_claimed = usr.is_claimed
        #             user.invites = usr.invites
        #             user.mission = usr.mission
        #             break

        daily_loop.start()
        # update_data.start()

        # DailyEmbed = discord.Embed(title="Daily Bonus", description='Click **Daily** to claim your daily bonus!', color=0x00ff00)
        # await discord.utils.get(bot.get_all_channels(), guild__name=server.name, id=1003399518601089124).send(embed=DailyEmbed, components=[create_actionrow(*[create_button(style=ButtonStyle.green,label="Daily"),])])

        # WorkEmbed = discord.Embed(title="Work System", description='Click **Claim** to claim your Work reward', color=0x00ff00)
        # await discord.utils.get(bot.get_all_channels(), guild__name=server.name, id=1003399557134159882).send(embed=WorkEmbed, components=[create_actionrow(*[create_button(style=ButtonStyle.green,label="Claim"), create_button(style=ButtonStyle.grey,label="Work"),])])

        DiscordComponents(bot)
        print("Bot is Online !")

@bot.event
async def on_member_join(member):
    if member.id not in [usr.id for usr in users]:
        globals()["User_" + str(member.id)] = person(member.name, member.id)
        users.append(globals()["User_" + str(member.id)])

@bot.command()
async def rank(ctx):
    if ctx.channel.id in cmd_channels:
        if isExsist("User_" + str(ctx.author.id)):
            if mention_exist(ctx.message): 
                if server.get_member(ctx.author.id).guild_permissions.administrator == True: user = ctx.message.mentions[0]
            else: user = ctx.author
            await rank_graph(user, ctx, rank_schema, globals()["User_" + str(user.id)], progress)
            await ctx.send(file=discord.File(f"temp/rank_{user.id}.png"))
        else:
            await create_wallet(ctx.author)
            await balance(ctx)

@bot.command(aliases=['bal'])
async def balance(ctx):
    if ctx.channel.id in cmd_channels:
        if isExsist("User_" + str(ctx.author.id)):
            if mention_exist(ctx.message): 
                if server.get_member(ctx.author.id).guild_permissions.administrator == True: user = ctx.message.mentions[0]
            else: user = ctx.author
            async with ctx.typing():
                bal = await balance_graph(user, bal_schema)
                file = discord.File(fp=bal, filename=f"bal_{user.id}.png")
                await ctx.send(file=file)
                await ctx.message.delete()
        else:
            await create_wallet(ctx.author)
            await balance(ctx)

@bot.command(aliases=['send'])
async def trans(ctx, arg1, arg2):
    if server.get_member(ctx.author.id).guild_permissions.administrator == True:
        to = ctx.message.mentions
        frm = globals()[f"User_{ctx.author.id}"]
        now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        for i in to:
            globals()["User_" + str(i.id)].lbinga += int(arg1)
            globals()["User_" + str(i.id)].history.append({"from":f"{frm.name}:{frm.id}", "to":f"{i.name}:{i.id}" , "value":int(arg1), "date":now})
            frm.history.append({"from":f"{frm.name}:{frm.id}", "to":f"{i.name}:{i.id}" , "value":int(arg1), "date":now})
        await ctx.send(f"{', '.join(['<@'+str(i.id)+'>' for i in to])} recieved **{arg1}฿** from **{ctx.author.name}** <:binga:958417539438895135>")
    else:
        if ctx.channel.id in cmd_channels:
            user = ctx.author.id
            frm = globals()[f"User_{ctx.author.id}"]
            to = ctx.message.mentions[0]
            now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            if isExsist("User_" + str(to.id)):
                if globals()["User_" + str(user)].lbinga >= int(arg1):
                    globals()["User_" + str(to.id)].lbinga += int(arg1)
                    globals()["User_" + str(user)].lbinga -= int(arg1)

                    to.history.append({"from":f"{frm.name}:{frm.id}", "to":f"{to.name}:{to.id}" , "value":int(arg1), "date":now})
                    frm.history.append({"from":f"{frm.name}:{frm.id}", "to":f"{to.name}:{to.id}" , "value":int(arg1), "date":now})

                    await ctx.send(f"**{to.name}** recieved **{arg1}฿** from **{ctx.author.name}** <:binga:958417539438895135>")
                    await logs.send(f"**{ctx.author.name}** sent **{arg1}฿** to **{to.name}**")

                else: await ctx.send("You don't have Enough *binga* to transfer")
            else:
                await create_wallet(to)
                await trans(ctx, arg1, arg2)

@bot.command(aliases=['help', 'binga'])
async def info(ctx):
    await ctx.send("""
**Commandes :**
```
$trans & $send : to transfer binga's to Someone [$send <value> @Someone].\n
$bal & $balance : to check your balance.\n
$top3 : to show info about top 3 binga wallets.\n
$rank : to get info about your xp and level.\n
$info & $help : to get info help about the commandes.
```
""")

@bot.command(aliases=['top', 'top3'])
async def top5(ctx):
    if ctx.channel.id in cmd_channels:
        top = [(i.id, i.lbinga) for i in ((QuickSort(users, "b"))[::-1])[0:3]]
        embedVar = discord.Embed(title="► Top 3 binga wallets ◄", color=0x00ff00)
        embedVar.add_field(name="\u200b", value=f":first_place: <@{top[0][0]}>  :  {top[0][1]}฿", inline=False)
        embedVar.add_field(name="\u200b", value=f":second_place: <@{top[1][0]}>  :  {top[1][1]}฿", inline=False)
        embedVar.add_field(name="\u200b", value=f":third_place: <@{top[2][0]}>  :  {top[2][1]}฿", inline=False)
        await ctx.send(embed=embedVar)

@bot.command(aliases=['rest', 'res'])
async def reset(ctx, arg1):
    if server.get_member(ctx.author.id).guild_permissions.administrator == True:
        to = ctx.message.mentions[0]
        if isExsist("User_" + str(to.id)):
            globals()["User_" + str(to.id)].lbinga = 0
            globals()["User_" + str(to.id)].lvl = 1
            globals()["User_" + str(to.id)].xp = 0
            globals()["User_" + str(to.id)].mission = 1
            await ctx.send(f"**{to.name}** has been reseted to **0฿, 0xp, level 1** :white_check_mark:")
            await ctx.message.delete()
        else:
            await create_wallet(to)
            await reset(ctx, arg1)

@bot.command()
async def addxp(ctx, arg1, arg2):
    if server.get_member(ctx.author.id).guild_permissions.administrator == True:
        to = ctx.message.mentions[0]
        if isExsist("User_" + str(to.id)):
            user = globals()["User_" + str(to.id)]
            user.xp += int(arg1)
            for l in range(1, len(levels)+1):
                if user.xp < levels[str(l)]:
                    user.lvl = l-1
                    break
            await ctx.send(f"**{arg1} xp** added to **{to.name}** !")
        else: 
            await create_wallet(to)
            await addxp(ctx, arg1, arg2)

@bot.command()
async def gift(ctx, arg1, arg2):
    if server.get_member(ctx.author.id).guild_permissions.administrator == True:
        to = ctx.message.mentions[0]
        if isExsist("User_" + str(to.id)):
            globals()["User_" + str(to.id)].lbinga += int(arg1)

            now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            globals()["User_" + str(to.id)].history.append({"from":f"{ctx.author.name}:{ctx.author.id}", "to":f"{to.name}:{to.id}" , "value":int(arg1), "date":now})

            await ctx.send(f"**{arg1}฿** Gifted to **{to.name}** <:binga:958417539438895135> :gift:")
            await ctx.message.delete()
        else:
            await create_wallet(to)
            await gift(ctx, arg1, arg2)

@bot.command()
async def setday(ctx, arg1):
    if server.get_member(ctx.author.id).guild_permissions.administrator == True:
        if int(arg1) == 0:
            for user in users:
                user.is_claimed = True      
        for user in users:
            user.day = int(arg1)
            user.is_claimed = False
        await ctx.message.delete()

@bot.command()
async def prefix(ctx, arg1):
    if server.get_member(ctx.author.id).guild_permissions.administrator == True:
        bot.command_prefix = str(arg1)
        await ctx.send(f"Bot Prefix now is '{arg1}'")
        await ctx.message.delete()

@bot.command()
async def dev(ctx, arg1):
    if server.get_member(ctx.author.id).guild_permissions.administrator == True:
        if isExsist("User_" + str(arg1)):
            total = 0
            for i in await server.invites():
                if str(i.inviter.id) == str(arg1):
                    total += i.uses
            usr = globals()["User_" + str(arg1)]
            await ctx.send(f"{'-'*40}\nName: **{usr.name}**\nID: **{usr.id}**\nbinga: **{usr.lbinga}฿**\nLvL: **{usr.lvl}**\nXp: **{usr.xp}**\nMission: **{usr.mission}**\nDB_Invites: **{usr.invites}**\nReal_Invites: **{total}**\nIs_claimed: **{usr.is_claimed}**\n{'-'*40}")
        else: await ctx.send(f"user {arg1} does not exist")

@bot.command()
async def fixdb(ctx):
    if server.get_member(ctx.author.id).guild_permissions.administrator == True:
        for user in users:
            if user.lvl == 0: user.lvl = 1
            for l in range(1, len(levels)+1):
                if user.xp < levels[str(l)]:
                    user.lvl = l-1
                    break

@bot.command()
async def dev_edit(ctx, arg1, arg2, arg3):
    if server.get_member(ctx.author.id).guild_permissions.administrator == True:
        if isExsist("User_" + str(arg1)):
            try:
                exec(f"globals()['User_{arg1}'].{arg2} = {arg3}")
                await fixdb(ctx)
            except:
                await ctx.send("something went wrong")
        else: await ctx.send(f"user {arg1} does not exist")

@bot.event
async def on_button_click(click):
    try:
        if click.component.label.startswith("Daily"):
            user = click.author.id
            user = globals()["User_" + str(user)]
            if user.is_claimed == False:
                user.is_claimed = True
                await click.respond(type=4, embed=discord.Embed(title="Daily Bonus", description=f"**{click.author.name}** You have claimed **{user.daily_claim()}฿** as a Daily Bonus <:binga:958417539438895135>", color=0x00ff00))
            else: await click.respond(type=4, embed=discord.Embed(title="Daily Bonus", description=f"**{click.author.name}** You already claimed your daily Bonus ! :x:", color=0xba0000))
        elif click.component.label.startswith("Claim"):
            user = globals()["User_" + str(click.author.id)]
            if user.mission == 1:
                total_invites = 0
                for i in await server.invites():
                    if i.inviter == click.author:
                        total_invites += i.uses
                pure_invites = total_invites - user.invites
                if pure_invites >= 3:
                    if user.xp >= 500:
                        user.lbinga += 30
                        user.invites = user.invites + pure_invites
                        user.mission += 1
                        await click.respond(type=4, embed=discord.Embed(title="Work System", description="You've been Rewarded **30฿** for Completing **Mission #1** <:binga:958417539438895135>", color=0x00ff00))
                    else: await click.respond(type=4, embed=discord.Embed(title="Work System", description=f"**{click.author}** You need to gain at least 500 xp under 3 days. :x:", color=0xba0000))
                else: await click.respond(type=4, embed=discord.Embed(title="Work System", description=f"**{click.author}** You need to invite at least {3-pure_invites} people to claim your reward. :x:", color=0xba0000))
            elif user.mission == 2:
                support = await server.create_text_channel(f'mission#2_{click.author.id}')
                await support.set_permissions(server.default_role, view_channel=False, send_messages=False, read_message_history=False, read_messages=False)
                await support.set_permissions(click.author, view_channel=True, send_messages=True, read_message_history=True, read_messages=True, attach_files=True, )
                await support.send(f'<@&930099848944959598> the User "<@{click.author.id}>" is requesting a mission#2 verification. !')
                globals()["cmd_channels"].append(support.id)
                user.mission += 1
                check = lambda m: m.content == "close." and m.channel == support
                msg = await bot.wait_for('message', check=check)
                await support.delete()
                globals()["cmd_channels"].remove(support.id)
            else: await click.respond(type=4, embed=discord.Embed(title="Work System", description=f"**{click.author}** We don't have any Work for you currently. :x:", color=0xba0000))

        elif click.component.label.startswith("Work"):
            user = globals()["User_" + str(click.author.id)]
            if user.mission == 1:
                await click.respond(type=4, embed=discord.Embed(title="Work System", description="-**Mission #1**-\nYour goal is to invite three people to the discord server and earn up to 500 xp under 3 days.", color=0xba0000))
            elif user.mission == 2:
                m2 = discord.Embed(title="Work System", description="**Tasks :**")
                m2.add_field(name="#1", value="Follow us on instagram.", inline=False)
                m2.add_field(name="#2", value="Share instagram story.", inline=False)
                m2.add_field(name="#3", value="Follow us on twitter.", inline=False)
                m2.add_field(name="#4", value="Tag 3 people in our last post on instagarm.", inline=False)
                m2.set_footer(text="Notice : You should prove these actions with screenshots, when you're done click claim to request a screenshot verification.")
                await click.respond(type=4, embed=m2)
            else:
                await click.respond(type=4, embed=discord.Embed(title="Work System", description="**Sorry currently we don't have any missions left, we'll inform you if we opened a new mission !**"))
    except:
        pass

@bot.event
async def on_message(ctx):
    await bot.process_commands(ctx)
    if not ctx.author.bot and "$" not in ctx.content:
        user = globals()["User_" + str(ctx.author.id)]
        user.xp += 10
        current_lvl = user.lvl
        user.lvlup()
        if user.lvl > current_lvl:
            user.lbinga += 10
            await bot.get_channel(1003399587710640178).send(f"Mbrok <@{ctx.author.id}>, You've reached level {user.lvl}! You've rewarded 10 binga's")

app = Quart(__name__)
app.secret_key = b"s1kefl@sk1s@we@akfr@mw0rk"
developer_keys = ["s1kefl@sk1s@we@akfr@mw0rk", "test"]
app.config["DEBUG"] = True
app.config["DISCORD_CLIENT_ID"] = 978422349860859905
app.config["DISCORD_CLIENT_SECRET"] = "PoeYEjxX2HodCMxF23Vgei3NonQz2-Bd"
app.config["DISCORD_REDIRECT_URI"] = "http://127.0.0.1/callback"
app.config["DISCORD_BOT_TOKEN"] = "OTc4NDIyMzQ5ODYwODU5OTA1.G313ZP.L4RgM6tCBORUH72-0ZRnt5eUi6-4ZKfoxe9_QE"

discord_oath = DiscordOAuth2Session(app)

@app.route("/livesuggest", methods=["POST", "GET"])
async def live_suggestions():
    char = (await request.form)["search"]
    print(char)
    data = [f"{i.name}:{i.id}" for i in users]
    data = [i for i in data if search(char, i)]
    data = tuple(data)
    return jsonify(data)

@app.route("/login/")
async def login():
    return await discord_oath.create_session()

@app.route("/callback/")
async def callback():
    await discord_oath.callback()
    return redirect(url_for(".me"))

@app.errorhandler(Unauthorized)
async def redirect_unauthorized(e):
    return await render_template("unauth.html")
    
@app.route("/me/")
@requires_authorization
async def me():
    user = await discord_oath.fetch_user()
    session.permanent = True
    session["id"] = user.id
    return redirect(url_for("dashboard"))

@app.route("/index")
async def index():
    return await render_template("index.html")

@app.route("/", methods=['GET', 'POST'])
@app.route("/dashboard", methods=['GET', 'POST'])
@requires_authorization
async def dashboard():
    user = await discord_oath.fetch_user()
    usr = globals()[f"User_{user.id}"]
    
    if request.method == 'POST':

        if (await request.form)['button'] == 'daily':
            if usr.is_claimed == False:
                usr.is_claimed = True
                await flash(f"You have claimed {usr.daily_claim()} ฿", "success")
                return redirect(url_for("dashboard"))
            else:
                await flash("you have already claimed your daily", "info")
                return redirect(url_for("dashboard"))

        elif (await request.form)['button'] == 'message':
            await flash("This form is still under dev, also it needs front end :)", "info")
            return redirect(url_for("dashboard"))

        elif (await request.form)['button'] == 'logout':
            discord_oath.revoke()
            return redirect(url_for("index"))

        elif (await request.form)['button'] == 'send':
            send_to = (await request.form)['send_to']
            send_to = send_to.split(":")[1]
            value = (await request.form)['value']

            if isExsist(f"User_{send_to}"):
                if usr.lbinga >= int(value):

                    to = globals()[f"User_{int(send_to)}"]
                    usr.lbinga -= int(value)
                    to.lbinga += int(value)
                    try:
                        dm_channel = await server.get_member(int(send_to)).create_dm()
                        await dm_channel.send(f"<@{usr.id}> sent you **{value}฿**")
                    except:
                        pass
                    now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                    to.history.append({"from":f"{usr.name}:{usr.id}", "to":f"{to.name}:{to.id}" , "value":int(value), "date":now})
                    usr.history.append({"from":f"{usr.name}:{usr.id}", "to":f"{to.name}:{to.id}" , "value":int(value), "date":now})

                    await flash(f"{value}฿ Has been sent succefuly to {to.id}:{to.name} !", "success")
                    return redirect(url_for("dashboard"))

                else:
                    await flash("You don't have enough Binga in your wallet.", "info")
                    return redirect(url_for("dashboard"))
            else:
                await flash("couldn't find this wallet ID!\nTry another wallet ID.", "error")
                return redirect(url_for("dashboard"))

    else: return await render_template('dashboard.html', users_suggest=[(i.name) for i in users], user_name=user.name, user_lbinga=usr.lbinga, user_avatar=user.avatar_url, user_rank=str([i.id for i in (QuickSort(users, "xjd")[::-1])].index(usr.id)+1), user_lvl=usr.lvl, user_xp=usr.xp, user_id=usr.id)

@app.route("/top")
async def top():
    html_list = []
    top = [(i.name, i.lbinga) for i in ((QuickSort(users, "b"))[::-1])[0:3]]
    for i in top:
        if i[0] == globals()[f'User_{session["id"]}'].name: 
            html_list.append(f"<h1><big>● {i[0]} : {i[1]} ●</big></h1>")
        else: html_list.append(f"<h2>{i[0]} : {i[1]}</h2>")
    html_text = "\n".join(html_list)
    return html_text

@app.route("/history")
async def hist():
    usr = globals()[f"User_{session['id']}"]
    html_list = []
    for act in usr.history:
        if str(usr.id) in str(act["from"]): html_list.append(f"<h2>{act['date']} -> You Sent {act['value']}฿ To {act['to']}</h2>")
        else: html_list.append(f"{act['date']} -> <h2>You Recieved {act['value']}฿ From {act['from']}</h2>")
    html_text = "\n".join(html_list)
    return html_text

@app.route("/api/in", methods=['GET', 'POST'])
async def api_in():
    content = await request.get_json(silent=True)
    if content["key"] in developer_keys:
        User = globals()[f"User_{content['UserID']}"]
        try:
            if content["what"] == "name": User.name = str(content["data"])
            elif content["what"] == "id": User.id = int(content["data"])
            elif content["what"] == "lbinga": User.lbinga = int(content["data"])
            elif content["what"] == "is_claimed": User.is_claimed = bool(content["data"])
            elif content["what"] == "day": User.day = int(content["data"])
            elif content["what"] == "invites": User.invites = int(content["data"])
            elif content["what"] == "level": User.lvl = int(content["data"])
            elif content["what"] == "xp": User.xp = int(content["data"])
            elif content["what"] == "mission": User.mission = int(content["data"])
            else:
                return jsonify({"response": "ERROR", "error": f"There is no Data under the name {content['what']}"})
            return jsonify({"response": "OK"})
        except Exception as e:
            return jsonify({"response": "ERROR", "error": str(e)})
    else:
        return jsonify({"response": "ERROR", "error": "You don't have access to the API Service."})

@app.route("/api/out", methods=['GET', 'POST'])
async def api_out():
    content = await request.get_json(silent=True)
    if content["key"] in developer_keys:
        User = globals()[f"User_{content['UserID']}"]
        try:
            if content["what"] == "name": data = User.name
            elif content["what"] == "id": data = User.id
            elif content["what"] == "lbinga": data = User.lbinga
            elif content["what"] == "is_claimed": data = User.is_claimed
            elif content["what"] == "day": data = User.day
            elif content["what"] == "invites": data = User.invites
            elif content["what"] == "level": data = User.lvl
            elif content["what"] == "xp": data = User.xp
            elif content["what"] == "mission": data = User.mission
            else:
                return jsonify({"response": "ERROR", "error": f"There is no Data under the name {content['what']}"})
            return jsonify({"response": "OK", "UserID": content["UserID"], "what": content["what"], "data": data})
        except Exception as e:
            return jsonify({"response": "ERROR", "error": str(e)})
    else:
        return jsonify({"response": "ERROR", "error": "You don't have access to the API Service."})

@app.route("/<bad_url>")
async def bad(bad_url):
    return "Bad_URL"

app.app_context()
bot.loop.create_task(api.app.run_task(host="0.0.0.0", port=PORT))
bot.run("OTc4NDIyMzQ5ODYwODU5OTA1.GqIJf5.13TcfQkQcFtbICWPh_uNt-5Mqf28Z-aViKE5Fw")

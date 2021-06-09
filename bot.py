import inspect
import math
import sqlite3
from discord.ext import commands
import discord
from googletrans import Translator
from google_images_search import GoogleImagesSearch

translator = Translator()

connection = sqlite3.connect('customcommands.db')

cursor = connection.cursor()

client = commands.Bot(command_prefix='t!')
client.remove_command('help')


main_guild = client.get_guild(828423940531159101)

gis = GoogleImagesSearch('AIzaSyC-i2O27A8za7mh6y6S12EBP7yzIRtGGXo', '1622d7da3fd654f12')


        


@client.event
async def on_ready():
    main_channel = client.get_channel(828423941017042964)
    print("bot is yesing")
    

@client.command(name="t")
async def s(ctx, ccname):
    command5 = f"""SELECT DISTINCT CUSTOMCOMMAND FROM CUSTOMCOMMANDS  WHERE CUSTOMCOMMAND = ("{ccname}")"""
    cursor.execute(command5)
    command6 = f"""SELECT WHATWILLCCSEND FROM CUSTOMCOMMANDS WHERE CUSTOMCOMMAND LIKE '%{ccname}%'"""
    cursor.execute(command6)
    result = cursor.fetchone()
    if result is not None:
        await ctx.send(result[0].replace("(,)", ""))


@client.command(name='eval', pass_context=True)
@commands.is_owner()
async def eval_(ctx, *, command):
    res = eval(command)
    if inspect.isawaitable(res):
        print(await res)
    else:
        print(res)


@client.command()
async def ping(ctx):
    embed = discord.Embed(
        title='Ping',
        description=f"Pong! `{math.floor(client.latency * 1000)}ms`",
        color=discord.Colour.orange()
    )

    embed.set_footer(text="i am racist")
    embed.set_image(
        url="https://media.discordapp.net/attachments/824625614312046592/844570716250963978/caption-5-1.gif")
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url_as(size=128))

    await ctx.send(embed=embed)


@client.command()
async def allcc(ctx):
    cursor.execute("SELECT CUSTOMCOMMAND FROM CUSTOMCOMMANDS")
    allccs = cursor.fetchall()
    embed = discord.Embed(
        title="All Custom Commands",
        description=allccs,
        color=discord.Colour.orange()
    )

    embed.set_footer(text=f"Number of custom commands is: {len(allccs)}")
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url_as(size=128))
    embed.set_thumbnail(
        url="https://media.discordapp.net/attachments/824625614312046592/844570716250963978/caption-5-1.gif")

    await ctx.send(embed=embed)


@client.command()
async def addcc(ctx, thing, *, thingtosend):
    command1 = """CREATE TABLE IF NOT EXISTS
    CUSTOMCOMMANDS(
    CUSTOMCOMMAND  TEXT  PRIMARY KEY NOT NULL,
    WHATWILLCCSEND TEXT              NOT NULL
    )"""
    cursor.execute(command1)
    cursor.execute(f'INSERT INTO CUSTOMCOMMANDs VALUES ("{thing}", "{thingtosend}")')
    connection.commit()
    await ctx.send("added " + thing + " in database")


@client.command()
async def removecc(ctx, *, thingtoremove):
    command4 = f"""DELETE FROM CUSTOMCOMMANDS WHERE  CUSTOMCOMMAND = {thingtoremove}"""
    cursor.execute(command4)
    connection.commit()
    result = cursor.fetchall()
    if result is not None:
        await ctx.send(f"deleted {result} from database")


@client.command()
@commands.is_owner()
async def removeallcc(ctx):
    cursor.execute("DELETE FROM CUSTOMCOMMANDS")
    connection.commit()
    await ctx.send("deleted every custom command from database")


@client.group(invoke_without_command=True)
async def help(ctx):
    embed = discord.Embed(
        title="Help",
        description="Use t!help to find out about all the commands",
        color=discord.Colour.orange()
    )
    embed.add_field(name="Custom Commands",
                    value="t!addcc {customcommand} {whatwillcustomcommandsend} \nt!removecc {customcommandname} \nt!removeallcc(tamim only) \nt!t {customcommandname}",
                    inline=False)
    embed.add_field(name="Status", value="t!ping")
    embed.add_field(name="Other", value="t!john_china")
    embed.add_field(name="Translation", value="t!translate {untranslated text} \nt!translate_from {from} {to} {untranslated text}")
    embed.set_footer(text="yo mama so fat")
    embed.set_author(name=ctx.author.name)

    await ctx.send(embed=embed)


@client.command()
async def john_china(ctx):
    await ctx.send("https://cdn.discordapp.com/attachments/792480412647161906/848385363709526046/video0_1.mp4")


@client.command()
async def translate(ctx, *, thingtotranslate):
    result = translator.translate(text=f'{thingtotranslate}', src='auto', dest='en')
    embed = discord.Embed(
        title="translation",
        color=discord.Colour.orange()
    )

    embed.set_footer(text="Note: This is not 100% correct so dont expect it to be exactly that")
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url_as(size=128))
    embed.add_field(name=f"From {result.src}", value=thingtotranslate)
    embed.add_field(name=f"To {result.dest}", value=result.text)

    if result is not None:
        await ctx.send(embed=embed)


@client.command()
async def translate_from(ctx, source, desti, *, thingtotranslate):
    result = translator.translate(text=f'{thingtotranslate}', src=f'{source}', dest=f'{desti}')
    embed = discord.Embed(
        title="translation",
        color=discord.Colour.orange()
    )

    embed.set_footer(text="Note: This is not 100% correct so dont expect it to be exactly that")
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url_as(size=128))
    embed.add_field(name=f"From {result.src}", value=thingtotranslate)
    embed.add_field(name=f"To {result.dest}", value=result.text)

    if result is not None:
        await ctx.send(embed=embed)

@client.command()
async def im(ctx, *, thingtosearxh):
    _search_params = {
    'q': f'{thingtosearxh}',
    'num': 1,
    'safe': 'high',
    'fileType': 'jpg|gif|png',
    'imgType': 'photo',
    'imgSize': 'huge|icon|large|medium|small|xlarge|xxlarge',
    'imgDominantColor': 'black|blue|brown|gray|green|pink|purple|teal|white|yellow',
    'rights': 'cc_publicdomain|cc_attribute|cc_sharealike|cc_noncommercial|cc_nonderived'
}
    embed = discord.Embed(
          title="the inage",
          color = discord.Color.orange()
        )
    gis.search(search_params=_search_params)
img = gis.results()

embed.set_image(url=img)

ctx.send(embed=embed)


with open("token.txt") as reader:
    TOKEN = reader.read()

client.run(TOKEN)

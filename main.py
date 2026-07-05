import discord
from discord.ext import commands
import json
import random
import string
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

FILE = "keys.json"

def load_data():
    if not os.path.exists(FILE):
        with open(FILE, "w") as f:
            json.dump({"keys": {}, "banned": []}, f)

    with open(FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)

@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")

@bot.command()
@commands.has_permissions(administrator=True)
async def genkey(ctx, jours: int):
    data = load_data()

    key = "-".join(
        "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
        for _ in range(4)
    )

    data["keys"][key] = {
        "owner": None,
        "days": jours,
        "used": False
    }

    save_data(data)

    await ctx.send(f"🔑 Clé créée : `{key}` ({jours} jours)")

@bot.command()
@commands.has_permissions(administrator=True)
async def listkeys(ctx):
    data = load_data()

    if len(data["keys"]) == 0:
        return await ctx.send("Aucune clé.")

    txt = ""

    for k, v in data["keys"].items():
        txt += f"{k} | Utilisée : {v['used']} | Durée : {v['days']} jours\n"

    await ctx.send(f"```{txt}```")

@bot.command()
async def redeem(ctx, key):
    data = load_data()

    if ctx.author.id in data["banned"]:
        return await ctx.send("❌ Tu es banni du système de clés.")

    if key not in data["keys"]:
        return await ctx.send("❌ Clé invalide.")

    if data["keys"][key]["used"]:
        return await ctx.send("❌ Cette clé est déjà utilisée.")

    data["keys"][key]["used"] = True
    data["keys"][key]["owner"] = ctx.author.id

    save_data(data)

    await ctx.send(f"✅ Clé activée pour {ctx.author.mention} pendant {data['keys'][key]['days']} jours.")

@bot.command()
@commands.has_permissions(administrator=True)
async def resetkey(ctx, key):
    data = load_data()

    if key not in data["keys"]:
        return await ctx.send("Clé introuvable.")

    data["keys"][key]["used"] = False
    data["keys"][key]["owner"] = None

    save_data(data)

    await ctx.send("✅ Clé réinitialisée.")

@bot.command()
@commands.has_permissions(administrator=True)
async def bankey(ctx, member: discord.Member):
    data = load_data()

    if member.id not in data["banned"]:
        data["banned"].append(member.id)

    save_data(data)

    await ctx.send(f"{member.mention} est banni du système de clés.")

@bot.command()
@commands.has_permissions(administrator=True)
async def unbankey(ctx, member: discord.Member):
    data = load_data()

    if member.id in data["banned"]:
        data["banned"].remove(member.id)

    save_data(data)

    await ctx.send(f"{member.mention} est débanni du système de clés.")

bot.run("TON_TOKEN")
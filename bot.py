import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import random
import datetime

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.messages = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.synced = False

    async def setup_hook(self):
        if not self.synced:
            await self.tree.sync()
            self.synced = True

bot = MyBot()

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")

# === Commandes Fun / Utilitaires ===

@bot.tree.command(name="ping", description="Répond Pong!")
async def slash_ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong !")

@bot.tree.command(name="say", description="Le bot répète ton message")
@app_commands.describe(message="Message à répéter")
async def slash_say(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(f"📣 {message}")

@bot.tree.command(name="choix", description="Choisit entre plusieurs options")
@app_commands.describe(options="Écris des choix séparés par des virgules")
async def slash_choix(interaction: discord.Interaction, options: str):
    choix = [o.strip() for o in options.split(",") if o.strip()]
    if len(choix) < 2:
        await interaction.response.send_message("⚠️ Donne au moins deux options séparées par des virgules.")
    else:
        selection = random.choice(choix)
        await interaction.response.send_message(f"🎲 Je choisis : **{selection}**")

# === Commandes de Modération ===

@bot.tree.command(name="clear", description="Supprime des messages")
@app_commands.describe(amount="Nombre de messages à supprimer (max 100)")
@app_commands.checks.has_permissions(manage_messages=True)
async def slash_clear(interaction: discord.Interaction, amount: int):
    if not interaction.channel.permissions_for(interaction.user).manage_messages:
        await interaction.response.send_message("🚫 Tu n'as pas la permission de faire ça.", ephemeral=True)
        return
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"🧹 {len(deleted)} messages supprimés.", ephemeral=True)

@bot.tree.command(name="kick", description="Expulse un membre")
@app_commands.describe(user="Utilisateur à expulser", reason="Raison (optionnelle)")
@app_commands.checks.has_permissions(kick_members=True)
async def slash_kick(interaction: discord.Interaction, user: discord.Member, reason: str = None):
    try:
        await user.kick(reason=reason)
        await interaction.response.send_message(f"👢 {user.mention} a été expulsé.")
    except Exception as e:
        await interaction.response.send_message(f"Erreur : {str(e)}")

@bot.tree.command(name="ban", description="Bannit un membre")
@app_commands.describe(user="Utilisateur à bannir", reason="Raison (optionnelle)")
@app_commands.checks.has_permissions(ban_members=True)
async def slash_ban(interaction: discord.Interaction, user: discord.Member, reason: str = None):
    try:
        await user.ban(reason=reason)
        await interaction.response.send_message(f"🔨 {user.mention} a été banni.")
    except Exception as e:
        await interaction.response.send_message(f"Erreur : {str(e)}")

@bot.tree.command(name="unban", description="Débannit un utilisateur avec son ID")
@app_commands.describe(user_id="ID du membre à débannir")
@app_commands.checks.has_permissions(ban_members=True)
async def slash_unban(interaction: discord.Interaction, user_id: int):
    user = await bot.fetch_user(user_id)
    try:
        await interaction.guild.unban(user)
        await interaction.response.send_message(f"♻️ {user.name} a été débanni.")
    except Exception as e:
        await interaction.response.send_message(f"Erreur : {str(e)}")

# === Autres permissions manquantes ? ===
@slash_clear.error
@slash_kick.error
@slash_ban.error
@slash_unban.error
async def perms_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("🚫 Tu n'as pas la permission pour cette commande.", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Une erreur est survenue.", ephemeral=True)

bot.run(TOKEN)
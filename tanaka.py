import discord
from discord.ext import commands
from discord import app_commands, ui
import asyncio
import time

TOKEN = "MTQ4MTIzMDgxNjAwNzY4NDI4MQ.GaqWsS.PaVLUht973kdC_ybT9J0Gs8ZKsyD5F97-WuFuA"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# -------------------------
# 認証ボタン
# -------------------------
class VerifyView(ui.View):
    def __init__(self, member_role, unverified_role):
        super().__init__(timeout=None)
        self.member_role = member_role
        self.unverified_role = unverified_role

    @ui.button(label="✅ 認証する", style=discord.ButtonStyle.green)
    async def verify(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.user.add_roles(self.member_role)
        await interaction.user.remove_roles(self.unverified_role)
        await interaction.response.send_message("✅ 認証完了！", ephemeral=True)

# -------------------------
# メンバー参加時
# -------------------------
@bot.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name="未認証")
    if role:
        await member.add_roles(role)

# -------------------------
# スパム対策
# -------------------------
spam = {}

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    uid = message.author.id
    now = time.time()

    if uid not in spam:
        spam[uid] = []

    spam[uid] = [t for t in spam[uid] if now - t < 5]
    spam[uid].append(now)

    # 5秒で5回発言 → タイムアウト
    if len(spam[uid]) >= 5:
        try:
            await message.author.timeout(discord.utils.utcnow() + discord.timedelta(minutes=5))
            await message.channel.send(f"{message.author.mention} スパムでタイムアウト")
        except:
            pass

    # 危険ワード削除
    bad_words = ["discord.gg/", "@everyone", "@here", "nitro", "無料配布"]
    if any(w in message.content.lower() for w in bad_words):
        try:
            await message.delete()
        except:
            pass

    await bot.process_commands(message)

# -------------------------
# SETUP（爆速＋完全構成）
# -------------------------
@bot.tree.command(name="setup", description="サーバーを最強構成にする")
async def setup(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild

    # -------------------------
    # 全チャンネル削除（爆速）
    # -------------------------
    await asyncio.gather(*[c.delete() for c in guild.channels], return_exceptions=True)

    # -------------------------
    # ロール作成
    # -------------------------
    unverified = await guild.create_role(name="未認証", color=discord.Color.light_gray())
    member = await guild.create_role(name="Member", color=discord.Color.green())
    admin = await guild.create_role(name="Admin", permissions=discord.Permissions.all())

    # -------------------------
    # 権限定義
    # -------------------------
    no = discord.PermissionOverwrite(view_channel=False)
    read = discord.PermissionOverwrite(view_channel=True, send_messages=False)
    write = discord.PermissionOverwrite(view_channel=True, send_messages=True)

    # -------------------------
    # 🛡️ 認証エリア
    # -------------------------
    sec_cat = await guild.create_category("🛡️｜認証", overwrites={
        guild.default_role: no,
        unverified: read,
        member: no
    })

    verify_ch = await guild.create_text_channel("認証", category=sec_cat)

    embed = discord.Embed(
        title="🔒 認証",
        description="ボタンを押して参加",
        color=0x2ecc71
    )

    await verify_ch.send(embed=embed, view=VerifyView(member, unverified))

    # -------------------------
    # 📢 お知らせ
    # -------------------------
    info_cat = await guild.create_category("📢｜お知らせ", overwrites={
        guild.default_role: no,
        unverified: no,
        member: read
    })

    await guild.create_text_channel("お知らせ", category=info_cat)
    await guild.create_text_channel("ルール", category=info_cat)

    # -------------------------
    # 💬 コミュニティ
    # -------------------------
    chat_cat = await guild.create_category("💬｜コミュニティ", overwrites={
        guild.default_role: no,
        unverified: no,
        member: write
    })

    await asyncio.gather(
        guild.create_text_channel("雑談", category=chat_cat),
        guild.create_text_channel("質問", category=chat_cat),
        guild.create_text_channel("メディア", category=chat_cat),
        guild.create_text_channel("コマンド", category=chat_cat),
    )

    # -------------------------
    # 🔊 通話
    # -------------------------
    vc_cat = await guild.create_category("🔊｜通話", overwrites={
        guild.default_role: no,
        unverified: no,
        member: write
    })

    await asyncio.gather(
        guild.create_voice_channel("通話1", category=vc_cat),
        guild.create_voice_channel("通話2", category=vc_cat),
        guild.create_voice_channel("ゲームVC", category=vc_cat),
    )

    # -------------------------
    # 🎮 ゲーム
    # -------------------------
    game_cat = await guild.create_category("🎮｜ゲーム", overwrites={
        guild.default_role: no,
        unverified: no,
        member: write
    })

    await asyncio.gather(
        guild.create_text_channel("フォートナイト", category=game_cat),
        guild.create_text_channel("APEX", category=game_cat),
        guild.create_text_channel("VALORANT", category=game_cat),
    )

    await interaction.followup.send("🔥 最強サーバー完成", ephemeral=True)

# -------------------------
# 起動
# -------------------------
bot.run(TOKEN)
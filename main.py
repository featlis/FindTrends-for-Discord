import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# インテントの設定 (デフォルトインテント)
intents = discord.Intents.default()
# コマンドプレフィックスはスラッシュコマンドメインなので適当に設定
bot = commands.Bot(command_prefix='!', intents=intents)

# 読み込む拡張機能(Cog)のリスト
INITIAL_EXTENSIONS = [
    'cogs.trends',
    'cogs.news'
]

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')
    
    # Cogの読み込み
    for extension in INITIAL_EXTENSIONS:
        try:
            await bot.load_extension(extension)
            print(f'Loaded extension: {extension}')
        except Exception as e:
            print(f'Failed to load extension {extension}.', e)
            
    # スラッシュコマンドの同期
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} slash command(s).')
    except Exception as e:
        print(f'Failed to sync commands.', e)

if __name__ == '__main__':
    if not TOKEN:
        print("エラー: .env ファイルに DISCORD_BOT_TOKEN が設定されていません。")
    else:
        bot.run(TOKEN)

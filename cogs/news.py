import discord
from discord.ext import commands
from discord import app_commands
import feedparser
import urllib.parse
import asyncio

class News(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="news", description="最新のニュースを取得します。")
    @app_commands.describe(
        keyword="検索するキーワード (未指定の場合はおすすめニュース)",
        timeframe="ニュースの期間 (デフォルト: 24時間)",
        count="表示する件数 (デフォルト: 5件)"
    )
    @app_commands.choices(timeframe=[
        app_commands.Choice(name="24時間", value="1d"),
        app_commands.Choice(name="1週間", value="7d"),
        app_commands.Choice(name="1ヶ月", value="30d"),
        app_commands.Choice(name="1年", value="1y")
    ])
    async def news(self, interaction: discord.Interaction, keyword: str = None, timeframe: app_commands.Choice[str] = None, count: int = 5):
        await interaction.response.defer()
        
        tf_val = timeframe.value if timeframe else "1d"
        
        # URLの構築
        if keyword:
            # キーワード指定がある場合
            query = urllib.parse.quote(f"{keyword} when:{tf_val}")
            url = f"https://news.google.com/rss/search?q={query}&hl=ja&gl=JP&ceid=JP:ja"
            title_text = f"📰 「{keyword}」のニュース ({timeframe.name if timeframe else '24時間'})"
        else:
            # キーワード指定がない場合
            if timeframe:
                # 期間指定がある場合は「ニュース」というキーワードで検索をかける
                query = urllib.parse.quote(f"ニュース when:{tf_val}")
                url = f"https://news.google.com/rss/search?q={query}&hl=ja&gl=JP&ceid=JP:ja"
                title_text = f"📰 おすすめニュース ({timeframe.name if timeframe else '24時間'})"
            else:
                # 完全デフォルト(期間指定もキーワード指定もなし)の場合、トップニュース
                url = "https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja"
                title_text = "📰 最新のおすすめトップニュース"

        try:
            # RSSのパースを非同期で実行
            loop = asyncio.get_event_loop()
            feed = await loop.run_in_executor(None, feedparser.parse, url)
            
            if not feed.entries:
                await interaction.followup.send("ニュースが見つかりませんでした。")
                return
            
            # 指定件数取得
            # APIやRSSによっては上限があるため、実際の件数と指定件数を比較して取得
            entries = feed.entries[:count]
            
            embed = discord.Embed(
                title=title_text,
                color=discord.Color.green()
            )
            
            for entry in entries:
                # タイトルとリンクを追加
                embed.add_field(
                    name=entry.title,
                    value=f"[記事を読む]({entry.link})",
                    inline=False
                )
            
            # フッターに出典元を表示
            embed.set_footer(text="Powered by Google News RSS")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            print(f"Error fetching news: {e}")
            await interaction.followup.send("ニュースの取得中にエラーが発生しました。")

async def setup(bot):
    await bot.add_cog(News(bot))

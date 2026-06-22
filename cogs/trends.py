import discord
from discord.ext import commands
from discord import app_commands
from pytrends.request import TrendReq
import asyncio

class Trends(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # pytrendsの初期化 (タイムゾーンは日本時間、言語は日本語)
        self.pytrends = TrendReq(hl='ja-JP', tz=540)

    @app_commands.command(name="trend", description="日本の現在の急上昇トレンドを取得します。")
    async def trend(self, interaction: discord.Interaction):
        # 処理に時間がかかる可能性があるため、考え中状態にする
        await interaction.response.defer()
        
        try:
            # 非同期でpytrendsの処理を実行してブロックを避ける
            loop = asyncio.get_event_loop()
            trending_df = await loop.run_in_executor(None, self.pytrends.trending_searches, 'japan')
            
            if trending_df.empty:
                await interaction.followup.send("トレンド情報が取得できませんでした。")
                return

            # 上位10件を取得
            trends_list = trending_df[0].tolist()[:10]
            
            # Embedの作成
            embed = discord.Embed(
                title="📈 現在の急上昇トレンド (日本)",
                color=discord.Color.blue()
            )
            
            for i, trend in enumerate(trends_list, 1):
                embed.add_field(name=f"第{i}位", value=trend, inline=False)
                
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            print(f"Error fetching trends: {e}")
            await interaction.followup.send("トレンドの取得中にエラーが発生しました。時間をおいて再度お試しください。")

async def setup(bot):
    await bot.add_cog(Trends(bot))

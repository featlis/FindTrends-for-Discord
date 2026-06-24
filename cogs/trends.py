import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import aiohttp
import xml.etree.ElementTree as ET
from urllib.parse import quote

RSS_URL = "https://trends.google.co.jp/trending/rss?geo=JP"
RSS_NS = {"ht": "https://trends.google.com/trending/rss"}


def _parse_rss(xml_bytes: bytes) -> list[dict]:
    """RSSバイト列をパースしてトレンドリストを返す。"""
    root = ET.fromstring(xml_bytes)
    channel = root.find("channel")
    results = []
    for item in channel.findall("item"):
        title = item.findtext("title") or "不明"
        traffic = item.findtext("ht:approx_traffic", namespaces=RSS_NS) or "N/A"
        picture = item.findtext("ht:picture", namespaces=RSS_NS)
        results.append({"title": title, "traffic": traffic, "picture": picture})
    return results


class Trends(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="trend", description="日本の現在の急上昇トレンドを取得します。")
    async def trend(self, interaction: discord.Interaction):
        await interaction.response.defer()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    RSS_URL,
                    headers={"User-Agent": "Mozilla/5.0 (compatible; DiscordBot)"},
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status != 200:
                        await interaction.followup.send(
                            f"トレンド情報の取得に失敗しました（HTTP {resp.status}）。"
                        )
                        return
                    xml_bytes = await resp.read()

            loop = asyncio.get_event_loop()
            trends = await loop.run_in_executor(None, _parse_rss, xml_bytes)

            if not trends:
                await interaction.followup.send("トレンド情報が取得できませんでした。")
                return

            # 上位10件
            trends = trends[:10]

            embed = discord.Embed(
                title="📈 現在の急上昇トレンド（日本）",
                color=discord.Color.blue()
            )

            # サムネイルは1位のトレンドの画像を使用
            if trends[0]["picture"]:
                embed.set_thumbnail(url=trends[0]["picture"])

            for i, t in enumerate(trends, 1):
                keyword = t["title"]
                traffic = t["traffic"]
                search_url = f"https://trends.google.co.jp/trending?q={quote(keyword)}&geo=JP"
                
                embed.add_field(
                    name=f"第{i}位: {keyword}",
                    value=f"🔍 {traffic} 検索\n[詳細を見る]({search_url})",
                    inline=False
                )

            embed.set_footer(text="Google Trends • データはリアルタイムで変動します")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            print(f"Error fetching trends: {e}")
            await interaction.followup.send(
                "トレンドの取得中にエラーが発生しました。時間をおいて再度お試しください。"
            )


async def setup(bot):
    await bot.add_cog(Trends(bot))

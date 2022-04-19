import os
import discord
import asyncpraw
from discord.ext import commands, tasks

ID = 'e6g259e7'
FEED_CHANNEL = 882052028388503582


class RedditCommands(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.reddit = asyncpraw.Reddit(
            user_agent='Phantom Bot (by u/PhantomFamily)',
            client_id=os.getenv('R_CLIENT'),
            client_secret=os.getenv('R_SECRET'),
            username=os.getenv('USERNAME'),
            password=os.getenv('COCPWD'))
        # self.scrape_subreddit.start()

    # @commands.command(name='e')
    async def test_ping(self, ctx):
        redditor = await self.reddit.redditor('PhantomFamily')
        await redditor.message("TEST", "test message from Async PRAW")
        return

    async def scrap_embed(self, ctx):
        channel = self.client.get_channel(FEED_CHANNEL)
        subreddit = await self.reddit.subreddit('ClashOfClansRecruit')
        bot_phrase = 'Please join our clan!'
        keywords = {
            'th14', 'th13', 'th12', 'th 14', 'th 13', 'th 12', 'townhall14',
            'townhall13', 'townhall12', 'townhall 14', 'townhall 13',
            'townhall 12'
        }
        async for submission in subreddit.stream.submissions():
            post = submission.title.lower()
            for i in keywords:
                if '[searching]' in post and i in post:
                    # submission.reply(bot_phrase)
                    break
        return

    async def scrape(self):
        channel = self.client.get_channel(FEED_CHANNEL)
        subreddit = await self.reddit.subreddit('ClashOfClansRecruit')
        async for submission in subreddit.stream.submissions():
            if submission.created_utc > self.client.start_time:
                e = discord.Embed(title=submission.title[:255],
                                  description=submission.selftext[:4000],
                                  color=0x3498db,
                                  url=submission.url)
                e.set_author(name='New post on /r/ClashOfClansRecruit',
                             url=submission.url)
                e.add_field(name='Post Author',
                            value=('/u/' + submission.author),
                            inline=True)
                e.add_field(name='Comments',
                            value=submission.num_comments,
                            inline=True)
                await channel.send(embed=e)

    #@tasks.loop()
    #async def scrape_subreddit(self):
    #await self.client.wait_until_ready()
    #await self.scrape()


def setup(client):
    client.add_cog(RedditCommands(client))

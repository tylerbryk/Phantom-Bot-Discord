import os
import coc
import time
import Server
import discord
from discord.ext import commands

extensions = [
    'LinkCommands', 'WarCommands', 'MiscCommands', 'CwlCommands',
    'RedditCommands', 'InfoCommands'
]

GUILD = 819709187239313428
EMOJI_GUILD = 803663172762337350

emoji_dict = dict(FIRE='870147325996204062',
                  STAR='870147326184923166',
                  SWRD='870147326147166259',
                  TH1='870138804319686677',
                  TH2='870139132201021540',
                  TH3='870139169781993522',
                  TH4='870139201226694756',
                  TH5='870139219132178452',
                  TH6='870139230968508426',
                  TH7='870139417862504499',
                  TH8='870139430810320896',
                  TH9='870139442411761754',
                  TH10='870139453946085487',
                  TH11='870139464549285889',
                  TH12='870139475945222154',
                  TH13='870139489908035594',
                  TH14='870139501064888320')


class PhantomBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='%', intents=discord.Intents.all())
        self.guild = GUILD
        self.emoji_guild = EMOJI_GUILD
        self.emoji_dict = emoji_dict
        self.start_time = time.time()
        self.coc = coc.login(os.getenv('EMAIL'),
                             os.getenv('COCPWD'),
                             client=coc.EventsClient)
        for ext in extensions:
            self.load_extension(ext)

    async def on_ready(self):
        print('Bot Online!')
        await self.change_presence(activity=discord.Game('Clash of Clans'))

    def run_bot(self):
        Server.start()
        super().run(os.getenv('TOKEN'))


if __name__ == '__main__':
    PhantomBot().run_bot()

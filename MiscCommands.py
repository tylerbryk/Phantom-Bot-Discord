import os
import pymysql
import discord
import pandas as pd
from datetime import datetime
from discord.ext import commands, tasks

# === Applicant Variables ===
message_id = 885994753680867378
dz_channel = 819709187822583813
dl_channel = 819709187822583816
wlc_channel = 819709187822583812
dz_role = '<@&819709187285975073>'
dl_role = '<@&819709187285975071>'
rc_role = '<@&819709187285975070>'
sr_rules = '<#819709187613392913>'
cl_rules = '<#819709187613392914>'
dz_emoji = 852634339844816966
dl_emoji = 858033764453580820
ga_emoji = 820103306604707860

# === on_member_join() -> Give this role ===
ga_role = 819709187285975075

# === Recruitment Variables ===
nr_red_ch_id = 675444353237516314
ph_red_ch_id = 819709189181800481
reminder_ch_id = 819709189181800480

# === Update/Export Roles ===
mem_id = 819709187302359052
clans = {
    'Danger Zone': 819709187302359059,
    'Downfall Legend': 858006003042746399
}
th = {
    14: 833162119477723136,
    13: 819709187239313436,
    12: 819709187239313435,
    11: 819709187239313434,
    10: 819709187239313433
}


class MiscCommands(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.reddit_reminder.start()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, ctx):
        await self.applicant_ping(ctx)

    @commands.Cog.listener()
    async def on_message(self, ctx):
        await self.forward_reddit(ctx)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = self.client.get_guild(self.client.guild)
        role = guild.get_role(ga_role)
        await member.add_roles(role)
        await self.applicant_ping_forced(member)

    @commands.command(name='clear')
    @commands.has_permissions(administrator=True)
    async def clear(self, ctx):
        return await ctx.channel.purge()

    @commands.command(name='clan-list')
    async def clan_list(self, ctx):
        await ctx.send(file=discord.File('banners/clan_list.png'))
        db, cursor = await self.connect_db()
        cursor.execute('SELECT tag, description FROM clans')
        results = cursor.fetchall()
        for r in results:
            clan = await self.client.coc.get_clan(r[0])
            e = discord.Embed(title=clan.name,
                              url=clan.share_link,
                              description=f'{r[1]}\n{clan.war_league.name}')
            e.set_thumbnail(url=clan.badge.url)
            await ctx.send(embed=e)

    @commands.command(name='export-mem')
    @commands.has_permissions(administrator=True)
    async def export_members(self, ctx):
        data = pd.DataFrame(columns=['Name', 'ID'])
        guild = self.client.get_guild(self.client.guild)
        role = guild.get_role(mem_id)
        for member in role.members:
            new = pd.DataFrame({'Name': [member.name], 'ID': [member.id]})
            data = pd.concat([data, new])
        data.to_csv('members.csv', index=False)
        return await ctx.send(file=discord.File('members.csv', filename='members.csv'))

    @commands.command(name='export-th')
    @commands.has_permissions(administrator=True)
    async def export_townhall(self, ctx):
        data = pd.DataFrame(columns=['TH', 'Name', 'ID'])
        guild = self.client.get_guild(self.client.guild)
        for role_id in th.items():
            role = guild.get_role(role_id[1])
            for member in role.members:
                new = pd.DataFrame({'TH': [role_id[0]], 'Name': [member.name], 'ID': [member.id]})
                data = pd.concat([data, new])
        data.to_csv('townhalls.csv', index=False)
        return await ctx.send(file=discord.File('townhalls.csv', filename='townhalls.csv'))

    @commands.command(name='export-clans')
    @commands.has_permissions(administrator=True)
    async def export_clans(self, ctx):
        data = pd.DataFrame(columns=['Clan', 'Name', 'ID'])
        guild = self.client.get_guild(self.client.guild)
        for role_id in clans.items():
            role = guild.get_role(role_id[1])
            for member in role.members:
                new = pd.DataFrame({'Clan': [role_id[0]], 'Name': [member.name], 'ID': [member.id]})
                data = pd.concat([data, new])
        data.to_csv('clans.csv', index=False)
        return await ctx.send(file=discord.File('clans.csv', filename='clans.csv'))

    @commands.command(name='update-th')
    @commands.has_permissions(administrator=True)
    async def update_townhall(self, ctx, *remove):
        msg = await ctx.send(embed=discord.Embed(title='Updating Townhall Roles!', color=0xf1c40f,
                                                 description='Hang tight, this operation may take a few minutes.'))
        db, cursor = await self.connect_db()
        guild = self.client.get_guild(self.client.guild)

        if remove:
            for role_id in th.items():
                role = guild.get_role(role_id[1])
                for member in role.members:
                    await member.remove_roles(role)

        cursor.execute('SELECT discord_id, townhall FROM linked_accounts')
        results = cursor.fetchall()
        failed = []
        for r in results:
            if r[1] >= 10:
                try:
                    user = guild.get_member(r[0])
                    role = guild.get_role(th[r[1]])
                    await user.add_roles(role)
                except Exception:
                    failed.append(r[0])
                    continue
        if failed:
            players = []
            for player in failed:
                cursor.execute('SELECT discord_name FROM linked_accounts WHERE discord_id = "{}"'.format(player))
                result = cursor.fetchall()
                players.append(result[0])
            return await msg.edit(embed=discord.Embed(title='Townhall Roles Updates!', color=0x287e29,
                                                      description='Role assignment failed on:\n{}'
                                                      .format('\n'.join(players))))
        return await msg.edit(embed=discord.Embed(title='Townhall Roles Updates!', color=0x287e29))

    async def applicant_ping(self, ctx):
        if ctx.message_id != message_id:
            return

        message = '{} is applying for **{}**\n\nPlease do the following:\n1. Read {} and {}\n2. Send a screenshot of your base and profile\n3. Send your player tag (Ex: #5GC47AE)\n\nA {} will be online to assist you shortly!'

        if ctx.emoji.id == dz_emoji:
            channel = self.client.get_channel(dz_channel)
            await channel.send(message.format(ctx.member.mention,
                                              'Danger Zone', sr_rules, cl_rules, dz_role))
        elif ctx.emoji.id == dl_emoji:
            channel = self.client.get_channel(dl_channel)
            await channel.send(message.format(ctx.member.mention,
                                              'Gear Savana', sr_rules, cl_rules, dl_role))
        elif ctx.emoji.id == ga_emoji:
            channel = self.client.get_channel(wlc_channel)
            await channel.send(
                '{} is a **General Applicant**\n\nPlease do the following:\n1. Read {}\n2. Send a screenshot of your base and profile\n3. Send your player tag (Ex: #5GC47AE)\n\nA {} will be online to assist you shortly!'.format(
                    ctx.member.mention, sr_rules, rc_role))
        else:
            channel = self.client.get_channel(wlc_channel)
            await channel.send(
                '{} reacted with an invalid option!\nPlease visit {} and select a clan application type!'.format(
                    ctx.member.mention, sr_rules))

    async def applicant_ping_forced(self, member):
        channel = self.client.get_channel(wlc_channel)
        await channel.send(
            '{} is a **General Applicant**\n\nPlease do the following:\n1. Read {}\n2. Send a screenshot of your base and profile\n3. Send your player tag (Ex: #5GC47AE)\n\nA {} will be online to assist you shortly!'.format(
                member.mention, sr_rules, rc_role))

    async def forward_reddit(self, ctx):
        if ctx.channel.id != nr_red_ch_id or not ctx.embeds:
            return
        channel = self.client.get_channel(ph_red_ch_id)
        for embed in ctx.embeds:
            await channel.send(embed=embed)
        return

    @tasks.loop(minutes=1)
    async def reddit_reminder(self):
        if datetime.now().hour == 19 and datetime.now().minute == 0:  # 3pm
            day = datetime.today().weekday()
            db, cursor = await self.connect_db()
            cursor.execute('SELECT * FROM recruitment_reminders WHERE day = "{}"'.format(day))
            result = cursor.fetchall()
            channel = self.client.get_channel(reminder_ch_id)
            if not result:
                return await channel.send('**No Recruitment Reminders Today**')
            rc = self.client.get_user(result[0][3])
            return await channel.send(
                '**Recruitment Post Reminder**\nPlease post for {} {}'.format(result[0][1], rc.mention))

    @staticmethod
    async def connect_db():
        db = pymysql.connect(
            host=os.getenv('HOST'),
            user=os.getenv('USER'),
            password=os.getenv('COCPWD'),
            database=os.getenv('USER'))
        return db, db.cursor()


def setup(client):
    client.add_cog(MiscCommands(client))

import os
import csv
import time

import coc
import pymysql
import discord
from discord.ext import commands, tasks


class LinkCommands(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.background_db_update.start()

    @commands.command(name='link')
    async def add_link(self, ctx, arg1, arg2):
        db, cursor = await self.connect_db()
        if '#' in arg1:
            tag = arg1
            raw_user = arg2
        else:
            tag = arg2
            raw_user = arg1

        # Is tag already in DB?
        cursor.execute('SELECT * FROM linked_accounts WHERE player_tag = "{}"'.format(tag))
        result = cursor.fetchall()
        if result:
            ign, tag, name = result[0][3], result[0][2], result[0][1]
            return await ctx.send(embed=discord.Embed(title='Already Linked!',
                                                      description='{} ({}) is linked to {}'.format(ign, tag, name),
                                                      color=0xbf0000))
        # Lookup Discord ID
        try:
            user = await self.find_user(ctx, raw_user)
            if user is None:
                return await ctx.send('The provided Discord user could not be located in this server!')
        except ValueError:
            return await ctx.send(
                'The provided Discord user ID is invalid! Please ensure that the ID is entered in the form of @12345.')
        except Exception:
            return await ctx.send('An error occurred while looking up the provided ID, please contact leadership.')

        # Get Clash Player Tag info
        try:
            player_name, player_th, player_clan = await self.query_tag(tag)
        except TypeError:
            return await ctx.send(
                'The provided player tag is invalid! Please ensure that the player tag is entered in the form of #ABC123.')
        except Exception:
            return await ctx.send(
                'The COC API failed to retrieve the provided player tag. This could be due to high demand on the COC API server. Please try again later or contact leadership.')

        # INSERT into SQL DB
        try:
            sql = 'INSERT INTO linked_accounts VALUES (%s, %s, %s, %s, %s, %s)'
            val = (
                user.id, '{}#{}'.format(user.name, user.discriminator), tag, player_name, player_th, str(player_clan))
            cursor.execute(sql, val)
            db.commit()
        except Exception:
            return await ctx.send('An error occurred while appending to the database, please contact leadership.')

        # Job Complete
        return await ctx.send(embed=discord.Embed(title='Account Linked!',
                                                  description='{} ({}) is linked to {}#{}'.format(player_name, tag,
                                                                                                  user.name,
                                                                                                  user.discriminator),
                                                  color=0x287e29))

    @commands.command(name='get')
    async def get_link(self, ctx, arg):
        db, cursor = await self.connect_db()
        if '#' in arg:
            if not coc.utils.is_valid_tag(arg):
                return await ctx.send('The provided player tag is invalid!')
            cursor.execute('SELECT * FROM linked_accounts WHERE player_tag = "{}"'.format(arg))
            result = cursor.fetchall()
            if not result:
                return await ctx.send(embed=discord.Embed(title='Not Linked!',
                                                          description='Please use %link to link an account, or try %help for more info.',
                                                          color=0xbf0000))
            cursor.execute('SELECT * FROM linked_accounts WHERE discord_id = "{}"'.format(result[0][0]))
            result = cursor.fetchall()
        else:
            try:
                user = await self.find_user(ctx, arg)
                if user is None:
                    return await ctx.send('The provided Discord user could not be located in this server!')
            except Exception:
                return await ctx.send(
                    'The provided input is invalid! Please ensure that either a valid COC player tag or discord user ID are entered.')
            cursor.execute('SELECT * FROM linked_accounts WHERE discord_id = "{}"'.format(user.id))
            result = cursor.fetchall()
            if not result:
                return await ctx.send(embed=discord.Embed(title='No Accounts Found!',
                                                          description='Please use %link to link an account, or try %help for more info.',
                                                          color=0xbf0000))
        account_list = ''
        for row in result:
            th, ign, tag, name = row[4], row[3], row[2], row[1]
            account_list += '{} ({}) - TH{}\n'.format(ign, tag, th)
        return await ctx.send(
            embed=discord.Embed(title='{}\'s Account(s)'.format(name), description=account_list, color=0x287e29))

    @commands.command(name='scan')
    async def scan_clan(self, ctx, abv):
        db, cursor = await self.connect_db()
        cursor.execute('SELECT * FROM clans WHERE abv = "{}"'.format(abv))
        result = cursor.fetchall()
        if not result:
            return await ctx.send(
                'Invalid input! Please enter the two-letter abbreviation for the desired clan. (DZ, GC, etc.)')
        msg = await ctx.send(embed=discord.Embed(title='Scanning...', description='ETA: 10 seconds', color=0xf1c40f))
        clan = await self.client.coc.get_clan(result[0][2])
        accounts = []
        async for player in clan.get_detailed_members():
            cursor.execute('SELECT * FROM linked_accounts WHERE player_tag = "{}"'.format(player.tag))
            result = cursor.fetchall()
            if not result:
                accounts.append('{} - {}'.format(player.tag, player.name))
        if not accounts:
            return await msg.edit(embed=discord.Embed(title='All Accounts Linked!', color=0x287e29))
        return await msg.edit(embed=discord.Embed(title='Unlinked Accounts in {}:'.format(clan.name),
                                                  description='{}'.format('\n'.join(accounts)),
                                                  color=0xf1c40f))

    @commands.command(name='update')
    async def force_update(self, ctx):
        t0 = time.time()
        msg = await ctx.send(
            embed=discord.Embed(title='Updating Database...', description='ETA: 60 seconds', color=0xf1c40f))
        await self.update_db(ctx)
        t1 = time.time()
        return await msg.edit(embed=discord.Embed(title='Update Complete!',
                                                  description='Elapsed Time: {:.1f} seconds'.format(t1 - t0),
                                                  color=0x287e29))

    @commands.command(name='export')
    async def export_db(self, ctx):
        db, cursor = await self.connect_db()
        cursor.execute('SELECT * FROM linked_accounts ORDER BY discord_name ASC, townhall DESC')
        result = cursor.fetchall()
        with open('db.csv', 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile, lineterminator='\n')
            csv_writer.writerow(['id', 'disc_name', 'tag', 'name', 'th', 'clan'])
            csv_writer.writerows(result)
        return await ctx.send(file=discord.File('db.csv', filename='linked_accounts.csv'))

    @commands.command(name='length', aliases=['len'])
    async def db_len(self, ctx):
        db, cursor = await self.connect_db()
        cursor.execute('SELECT COUNT(*) FROM linked_accounts')
        return await ctx.send('{} Linked Accounts'.format(cursor.fetchall()[0][0]))

    @commands.command(name='clean')
    async def clean_db(self, ctx):
        guild = self.client.get_guild(self.client.guild)
        mem_id = [member.id for member in guild.members]
        db, cursor = await self.connect_db()
        cursor.execute('SELECT * FROM linked_accounts')
        result = cursor.fetchall()
        purge = [row[1] for row in result if row[0] not in mem_id]
        if not purge:
            return await ctx.send(embed=discord.Embed(title='No Purgeable Players!', color=0x287e29))
        return await ctx.send(embed=discord.Embed(title='Purgeable Players:',
                                                  description='{}'.format('\n'.join(purge)),
                                                  color=0xf1c40f))

    @staticmethod
    async def connect_db():
        db = pymysql.connect(
            host=os.getenv('HOST'),
            user=os.getenv('USER'),
            password=os.getenv('COCPWD'),
            database=os.getenv('USER'))
        return db, db.cursor()

    @staticmethod
    async def find_user(ctx, raw_user):
        user_id = raw_user.translate({ord(i): None for i in '<@>'})
        user_id = user_id.translate({ord(i): None for i in '!'})
        user_id = user_id.translate({ord(i): None for i in '\\'})
        return ctx.guild.get_member(int(user_id))

    async def query_tag(self, tag):
        if not coc.utils.is_valid_tag(tag):
            return TypeError
        player = await self.client.coc.get_player(tag)
        return player.name, player.town_hall, player.clan

    async def update_db(self, ctx=None):
        guild = self.client.get_guild(self.client.guild)
        db, cursor = await self.connect_db()
        cursor.execute('SELECT * FROM linked_accounts')
        result = cursor.fetchall()
        for row in result:
            name, th, clan = await self.query_tag(row[2])
            if ctx is not None:
                user = guild.get_member(int(row[0]))
                if user is None:
                    continue
                sql = 'UPDATE linked_accounts ' \
                      'SET discord_name = "{}#{}", player_name = "{}", townhall = "{}", clan = "{}" ' \
                      'WHERE player_tag = "{}"'.format(user.name, user.discriminator, name, th, clan, row[2])
                cursor.execute(sql)
            else:
                sql = 'UPDATE linked_accounts ' \
                      'SET player_name = "{}", townhall = "{}", clan = "{}" ' \
                      'WHERE player_tag = "{}"'.format(name, th, clan, row[2])
                cursor.execute(sql)
            db.commit()
        return

    @tasks.loop(minutes=3)
    async def background_db_update(self):
        await self.update_db()

    @background_db_update.before_loop
    async def before_background_db_update(self):
        await self.client.wait_until_ready()


def setup(client):
    client.add_cog(LinkCommands(client))

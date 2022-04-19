import os
import time
from datetime import datetime

import pymysql
import discord
from discord.ext import commands, tasks


class WarCommands(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.war_updates.start()

    @commands.command(name='war')
    async def war(self, ctx, abv, *no_ping):
        tag = abv
        if '#' not in abv:
            db, cursor = await self.connect_db()
            cursor.execute('SELECT * FROM clans WHERE abv = "{}"'.format(abv))
            result = cursor.fetchall()
            if not result:
                return await ctx.send(
                    'Invalid input! Please enter the two-letter abbreviation for the desired clan. (DZ, GC, etc.)')
            tag = result[0][2]
        war = await self.client.coc.get_current_war(tag)
        guild = self.client.get_guild(self.client.emoji_guild)
        em = {name: (await guild.fetch_emoji(id)) for name, id in self.client.emoji_dict.items()}
        gmt = datetime.fromtimestamp(time.mktime(time.gmtime()))
        d = '**War Against**\n{} ({})\n\n'.format(war.opponent.name, war.opponent.tag)
        if war.state == 'preparation':
            t = await self.format_time((war.start_time.time - gmt).total_seconds())
            d += '**War State**\nPreparation ({} vs {})\nStarts in {}\n\n'.format(war.team_size, war.team_size, t)
        elif war.state == 'inWar':
            t = await self.format_time((war.end_time.time - gmt).total_seconds())
            d += '**War State**\nBattle Day ({} vs {})\nEnds in {}\n\n'.format(war.team_size, war.team_size, t)
        elif war.state == 'warEnded':
            t = await self.format_time((gmt - war.end_time.time).total_seconds())
            d += '**War State**\nWar Ended ({} vs {})\nEnded {} ago\n\n'.format(war.team_size, war.team_size, t)
        else:
            clan = await self.client.coc.get_clan(tag)
            return await ctx.send(embed=discord.Embed(title='{} is not in war!'.format(clan.name), color=0xbf0000,
                                                      description='The clan may be searching for a war currently or has not had any recent war activity.'))
        if war.state == 'inWar' or war.state == 'warEnded':
            attacks = await self.get_attack_info(war)
            size = war.team_size
            if not war.is_cwl:
                size *= 2
            d += '**Stats**\n'
            d += f'`{attacks["h_star"]:>8}`\t{em["STAR"]}\t`{attacks["e_star"]:<8}`\n'
            d += f'`{str(attacks["h_dest"])+"%":>8}`\t{em["FIRE"]}\t`{str(attacks["e_dest"])+"%":<8}`\n'
            d += f'`{str(attacks["h_hits"])+"/"+str(size):>8}`\t{em["SWRD"]}\t`{str(attacks["e_hits"])+"/"+str(size):8}`\n\n'
        home, away = await self.get_th_composition(war)
        d += '**Composition**\n{}\n'.format(war.clan.name)
        for th, amt in home.items():
            d += f'{em[th]} {amt} {" ":3}'
        d += '\n\n\n{}\n'.format(war.opponent.name)
        for th, amt in away.items():
            d += f'{em[th]} {amt} {" ":3}'
        ping_only = None
        if war.state == 'inWar':
            home_attacks = await self.get_home_attacks(war, tag)
            player_tags = await self.get_home_players(war, tag)
            remain_hits = await self.attacks_remaining(home_attacks, player_tags, cwl=war.is_cwl)
            full_ping, ping_only = await self.tag_to_name(remain_hits)
            if full_ping:
                d += '\n\n\n**Remaining Attacks**\n{}'.format('\n'.join(full_ping))
        e = discord.Embed(description=d, color=0x3498db)
        e.set_author(name='{} ({})'.format(war.clan.name, war.clan.tag), icon_url=war.clan.badge.small)
        await ctx.send(embed=e)
        if ping_only and not no_ping:
            await ctx.send(' '.join(ping_only))
        return

    @staticmethod
    async def get_th_composition(war):
        home, away = {}, {}
        for member in war.members:
            if member.clan.name == war.clan.name:
                if 'TH' + str(member.town_hall) not in home:
                    home['TH' + str(member.town_hall)] = 1
                else:
                    home['TH' + str(member.town_hall)] += 1
            else:
                if 'TH' + str(member.town_hall) not in away:
                    away['TH' + str(member.town_hall)] = 1
                else:
                    away['TH' + str(member.town_hall)] += 1
        return home, away

    @staticmethod
    async def get_attack_info(war):
        info = dict(
            h_star=0, e_star=0,
            h_dest=0, e_dest=0,
            h_hits=0, e_hits=0)
        attacks = dict()
        for attack in war.attacks:
            if attack.defender_tag not in attacks:
                attacks[attack.defender_tag] = [attack.stars, attack.destruction, attack.attacker]
            else:
                star = attacks[attack.defender_tag][0]
                dest = attacks[attack.defender_tag][1]
                if star < attack.stars:
                    attacks[attack.defender_tag][0] = attack.stars
                if dest < attack.destruction:
                    attacks[attack.defender_tag][1] = attack.destruction
            if attack.attacker.is_opponent:
                info['e_hits'] += 1
            else:
                info['h_hits'] += 1
        for tag, items in attacks.items():
            if items[2].is_opponent:
                info['e_star'] += items[0]
                info['e_dest'] += items[1]
            else:
                info['h_star'] += items[0]
                info['h_dest'] += items[1]
        info['h_dest'] = round((info['h_dest'] / war.team_size), 2)
        info['e_dest'] = round((info['e_dest'] / war.team_size), 2)
        return info

    @staticmethod
    async def get_home_attacks(war, tag):
        home_attack_tags = {}
        for attack in war.attacks:
            if attack.attacker.clan.tag == tag:
                player_tag = attack.attacker.tag
                if player_tag in home_attack_tags:
                    home_attack_tags[player_tag] += 1
                else:
                    home_attack_tags[player_tag] = 1
        return home_attack_tags

    @staticmethod
    async def get_home_players(war, tag):
        home_players = []
        for member in war.members:
            if member.clan.tag == tag:
                home_players.append(member.tag)
        return home_players

    @staticmethod
    async def attacks_remaining(home_attacks, player_tags, cwl):
        remaining = []
        for tag in player_tags:
            if tag not in home_attacks:
                remaining.append(tag)
            else:
                if cwl is False and home_attacks[tag] == 1:
                    remaining.append(tag)
        return remaining

    @staticmethod
    async def connect_db():
        db = pymysql.connect(
            host=os.getenv('HOST'),
            user=os.getenv('USER'),
            password=os.getenv('COCPWD'),
            database=os.getenv('USER'))
        return db, db.cursor()

    async def tag_to_name(self, tags):
        db, cursor = await self.connect_db()
        guild = self.client.get_guild(self.client.guild)
        full, ping = [], []
        for tag in tags:
            cursor.execute('SELECT * FROM linked_accounts WHERE player_tag = "{}"'.format(tag))
            result = cursor.fetchall()
            if result is None:
                player = await self.client.coc.get_player(tag)
                full.append(player.name)
                continue
            try:
                user = guild.get_member(result[0][0])
            except Exception:
                continue
            full.append('{} - {}'.format(result[0][3], user.mention))
            ping.append(user.mention)
        return full, ping

    @staticmethod
    async def format_time(total_seconds):
        result = []
        intervals = (
            ('w', 604800),
            ('d', 86400),
            ('h', 3600),
            ('m', 60),
        )
        for name, count in intervals:
            value = total_seconds // count
            if value:
                total_seconds -= value * count
                if value == 1:
                    name = name.rstrip('s')
                result.append(f'{int(value)}{name}')
        return ' '.join(result[:2])

    @tasks.loop(minutes=1)
    async def war_updates(self):
        db, cursor = await self.connect_db()
        cursor.execute('SELECT tag, cwl_channel_id FROM clans')
        tags = cursor.fetchall()
        gmt = datetime.fromtimestamp(time.mktime(time.gmtime()))
        for tag in tags:
            war = await self.client.coc.get_current_war(tag[0])
            if war.state == 'inWar':
                t = (war.end_time.time - gmt).total_seconds()
                if (43200 < t < 43260) or (21600 < t < 21660) or (10800 < t < 10860) or (3600 < t < 3660):
                    channel = self.client.get_channel(tag[1])
                    await self.war(channel, tag[0])

    @war_updates.before_loop
    async def before_war_updates(self):
        await self.client.wait_until_ready()


def setup(client):
    client.add_cog(WarCommands(client))

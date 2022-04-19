import discord
from discord.ext import commands


server_rules_text = '''1)** __Nickname__**
> • Your Discord nickname must represent your clash of clans in-game account name(s).

2)** __No Toxicity__**
> • This includes and is not limited to, homophobia, racism, sexism, and intentionally being harmful to others.

3)** __No BST__**
> • No buying, selling, or trading of accounts.

4)** __No Drama__**
> • No starting or escalating drama.
> • If you have a problem, deal with it privately.
> • If you need help dealing with anything related to this, bring it to leadership.

5) **__No Political Conversations__**
> • Everyone is entitled to their political opinions, but clash of clans is not the place to talk about them.

6)** __CWL__**
> • Participants must register via the form sent at the end of each month.
> • Players must be understanding that they may be relocated for CWL.
> • This allows players to be in the best league based on their skill level.
> • Heroes must be up for CWL, no exceptions.
> • Participants will vote on who earns bonuses for each clan.


<:DZ:966110287835037736> **DANGER ZONE**
> • Main clan in the Phantom family
> • TH13+ (TH14, or near max TH13)
> • Currently ranked Champion League I
> • Competitive and helpful environment
> • Read <#819709187613392914> for more info
> • FC’s will be required upon entry for new applicants

<:GS:966110287646306304> **★GEAR SAVANA★**
> • Secondary clan in the Phantom family
> • TH11+ (No rushed accounts!)
> • Currently ranked in Crystal League
> • Relaxed but helpful environment
> • Read <#819709187613392914> for more info
> • FC’s may be required upon entry for new applicants

⬆️ **SCROLL UP!** ⬆️
'''

# =============================================================================================================

clan_rules_text = '''<:DZ:966110287835037736>  **__DANGER ZONE  Requirements:__**
> • TH14 - BK75, AQ75, GW50, RC25
> • TH13 - BK65, AQ65, GW45, RC15
> • Base at least 90% max from previous Town Hall

<:GS:966110287646306304>  **__★GEAR SAVANA★  Requirements:__**
> • TH13 - BK65, AQ65, GW40, RC10
> • TH12 - BK60, AQ60, GW35
> • TH11 - BK35, AQ35, GW10
> • Base at least 80% max from previous Town Hall

**__Clan Games:__**
> • Clan Games are **mandatory**
> • 1000 point minimum

**__Donations:__**
> • Donate as much as possible, there is no minimum or requirement
> • Make an effort to fill pending donation requests before requesting yourself
> • Having little or no donations at the end of the season may result in a demotion

**__War Rules:__**
> • Opt in/out using the clan war preference button on your profile
> • If you are opted in (green) then you will be put in the next war
> • All heroes **must be up** for war, pets are **not** required
> • Above rule only applies to Danger Zone
> • First hour is used to scout and claim bases of the **same** town hall
> • Claim a base by using the red flag, do **not** use the mail note to claim
> • Try for the highest ranked base that you are confident in tripling
> • If a claimed base has not been hit after the first 16 hours, it is fair game
> • Both attacks are **mandatory** and should be done by the 23-hour mark

**__CWL Rules:__**
> • All heroes **must be up** during CWL week
> • Register via the form sent out at the end of each month
> • You will be assigned to one of the clans in our family
> • Clan selection is based on war hits, war defenses, and friendly challenges
> • Each clan may have a few extra players, in which case rotations may occur
> • Before attacking in CWL, you are **required** to submit a plan on Discord
> • **Do not attack in the first hour**, this time should be used to scout & claim a base
> • Failure to comply with any of our rules will result in being rotated out, minimum 1 day

⬆️ **SCROLL UP!** ⬆️
'''

# =============================================================================================================

roles_text = '''**Management:**
> <@&819709187323199511>
> <@&819709187315466268>

**Leadership:**
> <@&819709187315466264>
> <@&819709187315466267>
> <@&819709187315466265>

**Legendary Roles:**
> <@&819709187315466263>
> <@&819709187315466261>
> <@&819709187315466262>

**Main Clans:**
> <@&819709187302359059>
> <@&858006003042746399>

**Ranks:**
> <@&819709187302359053>
> <@&819709187302359052>

**Competitive Team:**
> <@&945893167352381440>

**Helper Roles:**
> <@&819709187268411410>
> <@&819709187302359050>
> <@&819709187302359051>

**Family Friends:**
> <@&819709187285975079>
> <@&820169532207005696>
> <@&820171267146514432>

**Recruiter Roles:**
> <@&819709187285975070>
> <@&819709187285975073>
> <@&819709187285975071>

**CWL Clan Roles:**
> <@&819709187268411409>
> <@&858032092519596042>
> <@&819793045318139905>
> <@&819709187268411408>
> <@&819793325125009438>
> <@&819793579495915531>
> <@&819709187268411406>
> <@&819709187268411405>
> <@&837775900463726662>
> <@&849075141560631307>

**Townhall Roles:**
> <@&833162119477723136>
> <@&819709187239313436>
> <@&819709187239313435>
> <@&819709187239313434>
> <@&819709187239313433>

**Applicant Roles:**
> <@&819709187285975075>
> <@&819709187285975078>
> <@&819709187285975076>
'''

# =============================================================================================================

horde_text = '''Phantom Family's competitive squad for tournaments, leagues, and events!

The team comprises of only max TH13’s from the family who are seeking a more competitive way of playing the game. 

The team has competed in Warriors Champions League (WCL), Blitzkreig, Clash Masters League (CML), and Universal War league (UWL), to name a few.

If you are interested in joining, want more information, or just want to check out the server, then click the link below! 
https://discord.gg/d3E8wkM'''


class InfoCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name='info-rules-serv')
    @commands.has_permissions(administrator=True)
    async def send_server_rules(self, ctx):
        await ctx.send(file=discord.File('banners/server_rules.png'))
        await ctx.send(server_rules_text)

    @commands.command(name='info-rules-clan')
    @commands.has_permissions(administrator=True)
    async def send_clan_rules(self, ctx):
        await ctx.send(file=discord.File('banners/clan_rules.png'))
        await ctx.send(clan_rules_text)

    @commands.command(name='info-roles')
    @commands.has_permissions(administrator=True)
    async def send_role_info(self, ctx):
        await ctx.send(file=discord.File('banners/role_info.png'))
        await ctx.send(roles_text)


def setup(client):
    client.add_cog(InfoCommands(client))

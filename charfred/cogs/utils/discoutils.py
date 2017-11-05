#!/usr/bin/env python

import discord
from discord.ext import commands
import random
import functools
import logging
from ..configs import keywords

log = logging.getLogger('charfred')


def has_permission(cmd):
    def predicate(ctx):
        if not isinstance(ctx.channel, discord.abc.GuildChannel):
            return False
        names = ctx.bot.cfg['commands'][cmd]
        getter = functools.partial(discord.utils.get, ctx.author.roles)
        return any(getter(name=name) is not None for name in names)
    return commands.check(predicate)


def is_cmdChannel(ctx):
    if ctx.channel.id in ctx.bot.cfg['commandCh'].values():
        return True
    return False


def _is_cmdChannel():
    async def predicate(ctx):
        return is_cmdChannel(ctx)
    return commands.check(predicate)


def get_cmdCh(ctx):
    cmdChID = ctx.bot.cfg['commandCh'][ctx.guild.id]
    return ctx.bot.get_channel(cmdChID)


async def sendReply(ctx, msg):
    if is_cmdChannel(ctx):
        await ctx.send(f'{random.choice(keywords.replies)}\n{msg}')
    else:
        await get_cmdCh(ctx).send(f'{random.choice(keywords.replies)}\n{msg}')
        await ctx.send(
            f'{random.choice(keywords.deposits)}\n{get_cmdCh(ctx).mention}',
            delete_after=30
        )


async def sendReply_codeblocked(ctx, msg, encoding=None):
    if encoding is None:
        mesg = f'\n```Markdown\n{msg}\n```'
    else:
        mesg = f'\n```{encoding}\n{msg}\n```'
    if is_cmdChannel(ctx):
        await ctx.send(
            f'{random.choice(keywords.replies)}' +
            mesg
        )
    else:
        await get_cmdCh(ctx).send(
            f'{random.choice(keywords.replies)}' +
            mesg
        )
        await ctx.send(
            f'{random.choice(keywords.deposits)}\n{get_cmdCh(ctx).mention}',
            delete_after=30
        )


async def sendEmbed(ctx, emb):
    if is_cmdChannel(ctx):
        await ctx.send(
            f'{random.choice(keywords.replies)}',
            embed=emb
        )
    else:
        await get_cmdCh(ctx).send(
            f'{random.choice(keywords.replies)}',
            embed=emb
        )
        await ctx.send(
            f'{random.choice(keywords.deposits)}\n{get_cmdCh(ctx).mention}',
            delete_after=30
        )

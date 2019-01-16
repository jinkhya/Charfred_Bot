import logging
import pprint
import os
import asyncio
from collections import namedtuple
from discord.errors import Forbidden, NotFound
from discord.ext import commands
from utils.discoutils import sendMarkdown
from utils.sizeddict import SizedDict

log = logging.getLogger('charfred')

Command = namedtuple('Command', 'msg output')


class CommandHistorian:
    def __init__(self, bot):
        self.bot = bot
        self.botCfg = bot.cfg
        self.dir = bot.dir
        self.loop = bot.loop
        self.lock = asyncio.Lock()
        self.pprinter = pprint.PrettyPrinter()
        self.cmd_map = SizedDict()
        self.logcmds = False
        if not hasattr(bot, 'cmd_map'):
            bot.cmd_map = self.cmd_map

    def _writelog(self, ctx):
        logname = f'{self.dir}/logs/commandlogs/{ctx.message.author.id}.log'
        if os.path.exists(logname):
            openmode = 'a'
        else:
            openmode = 'w'
            os.makedirs(os.path.dirname(logname), exist_ok=True)
            log.info(f'Created potentially missing dirs for {id}.log!')
        with open(logname, openmode) as cmdlog:
            cmdlog.write(f'cmd failed: {ctx.command_failed}; msg: \"{ctx.message.content}\"')

    async def _log(self, ctx):
        with await self.lock:
            await self.loop.run_in_executor(None, self._writelog, ctx)

    async def on_command(self, ctx):
        """Saves message attached to command context to the command map,
        and optionally logs command user\'s command history file.
        """

        self.cmd_map[ctx.message.id] = Command(
            msg=ctx.message,
            output=[]
        )
        if self.logcmds:
            await self._log(ctx)

    async def on_message_delete(self, message):
        """Deletes command output if original invokation
        message is deleted.

        Will only work if the command is still in the
        cmd_map and hasn\'t expired yet!
        """

        if message.id in self.cmd_map:
            log.info('Deleting previous command output!')
            try:
                await message.channel.delete_messages(self.cmd_map[message.id].output)
            except KeyError:
                log.error('Deletion of previous command output failed!')
            except Forbidden:
                log.error('No Permission!')
            except NotFound:
                log.warning('Some messages not found for deletion!')
            else:
                del self.cmd_map[message.id]

    async def on_message_edit(self, before, after):
        """Reinvokes a command if it has been edited,
        and deletes previous command output.

        Will only work if the command is still in the
        cmd_map and hasn\'t expired yet!
        """

        if before.content == after.content:
            return

        if before.id in self.cmd_map:
            log.info('Deleting previous command output!')
            try:
                await before.channel.delete_messages(self.cmd_map[before.id].output)
            except KeyError:
                log.error('Deletion of previous command output failed!')
            except Forbidden:
                log.error('No Permission!')
            except NotFound:
                log.warning('Some messages not found for deletion!')
            else:
                log.info(f'Reinvoking: {before.content} -> {after.content}')
                await self.bot.on_message(after)
                del self.cmd_map[before.id]

    @commands.group(hidden=True, invoke_without_command=True)
    @commands.is_owner()
    async def cmdlogging(self, ctx):
        """Command logging commands.

        Returns whether logging is currently enabled or not,
        if no subcommand is given.
        """

        log.info('Logging is currently ' + 'active!' if self.logcmds else 'inactive!')
        await sendMarkdown(ctx, '# Logging is currently ' + 'active!' if self.logcmds else 'inactive!')

    @cmdlogging.command(hidden=True)
    @commands.is_owner()
    async def toggle(self, ctx):
        """Toggles command logging on and off."""

        log.info('Toggled command logging ' + 'off!' if self.logcmds else 'on!')
        await sendMarkdown(ctx, '# Toggled command logging ' + 'off!' if self.logcmds else 'on!')

    @commands.group(invoke_without_command=True, hidden=True)
    @commands.is_owner()
    async def cmdmap(self, ctx):
        """Command Map commands.

        This returns a crude list of the current command map state,
        if no subcommand was given.
        """

        log.info('Showing cmd_map.')
        rep = self.pprinter.pformat(self.cmd_map)
        await sendMarkdown(ctx, rep)

    @cmdmap.command(hidden=True)
    @commands.is_owner()
    async def clear(self, ctx, max_size: int=100):
        """Clears the current command map.

        Optionally takes a number for the maximum
        size of the command map.
        """

        if max_size > 1:
            log.info(f'Clearing cmd_map, setting maximum size to: {max_size}.')
            self.cmd_map.clear()
            self.cmd_map.max_size = max_size
            await sendMarkdown(ctx, 'Command map cleared, new maximum size set '
                               f'to {max_size}!')
        else:
            log.warning('cmd_map clear with insufficient max_size!')
            await sendMarkdown(ctx, '< Insufficient maximum size, you can\'t '
                               'even store a single command in there! >')

    @commands.group(aliases=['cmdhistory'], invoke_without_command=True)
    async def history(self, ctx):
        """Command-history commands."""

        pass


def setup(bot):
    bot.add_cog(CommandHistorian(bot))

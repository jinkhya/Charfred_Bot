from discord.ext import commands
import re
import json
import logging as log
from ..utils.config import Config
from ..utils.discoutils import has_permission, sendReply_codeblocked, valid_server, sendReply
from ..utils.miscutils import isUp, sendCmd


class customs:
    def __init__(self, bot):
        self.bot = bot
        self.servercfg = bot.servercfg
        self.servercmds = Config(
            f'{self.bot.dir}/customCmds.json',
            loop=self.bot.loop,
            load=True
        )

    @commands.group(hidden=True, invoke_without_command=True)
    @has_permission('custom')
    async def custom(self, ctx):
        pass

    @custom.group(hidden=True, aliases=['console', 'cc'])
    @has_permission('consolecmd')
    async def consolecmd(self, ctx):
        if ctx.invoked_subcommand is None and ctx.subcommand_passed is not None:
            if ctx.subcommand_passed in self.servercmds and len(ctx.args) >= 2:
                log.info(f'Invoking custom command: \"{ctx.args[0]}\".')
                ctx.invoke(
                    self.run, ctx.subcommand_passed, ctx.args[1], ctx.args[2:]
                )

    @consolecmd.command(hidden=True, aliases=['edit', 'modify'])
    async def add(self, ctx, name: str, *cmds: str):
        self.servercmds[name] = cmds
        log.info(f'Added \"{cmds}\" to your custom console commands library.')
        await sendReply(ctx, f'Added \"{cmds}\" to your custom console commands library.')
        await self.servercmds.save()

    @consolecmd.command(hidden=True, aliases=['delete'])
    async def remove(self, ctx, name: str):
        del self.servercmds[name]
        log.info(f'Removed \"{name}\" from your custom console commands library.')
        await sendReply(ctx, f'Removed \"{name}\" from your custom console commands library.')
        await self.servercmds.save()

    @consolecmd.command(hidden=True, name='list')
    async def _list(self, ctx):
        msg = ['Custom Console Commands Library',
               '===============================']
        msg.append(json.dumps(self.servercmds))
        await sendReply_codeblocked(ctx, msg, encoding='json')

    @consolecmd.command(hidden=True, aliases=['execute', 'exec'])
    @valid_server()
    async def run(self, ctx, cmd: str, server: str, *args: str):
        msg = ['Command Log', '===========']
        if cmd not in self.servercmds:
            log.warning(f'\"{cmd}\" is undefined!')
            msg.append(f'[Error]: \"{cmd}\" is undefined!')
            return
        if re.match('all$', server, flags=re.I):
            for server in self.servercfg['servers']:
                if isUp(server):
                    log.info(f'Executing \"{cmd}\" on {server}.')
                    for _cmd in self.servercmds[cmd]:
                        if args:
                            await sendCmd(self.loop, server, _cmd.format(*args))
                        else:
                            await sendCmd(self.loop, server, _cmd)
                    msg.append(f'[Info] Executed \"{cmd}\" on {server}.')
                else:
                    log.warning(f'Could not execute \"{cmd}\", {server} is offline!')
                    msg.append(f'[Error]: Unable to execute \"{cmd}\", {server}, is offline!')
        else:
            if isUp(server):
                log.info(f'Executing \"{cmd}\" on {server}.')
                for _cmd in self.servercmds[cmd]:
                    if args:
                        await sendCmd(self.loop, server, _cmd.format(*args))
                    else:
                        await sendCmd(self.loop, server, _cmd)
                msg.append(f'[Info] Executed \"{cmd}\" on {server}.')
            else:
                log.warning(f'Could not execute \"{cmd}\", {server} is offline!')
                msg.append(f'[Error]: Unable to execute \"{cmd}\", {server}, is offline!')
        await sendReply_codeblocked(ctx, '\n'.join(msg))


def setup(bot):
    bot.add_cog(customs(bot))

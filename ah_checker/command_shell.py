import asynccmd as cmd
import logging
import asyncio
import readline

class ChipShell(cmd.Cmd):
    def __init__(self, client, target_channel, *args, **kwargs):
        self.prompt = kwargs.pop("prompt", "$> ")
        super().__init__(*args, **kwargs)
        self.client = client
        self.target_channel = target_channel
        self.loop = None

    def do_say(self, arg):
        self.loop.create_task(self.say_message(arg))
        
    async def say_message(self, message, chanid=None):
        chanid = chanid or self.target_channel
        await self.client.get_channel(chanid).send(message)
        
    def do_listtasks(self, arg):
        for task in asyncio.Task.all_tasks(loop=self.loop):
            print(task)

    def start(self, loop=None):
        self.loop = loop
        super().cmdloop(loop)

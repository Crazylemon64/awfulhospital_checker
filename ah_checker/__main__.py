from bs4 import BeautifulSoup
import discord
from discord import utils
import asyncio
import aiohttp
import async_timeout
import logging
import os
import configparser
import re
import xdg
import contextlib
from collections import OrderedDict
    
def minutes_to_seconds(minutes):
    return minutes * 60

APP_DIRNAME = 'ah_checker'
AH_URL = "http://www.bogleech.com/awfulhospital/index.html"
CHECK_DELAY = minutes_to_seconds(15)
NOISYTENANTS_GUILDID = 0
NOISYTENANTS_CHANNELID = 0

META_REGEX = re.compile(r'0; url=http://www.bogleech.com/awfulhospital/(?P<comicID>\d+).html')

async def fetch(session, url):
    with async_timeout.timeout(10):
        async with session.get(url) as response:
            return await response.text()

async def getPanelID():
    async with aiohttp.ClientSession() as session:
        logger = logging.getLogger(__name__)
        html = await fetch(session, AH_URL)
        soup = BeautifulSoup(html, 'html.parser')
        logger.debug("Meta's content: '{}'".format(soup.meta['content']))
        m = META_REGEX.search(soup.meta['content'])
        return int(m.group("comicID"))
    
async def countPanelDialogs(new_url):
    async with aiohttp.ClientSession() as session:
        logger = logging.getLogger(__name__)
        html = await fetch(session, new_url)
        soup = BeautifulSoup(html, 'html.parser')
        dialog_count = len(soup.find_all(class_="dialog"))
        logger.debug("Dialog count: '{}'".format(dialog_count))
        return dialog_count

def config_path():
    if 'APPDATA' in os.environ:
        APP_CONFIG_PATH = os.path.join(os.environ['APPDATA'], APP_DIRNAME)
    else:
        APP_CONFIG_PATH = os.path.join(xdg.XDG_CONFIG_HOME, APP_DIRNAME)
    
    if not os.path.exists(APP_CONFIG_PATH):
        try:
            os.makedirs(APP_CONFIG_PATH)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
    return APP_CONFIG_PATH

def panelIDToURL(panel_id):
    return "http://www.bogleech.com/awfulhospital/{}.html".format(panel_id)

def main():
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "WARNING"))
    logging.getLogger(__name__).setLevel(logging.INFO)
    logger = logging.getLogger(__name__)
    bot_token = "x"
    config = configparser.ConfigParser()
    config['DEFAULT'] = OrderedDict([
        ('noisytenants_guildid', '00000000000000000'),
        ('noisytenants_chanid', '00000000000000000'),
        ('bot_token', 'x'),
        ])
    
    APP_CONFIG_PATH = config_path()
    cfilepath = os.path.join(APP_CONFIG_PATH, "config.ini")
    try:
        with open(cfilepath, "r") as cf:
            config.read_file(cf)
    except FileNotFoundError:
        with open(cfilepath, "w") as cf:
            config.write(cf)
    
    bot_token = config['DEFAULT']['bot_token']
    NOISYTENANTS_GUILDID = int(config['DEFAULT']['noisytenants_guildid'])
    NOISYTENANTS_CHANID = int(config['DEFAULT']['noisytenants_chanid'])
        
    async def fillInitialPanelInfo():
        current_panel_id = await getPanelID()
        current_dialog_count = await countPanelDialogs(panelIDToURL(current_panel_id))
        logger = logging.getLogger(__name__)
        logger.info("Initial panel ID: {}".format(current_panel_id))
        logger.info("Initial dialog count: {}".format(current_dialog_count))
        while True:
            await asyncio.sleep(CHECK_DELAY)
            current_panel_id, current_dialog_count = await comparePanelIds(current_panel_id, current_dialog_count)
            
    async def announceNewPanel(new_url):
        # Post update announcement to the channel
        noisytenant_guild = cli.get_guild(NOISYTENANTS_GUILDID)
        comic_update_role = utils.find(lambda x: x.name == "comic update", noisytenant_guild.roles)
        comic_update_message = "{} Awful Hospital updated!\n{}".format(comic_update_role.mention, new_url)
        logger.info("Would send message: '{}'".format(comic_update_message))
        await cli.get_channel(NOISYTENANTS_CHANID).send(comic_update_message)
        
    async def comparePanelIds(current_panel_id, current_dialog_count):
        logger = logging.getLogger(__name__)
        logger.info("Checking {}...".format(AH_URL))
        new_panel_id = await getPanelID()
        new_dialog_count = await countPanelDialogs(panelIDToURL(new_panel_id))
        if new_panel_id != current_panel_id:
            logger.info("New panel ID: {}->{}".format(current_panel_id, new_panel_id))
            logger.info("New panel dialog count: {}".format(new_dialog_count))
            await announceNewPanel(panelIDToURL(new_panel_id))
        elif new_dialog_count != current_dialog_count:
            logger.info("New dialog count: {}->{}".format(current_dialog_count, new_dialog_count))
            await announceNewPanel(panelIDToURL(curren_panel_id))
        return new_panel_id, new_dialog_count
        
    loop = asyncio.get_event_loop()
    loop.create_task(fillInitialPanelInfo())
    
    cli = discord.Client(loop=loop)
    try:
        loop.run_until_complete(cli.start(bot_token))
    except KeyboardInterrupt:
        loop.run_until_complete(cli.logout())
        for task in asyncio.Task.all_tasks():
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                loop.run_until_complete(task)
        loop.run_until_complete(loop.shutdown_asyncgens())
    finally:
        loop.close()

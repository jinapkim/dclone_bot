import discord
from discord.ext import tasks, commands
import os
from dotenv import load_dotenv
import requests


load_dotenv()

API_TOKEN = os.environ.get('API_TOKEN')
API_BASE_URL = os.environ.get('API_BASE_URL')
CHANNEL_ID = int(os.environ.get('CHANNEL_ID'))

REGION_NAMES = {'Americas': '1', 'Europe': '2', 'Asia': '3'}
LADDER_NAMES = {'Ladder': '1', 'Non-Ladder': '2'}
HC_NAMES = {'Hardcore': '1', 'Softcore': '2'}

REGION_NUMS = {'1': 'Americas', '2': 'Europe', '3': 'Asia'}
LADDER_NUMS = {'1': 'Ladder', '2': 'Non-Ladder'}
HC_NUMS = {'1': 'Hardcore', '2': 'Softcore'}


class DClone(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.current_progress = {
            ('1', '1', '1'): None,  # Americas, Ladder, Hardcore
            ('1', '1', '2'): None,  # Americas, Ladder, Softcore
            ('1', '2', '1'): None,  # Americas, Non-Ladder, Hardcore
            ('1', '2', '2'): None,  # Americas, Non-Ladder, Softcore
            ('2', '1', '1'): None,  # Europe, Ladder, Hardcore
            ('2', '1', '2'): None,  # Europe, Ladder, Softcore
            ('2', '2', '1'): None,  # Europe, Non-Ladder, Hardcore
            ('2', '2', '2'): None,  # Europe, Non-Ladder, Softcore
            ('3', '1', '1'): None,  # Asia, Ladder, Hardcore
            ('3', '1', '2'): None,  # Asia, Ladder, Softcore
            ('3', '2', '1'): None,  # Asia, Non-Ladder, Hardcore
            ('3', '2', '2'): None  # Asia, Non-Ladder, Softcore
        }

    async def on_ready(self):
        """
        This function runs when the Discord bot is ready and will initiate the
        repeating task of querying the DClone API every 60 seconds.
        :return: none
        """

        self.update_progress.start()

    @tasks.loop(seconds=60)
    async def update_progress(self):
        """
        Queries the progress database that tracks the Diablo Clone every 60 seconds.
        Query parameters include region, ladder, and hc.
        :return: a JSON object with the query results
        """

        # Data courtesy of  diablo2.io (https://diablo2.io/dclonetracker.php)

        headers = {'User-Agent': 'DiabloTrackerDiscordBot'}
        response = requests.get(API_BASE_URL, headers=headers)
        if response.status_code == 200:
            result = response.json()

        else:
            return

        # Update current progress
        send_update = False
        for item in result:
            key = (item['region'], item['ladder'], item['hc'])

            if self.current_progress[key] != item['progress']:
                self.current_progress[key] = item['progress']

            # If progress has changed and is now above 2, send notification to channel
            if self.current_progress[key] != item['progress'] and int(item['progress']) > 2:
                send_update = True

        if send_update:
            await self.auto_status_update()
        else:
            return

    async def auto_status_update(self):
        """
        Sends a message to the channel with the currently saved dclone progress
        :return: none
        """
        print('auto running')
        # Construct message
        message = 'Current DClone Progress:\n\n'

        for k,v in self.current_progress.items():
            progress = v
            region_num, ladder_num, hc_num = k

            region = REGION_NUMS[region_num]
            ladder = LADDER_NUMS[ladder_num]
            hc = HC_NUMS[hc_num]

            message += f'-- Progress:{progress}/6   {region}   {ladder}   {hc}\n\n'

        channel = self.get_channel(CHANNEL_ID)
        await channel.send(message)

intents = discord.Intents.default()
intents.message_content = True
bot = DClone('/', intents)


@bot.command()
async def dclone(ctx, *args):
    """
    Sends a message to the channel with progress status
    :param ctx: context of the command
    :param progress: DcloneProgress instance containing the current saved dclone progress
    :return: none
    """

    keywords = args
    region, ladder, hc = None, None, None

    for word in keywords:
        if word == 'Americas':
            region = REGION_NAMES['Americas']
        if word == 'Europe':
            region = REGION_NAMES['Europe']
        if word == 'Asia':
            region = REGION_NAMES['Asia']

        if word == 'Ladder':
            ladder = LADDER_NAMES['Ladder']
        if word == 'Non-Ladder':
            ladder = LADDER_NAMES['Non-Ladder']

        if word == 'Hardcore':
            hc = HC_NAMES['Hardcore']
        if word == 'Softcore':
            hc = HC_NAMES['Softcore']

    # Make request to get current progress
    headers = {'User-Agent': 'DiabloTrackerDiscordBot'}
    params = {
        'region': region,
        'ladder': ladder,
        'hc': hc
    }

    filters = {k: v for k, v in params.items() if v is not None}

    # Data courtesy of  diablo2.io (https://diablo2.io/dclonetracker.php)
    response = requests.get(API_BASE_URL, headers=headers, params=params)
    if response.status_code == 200:
        result = response.json()

    else:
        ctx.send('Unable to retrieve data at this time.')
        return

    # Construct message
    message = 'Current DClone Progress:\n\n'
    for item in result:
        progress = item['progress']
        region = REGION_NUMS[item['region']]
        ladder = LADDER_NUMS[item['ladder']]
        hc = HC_NUMS[item['hc']]

        message += f'-- Progress:{progress}/6   {region}   {ladder}   {hc}\n\n'

    await ctx.send(message)

bot.run(API_TOKEN)

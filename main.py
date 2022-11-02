from typing import List
from zoneinfo import ZoneInfo

import aiohttp
import discord
from discord import app_commands, Embed, Color, Interaction
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from os import getenv

load_dotenv()
token = getenv("TOKEN")

intents = discord.Intents.default()
intents.members = True

target_departments = {
            "TEST": {
                "id": 994427431228289034,
                "enabled": True,
                "message": Embed(
                    color=Color.blue(),
                ).add_field(
                    name="Test Recruiting",
                    value="A Message of Testing"
                )
            }
        }


class Client(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.synced = False
        self.session = aiohttp.ClientSession()

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync()
            self.synced = True
        self.schedule().start()

    async def send_recruitment_messages(self):
        for dept in target_departments.values():
            if dept['enabled']:
                message_channel = client.get_channel(dept['id'])
                await message_channel.send(embed=dept["message"])

    def schedule(self):
        job_defaults = {
            "coalesce": False,
            "max_instances": 5,
            "misfire_grace_time": 15,
            "replace_existing": True,
        }

        scheduler = AsyncIOScheduler(job_defaults)
        scheduler.configure(timezone=ZoneInfo('America/Los_Angeles'))
        scheduler.add_job(self.send_recruitment_messages, CronTrigger.from_crontab("0 15 * * *"))

        return scheduler


client = Client()
tree = app_commands.CommandTree(client)


@tree.command(
    name="toggle_dept_recruitment",
    description="Toggles specific department recruiting message"
)
async def toggle_dept_recruitment(interaction: Interaction, dept: str, toggle: bool):
    department = dept.upper()
    global target_departments
    dept_toggle = target_departments[department]['enabled']

    if dept_toggle == toggle:
        await interaction.response.send_message(f"Department toggle is already {toggle}")
    else:
        target_departments[department]['enabled'] = toggle
        if toggle:
            await interaction.response.send_message(f"{dept} recruitment message has been enabled")
        else:
            await interaction.response.send_message(f"{dept} recruitment message has been disabled")


@toggle_dept_recruitment.autocomplete('dept')
async def command_dept_autocomplete(interaction: Interaction, current: str) -> List[app_commands.Choice[str]]:
    departments = []
    for department in target_departments:
        departments.append(department)
    return [
        app_commands.Choice(name=dept, value=dept)
        for dept in departments if current.lower() in dept.lower()
    ]

client.run(token)

"""
discord_bot.py

A module containing the DiscordBot class that represents a Discord bot.

Dependencies:
- Requires asyncio to run the Discord bot asynchronously.
- Requires discord to interact with the Discord API.
- Requires db_handler to interact with the database.
- Requires env_var_loader to load environment variables.
"""

import sys
import asyncio
import discord

from db_handler import DbHandler
from command_factory import CommandFactory
from env_var_loader import get_env_var_value

class DiscordBot:
    """
    A class that represents a Discord bot.
    The bot can send messages, react to commands, and interact with the database.

    Main Functions:
    - run: Starts the Discord bot.
    - logout: Logs out the Discord bot.
    - wait_until_ready: Waits until the bot is ready.
    - on_ready: An event handler for when the Discord bot is succesfully logged in.
    - on_message: An event handler for when there is a message sent in the Discord channel.
    - send_message: Sends a message via the Discord bot to a specified channel.

    Attributes:
    - token (string): The Discord bot token.
    - text_channel_id (int): The Discord channel ID.
    - client (discord.Client): The Discord client.
    """
    def __init__(self) -> None:

        # Getting environment variables
        self.token = get_env_var_value("DISCORD_BOT_TOKEN")

        # Discord API needs the CHANNEL_ID in form of an integer, not string
        try:
            self.text_channel_id = int(get_env_var_value("TEST_CHANNEL_ID"))
        except (TypeError, ValueError):
            print("Invalid DISCORD_CHANNEL_ID. Must be an integer.")
            sys.exit(1)

        # Declaring Intents for the Discord Client
        self.intents = discord.Intents.default()
        self.intents.message_content = True

        # Initialize the Discord client
        self.client = discord.Client(intents=self.intents)

        # Setup database connection
        self.db = DbHandler()

        # Command factory to create commands
        self.command_factory = CommandFactory(self.db)

        # Event to signal when the bot is ready
        self.ready_event = asyncio.Event()

        # Register event handlers
        self.client.event(self.on_ready)
        self.client.event(self.on_message)

    async def run(self) -> None:
        """
        The main starting point of the Discord bot.
        Creates a new event loop and starts a Discord client which takes control of the event loop,
        meaning listening to events from Discord servers.

        Returns:
            None
        """
        await self.client.start(self.token)

    async def logout(self) -> None:
        """
        Closing the currently opened Discord client, meaning the Discord bot logging off. 

        Returns:
            None
        """
        print("Shutting down Discord bot...")
        await self.client.close()

    async def wait_until_ready(self) -> None:
        """
        Waits until the bot is ready.

        Returns:
            None
        """
        await self.ready_event.wait()

    async def on_ready(self) -> None:
        """
        An event handler for when the Discord bot is succesfully
        logged in and ready to receive commands.
        
        Only announces that the bot is ready in the console.

        Returns:
            None
        """
        print(f"We have logged in as {self.client.user}")
        self.ready_event.set()

    async def on_message(self, message: discord.Message) -> None:
        """
        An event handler for when there is a message sent in the Discord
        channel where the bot is connected in.
        The bot ignores its own messages and reacts to specific commands starting
        with symbol "!" like "!games", "!mygames" etc.

        Returns:
            None
        """
        # Ensure the bot doesn't respond to itself
        if message.author == self.client.user:
            return
        
        print(f"Received message: {message.content}")
        # Check if the message is a command
        if message.content.startswith("!"):
            try:
                command = self.command_factory.get_command(message.content)
                if command is not None:
                    print("Command received:", message.content)
                    await command.execute(message)
                else:
                    await message.channel.send("Unknown command. Type `!help` for a list of commands.")
            except Exception as e:
                print(f"An error occurred: {e}")
                await message.channel.send("An error occurred while executing the command.")

    async def send_message(
            self,
            message: discord.Message,
            channel_id = None
        ) -> int:
        """
        Sends a message via the Discord bot to a specified channel.

        Parameters:
            message (string): The message to be sent.
            discord_channel_id (int, optional): The channel where the message will be sent.
                Defaults to None.

        Returns:
            int: Discord ID of the sent message.
        """
        if channel_id is None:
            channel_id = self.text_channel_id

        message = await self.client.get_channel(channel_id).send(message)
        print(f"Message sent: {message.content}")
        return message.id

    async def get_reaction_users(self, message_id: int, channel_id = None) -> list[str]:
        """
        Retrieves a list of users that put any reaction on the specific message in Discord chat.

        Parameters:
            message_id (int): The message's Discord ID.
            discord_channel_id (int, optional): The channel where the message is located.
                Defaults to DISCORD_CHANNEL_ID.

        Returns:
            List: A list of users that had at least one reaction on the message with message_id.
        """
        if channel_id is None:
            channel_id = self.text_channel_id

        channel = self.client.get_channel(channel_id)
        message = await channel.fetch_message(message_id)

        # Use a set to store unique user names
        users = set()

        for reaction in message.reactions:
            reaction_users = [user.name async for user in reaction.users()]
            users.update(reaction_users)

        return list(users)

async def main() -> None:
    """
    The main entry point of the script.

    Only used for testing this module.

    Returns:
        None 
    """
    # Create a new Discord bot
    bot = DiscordBot()

    # Start the Discord bot in the background
    await bot.run()

    # Wait for the bot to be ready
    await bot.wait_until_ready()
    print(f"Status: {bot.client.status}")

    # Testing
    await bot.send_message("Just Testing")

    # On terminating the code
    # await bot.logout()

if __name__ == '__main__':
    asyncio.run(main())

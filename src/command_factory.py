"""
command_factory.py

A module containing the CommandFactory class that creates command objects
based on the message content.

Dependencies:
- Requires the commands module to get the command classes.
"""

import commands
from db_handler import DbHandler

class CommandFactory:
    """
    A class that returns command objects based on the message content.

    Main Functions:
    - get_command: Returns the appropriate command class based on the message content.

    Attributes:
    - commands (list): A list of all command classes.
    """
    def __init__(self, db: DbHandler) -> None:
        self.commands: list[commands.Command] = [
            commands.ListGamesCommand("!games", "List all games in the server.", db),
            commands.AddGameCommand("!addgame", "Add a game to the server's game list.", db),
            commands.RemoveGameCommand("!removegame", "Remove a game from the server's game list.", db),
            commands.MyGamesCommand("!mygames", "List all games of the user.", db),
            commands.AddUserGameCommand("!add", "Add a game to the user's game list.", db),
            commands.RemoveUserGameCommand("!remove", "Remove a game from the user's game list.", db),
        ]
        self.commands.append(commands.HelpCommand("!help", "List all available commands.", self.commands))

    def get_command(self, message_content: str) -> commands.Command | None:
        """
        Returns the appropriate command class based on the message content.

        Parameters:
            message_content (str): The content of the message.

        Returns:
            Command: The command class that matches the message
        """
        possible_commands: list[commands.Command] = []

        # List all possible commands
        for command in self.commands:
            if message_content.startswith(command.name):
                possible_commands.append(command)

        # Return the command with the longest match
        max_len = 0
        matched_command = None

        for command in possible_commands:
            if len(command.name) > max_len:
                max_len = len(command.name)
                matched_command = command

        return matched_command

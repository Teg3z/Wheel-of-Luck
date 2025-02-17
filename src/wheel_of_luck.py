"""
wheel_of_luck.py

The main module.

Manages the application's UI, starts the corresponding Discord bot and sends it commands.
Maintains the wheel spinning logic and sends results into a MongoDB database.

Main Functions:
- remove_unwated_games:
    Hides every game in the wheels UI that isn't mentioned in the `common_games` parameter.
- choose_winning_game:
    Randomly chooses one game out of a list of Game objects based on their desire percentage.
- spin_wheel:
    The whole wheel spinning logic is in this function.
- send_message_to_discord:
    Sends a new coroutine to the thread that the Discord bot is running on,
    telling the bot to send a message on Discord.
- main:
    The main entry point of the application.

Dependencies:
- Requires asyncio to manage the event loop, so that the application can wait for coroutines,
    like waiting for Discord bot to send a message.
- Requires PySimpleGUI for the application's simple UI.
- Requires discord_bot to send commands to the Discord bot.
- Requires db_handler for all the databe operations and establishment.
"""

import sys
import random
import asyncio
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMenuBar, QMenu, QLineEdit, QFrame
)
from PyQt6.QtCore import Qt, QTimer

from discord_bot import DiscordBot
from db_handler import DbHandler
from bot_thread import BotThread
from utils import load_config, save_config

# Colors
bg_color = "Black"
fg_color = "White"
btn_color = "Green"
btn_mouseover_color = "DarkGreen"
btn_size = (7, 0)

# Fonts
font = ("Arial", 18)

# def remove_unwated_games(
#         game_ui_texts: list[sg.Text],
#         games: list[str],
#         window: sg.Window,
#         common_games: list[str]
#     ) -> tuple[list[sg.Text], list[str]]:
#     """
#     Hides every game in the wheels UI that isn't mentioned in the `common_games` parameter.

#     Parameters:
#         games_ui_texts (sg.Text): UI texts of all the game names.
#         games (list[Game]): A list of all games represented by Game objects.
#         window (sg.Window): The main UI window of the application.
#         common_games (list[string]): A list of game names that the players have in common.

#     Returns:
#         list[sg.Text]:
#             Contains all UI texts of games that will be visible during the spin.
#         list[Game]:
#             Contains all the Game objects with the game names that the players have in common.
#     """
#     wanted_game_ui_texts = []
#     wanted_games = []

#     for index, game_ui_text in enumerate(game_ui_texts):
#         if game_ui_text.key in common_games:
#             window[game_ui_text.key].Update(visible = True)
#             wanted_game_ui_texts.append(game_ui_text)
#             # The lists games and game_ui_texts are in the same order, so indexing works
#             wanted_games.append(games[index])
#         else:
#             window[game_ui_text.key].Update(visible = False)

#     window.refresh()
#     return wanted_game_ui_texts, wanted_games

# def change_last_spin_insertion_visibility(window: sg.Window, db: DbHandler, visible: bool):
#     """
#     Handles visibility of the corresponding UI elements taking care of last spin
#     insertion into the DB. 

#     Parameters:
#         window (sg.Window):
#             The main UI window of the application.
#         db (pymongo.mongo_client.MongoClient):
#             An instance of a MongoClient connected to the specified database.
#         visible (bool):
#             Indicates whether the UI elements should be hidden/shown .

#     Returns:
#         None
#     """
#     window["W"].Update(visible=visible)
#     window["L"].Update(visible=visible)
#     window["LAST_GAME"].Update(visible=visible)
#     if visible:
#         window["LAST_GAME"].Update(value=db.get_last_spin_string())

#     window.refresh()

# async def main_old() -> None:
#     last_game_result_ui = None
#     last_game_result = None
#     is_last_spin_inserted = None
#     # UI texts
#     last_game_result_ui = sg.Text(
#         f"\nLast game result? \n({last_game_result})",
#         text_color=fg_color,
#         background_color=bg_color,
#         font=font,
#         key="LAST_GAME",
#         visible= not is_last_spin_inserted
#     )
#     result_ui = sg.Text("", text_color=fg_color, background_color=bg_color, font=font)
#     win_lose_msg = sg.Text("", text_color=fg_color, background_color=bg_color, font=font)

#     # Buttons
#     win = sg.Button(
#         "W",
#         button_color=btn_color,
#         font=font,
#         mouseover_colors=btn_mouseover_color,
#         size=btn_size,
#         visible=not is_last_spin_inserted
#     )
#     lose = sg.Button(
#         "L",
#         button_color=btn_color,
#         font=font,
#         mouseover_colors=btn_mouseover_color,
#         size=btn_size,
#         visible=not is_last_spin_inserted
#     )
#     send_reaction_message_button = sg.Button(
#         "SEND REACTION",
#         button_color=btn_color,
#         font=font,
#         mouseover_colors=btn_mouseover_color,
#         size=btn_size
#     )

#     # Layout creation
#     layout = [
#         [last_game_result_ui],
#         [win, lose],
#         [win_lose_msg]
#     ]

#     # Initiate variables
#     rolled_game = None
#     message_id = None

    # # Pressing W/L buttons condition
    # if event == "W":
    #     win_lose_msg.update("\nYOU ARE THE BEST")
    #     db.insert_log_into_database(event)
    #     change_last_spin_insertion_visibility(main_window, db, visible=False)
    #     continue
    # if event == "L":
    #     win_lose_msg.update("\nYOU SUCK")
    #     db.insert_log_into_database(event)
    #     change_last_spin_insertion_visibility(main_window, db, visible=False)
    #     continue
    # if event == "SEND REACTION":
    #     rolled_game = None
    #     message_id = await bot.send_message("Let's spin the wheel of luck! Who's in?")
    #     continue
    # if event == "PLAY REACTION":
    #     # Check that there is a message already sent in the DC chat
    #     if message_id is None:
    #         print("You have to send a reaction message first.")
    #         continue
    #     players = await bot.get_reaction_users(message_id)

    #     # No reaction case
    #     if not players:
    #         await bot.send_message("Nobody wants to participate :(")
    #         continue

    #     # Get list of games that those players have in common
    #     is_first_player = True
    #     for player in players:
    #         # Inicialize the list of common games by the first player
    #         if is_first_player:
    #             common_games = db.get_list_of_user_games(player)
    #             is_first_player = False
    #             continue
    #         # Get current players list of games
    #         player_games = db.get_list_of_user_games(player)
    #         # Keep only the games that are still in the common_games list
    #         # and also in the current players list
    #         updated_games_list = []
    #         for game in common_games:
    #             if game in player_games:
    #                 updated_games_list.append(game)
    #         common_games = updated_games_list

    #     # Wheel setup and spinning
    #     wanted_game_ui_texts, wanted_games = remove_unwated_games(
    #         games_ui_texts,
    #         games,
    #         main_window,
    #         common_games
    #     )
    #     rolled_game = await spin_wheel(
    #         wanted_game_ui_texts,
    #         wanted_games,
    #         main_window,
    #         result_ui
    #     )
    #     db.update_last_spin(rolled_game.Get(), players=players)
    #     # Show insertion
    #     change_last_spin_insertion_visibility(main_window, db, True)
    #     continue

class MainWindow(QMainWindow):
    def __init__(self, db: DbHandler, bot: DiscordBot) -> None:
        super().__init__()

        self.db = db
        self.bot = bot
        self.games = []
        self.rolled_game = None
        self.previous_index = None
        self.current_index = 0
        self.timer = QTimer()
        self.spin_speed = 10
        self.slowdown_factor = 15

        self.setWindowTitle("Wheel of Luck")
        self.setGeometry(100, 100, 600, 400)

        # Create the main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Create menu bar with Settings option
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)
        menu = QMenu("&Menu", self)
        menu_bar.addMenu(menu)
        settings_action = menu.addAction("Settings")
        settings_action.triggered.connect(self.open_settings)

        # Create UI elements
        self.games_frame = QFrame()
        self.games_layout = QVBoxLayout(self.games_frame)

        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.spin_button = QPushButton("Spin")
        self.spin_button.clicked.connect(self.start_spin_wheel)

        self.button_layout = QHBoxLayout()
        self.announce_button = QPushButton("Announce")
        self.announce_button.clicked.connect(self.announce_game)

        self.button_layout.addWidget(self.spin_button)
        self.button_layout.addWidget(self.announce_button)

        # Add elements to the main layout
        self.main_layout.addWidget(menu_bar)
        self.main_layout.addWidget(self.games_frame)
        self.main_layout.addWidget(self.result_label)
        self.main_layout.addLayout(self.button_layout)

        # Load initial games
        self.update_games_list()

    def update_games_list(self):
        """ Updates the games list dynamically based on database. """
        for i in reversed(range(self.games_layout.count())):
            item = self.games_layout.itemAt(i)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if self.db.is_connected:
            self.games = self.db.get_list_of_games()
            for game in self.games:
                game_label = QLabel(game)
                self.games_layout.addWidget(game_label)
        else:
            self.games_layout.addWidget(QLabel("Please connect to the database."))

    def start_spin_wheel(self):
        """ Starts the spinning animation. """
        if not self.games:
            self.result_label.setText("No games available!")
            return

        # Whiten all games
        for i in range(self.games_layout.count()):
            label: QLabel = self.games_layout.itemAt(i).widget()
            label.setStyleSheet("color: white;")

        self.rolled_game = random.choice(self.games)
        self.previous_index = None
        self.current_index = 0
        self.spin_speed = 10
        self.timer.timeout.connect(self.spin_step)
        self.timer.start(self.spin_speed)

    def spin_step(self):
        """ Spins the wheel by highlighting one game at a time. """
        if not self.games_layout:
            return

        # Reset previous selection to white
        if self.previous_index is not None:
            curr_game_label: QLabel = self.games_layout.itemAt(self.previous_index).widget()
            curr_game_label.setStyleSheet("color: white;")

        # Highlight the current game in green
        curr_game_label = self.games_layout.itemAt(self.current_index).widget()
        curr_game_label.setStyleSheet("color: lime;")

        # Move to the next game (circular loop)
        self.previous_index = self.current_index
        self.current_index = (self.current_index + 1) % self.games_layout.count()

        # Stop spinning and announce the winner
        if self.spin_speed > 300 and curr_game_label.text() == self.rolled_game:
            self.timer.stop()
            self.timer.timeout.disconnect()
            self.result_label.setText(f"🎉 Enjoy {self.rolled_game}!")
        # Continue spinning
        else:
            self.spin_speed = self.spin_speed + self.slowdown_factor
            self.timer.start(self.spin_speed)

    def announce_game(self):
        """ Announces the rolled game via the Discord bot. """
        if self.rolled_game:
            asyncio.run_coroutine_threadsafe(
                self.bot.send_message(
                    f"Going to play {self.rolled_game}, anyone wanna join in?"
                ),
                self.bot.client.loop
            )

    def open_settings(self):
        """ Opens the settings window. """
        self.settings_window = SettingsWindow(self)
        self.settings_window.show()

class SettingsWindow(QWidget):
    def __init__(self, main_window: MainWindow) -> None:
        super().__init__()

        self.main_window = main_window
        self.setWindowTitle("Settings")
        self.setGeometry(200, 200, 300, 200)

        layout = QVBoxLayout(self)

        self.dc_token_input = QLineEdit(load_config().get("DISCORD_BOT_TOKEN", ""))
        self.channel_id_input = QLineEdit(load_config().get("CHANNEL_ID", ""))
        self.db_connection_input = QLineEdit(load_config().get("DB_CONNECTION_STRING", ""))

        layout.addWidget(QLabel("Discord Bot Token:"))
        layout.addWidget(self.dc_token_input)
        layout.addWidget(QLabel("Channel ID:"))
        layout.addWidget(self.channel_id_input)
        layout.addWidget(QLabel("Database Connection String:"))
        layout.addWidget(self.db_connection_input)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

    def save_settings(self):
        """ Saves settings and updates the database connection. """
        config = {
            "DISCORD_BOT_TOKEN": self.dc_token_input.text(),
            "CHANNEL_ID": self.channel_id_input.text(),
            "DB_CONNECTION_STRING": self.db_connection_input.text()
        }
        save_config(config)

        # Reinitialize the database connection
        # TODO dont reinitialize if db havent changed
        self.main_window.db.__init__()
        self.main_window.update_games_list()

        self.close()

async def main():
    """ Runs the PyQt application. """
    app = QApplication(sys.argv)

    # Establish database connection
    db = DbHandler()

    # Create a new Discord bot
    bot = DiscordBot()

    # Start Discord bot in a separate thread
    bot_thread = BotThread(bot)
    bot_thread.start()

    # Wait for the bot to be ready
    # await bot.wait_until_ready()

    main_window = MainWindow(db, bot)
    main_window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    # Create an event loop for the main function
    asyncio.run(main())
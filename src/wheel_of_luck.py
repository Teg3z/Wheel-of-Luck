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
from PyQt6.QtCore import Qt, QTimer, QEvent

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

class MainWindow(QMainWindow):
    def __init__(
            self,
            db: DbHandler,
            bot: DiscordBot,
            bot_thread: BotThread
        ) -> None:
        super().__init__()

        self.db = db
        self.bot = bot
        self.bot_thread = bot_thread
        self.games = []
        self.game_labels: dict[str, QLabel] = {}
        self.visible_games: list[str] = []
        self.last_players: list[str] = []
        self.ask_message_id = None
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

        self.result_lbl = QLabel("")
        self.result_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.ask_btn = QPushButton("Ask")
        self.ask_btn.clicked.connect(self.ask)

        self.spin_btn = QPushButton("Spin")
        self.spin_btn.clicked.connect(self.start_spin_wheel)

        self.announce_btn = QPushButton("Announce")
        self.announce_btn.clicked.connect(self.announce_game)

        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.ask_btn)
        self.button_layout.addWidget(self.spin_btn)
        self.button_layout.addWidget(self.announce_btn)

        # --- Last spin panel ---
        self.last_spin_lbl = QLabel("")
        self.last_spin_lbl.setStyleSheet("color: white;")
        self.last_spin_lbl.setVisible(True)

        self.win_btn = QPushButton("W")
        self.lose_btn = QPushButton("L")
        self.win_btn.setVisible(False)
        self.lose_btn.setVisible(False)

        self.win_lose_msg = QLabel("")
        self.win_lose_msg.setStyleSheet("color: white;")
        self.win_lose_msg.setVisible(False)

        self.win_btn.clicked.connect(lambda: self.on_spin_outcome("W"))
        self.lose_btn.clicked.connect(lambda: self.on_spin_outcome("L"))

        self.win_lose_button_layout = QHBoxLayout()
        self.win_lose_button_layout.addWidget(self.win_btn)
        self.win_lose_button_layout.addWidget(self.lose_btn)

        # Add elements to the main layout
        self.main_layout.addWidget(menu_bar)
        self.main_layout.addWidget(self.games_frame)
        self.main_layout.addWidget(self.result_lbl)
        self.main_layout.addWidget(self.last_spin_lbl)
        self.main_layout.addWidget(self.win_lose_msg)
        self.main_layout.addLayout(self.button_layout)
        self.main_layout.addLayout(self.win_lose_button_layout)

        # Load initial games
        self.update_games_list()

        self.set_last_spin_visibility(True)

    def update_games_list(self):
        """ Updates the games list dynamically based on database. """
        for i in reversed(range(self.games_layout.count())):
            item = self.games_layout.itemAt(i)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.game_labels.clear()
        self.visible_games.clear()

        if self.db.is_connected:
            self.games = self.db.get_list_of_games()
            for game in self.games:
                game_label = QLabel(game)
                game_label.setStyleSheet("color: white;")
                self.games_layout.addWidget(game_label)
                self.game_labels[game] = game_label
            self.visible_games = list(self.games)
        else:
            self.games_layout.addWidget(QLabel("Please connect to the database."))

    def ask(self):
        self.rolled_game = None

        for _, label in self.game_labels.items():
            label.setVisible(True)
            label.setStyleSheet("color: white;")
        self.visible_games = list(self.games)

        self.ask_message_id = asyncio.run_coroutine_threadsafe(
            self.bot.send_message(
                "Let's spin the wheel of luck! Who's in?"
            ),
            self.bot.client.loop
        ).result()
        print(f"Message ID: {self.ask_message_id}")

    def set_last_spin_visibility(self, visible: bool) -> None:
        """ Show/hide the 'last spin' UI section. """
        self.win_btn.setVisible(visible)
        self.lose_btn.setVisible(visible)
        self.last_spin_lbl.setVisible(visible)
        if visible and self.db.is_connected:
            self.last_spin_lbl.setText(f"Last game result?\n({self.db.get_last_spin_string()})")

    def on_spin_outcome(self, outcome: str) -> None:
        """User confirmed win/lose. Insert into DB and hide the W/L UI."""
        try:
            if self.db.is_connected:
                self.db.insert_log_into_database(outcome)
        except Exception as e:
            print("Failed to insert outcome: ", e)

        if outcome == "W":
            self.win_lose_msg.setText("\nYOU ARE THE BEST")
        else:
            self.win_lose_msg.setText("\nYOU SUCK")
        self.win_lose_msg.setVisible(True)

        self.set_last_spin_visibility(False)

    def compute_common_games(self, players: list[str]) -> list[str]:
        """ Returns a list of common games for players in players list. """
        if not players:
            return []

        common = set(self.db.get_list_of_user_games(players[0]))
        for name in players[1:]:
            games = set(self.db.get_list_of_user_games(name))
            # Keep only the games that are in both sets
            common &= games
            if not common:
                break
        # Common games must be only available games 
        common &= set(self.games)
        return sorted(common)
    
    def filter_ui_by_common_games(self, common_games: list[str]) -> None:
        """ Skryje všechny hry mimo common_games a nastaví visible_games jen na ty společné. """
        if not common_games:
            return

        common_set = set(common_games)
        for game, label in self.game_labels.items():
            label.setVisible(game in common_set)

        self.visible_games = list(common_games)

    def start_spin_wheel(self):
        """ Starts the spinning animation. """
        # Check if there are any games to spin
        if not self.games:
            self.result_lbl.setText("No games available!")
            return
        
        # Get players that reacted to the ask message
        players = []
        if self.ask_message_id is not None:
            try:
                players = asyncio.run_coroutine_threadsafe(
                    self.bot.get_reaction_users(self.ask_message_id),
                    self.bot.client.loop
                ).result()
            except Exception as e:
                print("Failed to read reaction users:", e)

        if players:
            common_games = self.compute_common_games(players)
            if not common_games:
                self.result_lbl.setText("No common games found for the current participants.")
                return
            self.filter_ui_by_common_games(common_games)
            self.last_players = players
        else:
            self.visible_games = list(self.games)
            self.last_players = []

        # Whiten all games
        for i in range(self.games_layout.count()):
            label: QLabel = self.games_layout.itemAt(i).widget()
            label.setStyleSheet("color: white;")

        if not self.visible_games:
            self.result_lbl.setText("No games to spin.")
            return
        
        # Hide last spin UI
        self.result_lbl.setText("")
        self.set_last_spin_visibility(False)
        self.win_lose_msg.setVisible(False)

        self.rolled_game = random.choice(self.visible_games)
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
            prev_label: QLabel = self.games_layout.itemAt(self.previous_index).widget()
            if prev_label:
                prev_label.setStyleSheet("color: white;")

        tries = 0
        while tries < self.games_layout.count():
            curr_label: QLabel = self.games_layout.itemAt(self.current_index).widget()
            if curr_label.isVisible():
                break
            self.current_index = (self.current_index + 1) % self.games_layout.count()
            tries += 1

        # Highlight the current game in green
        curr_game_label = self.games_layout.itemAt(self.current_index).widget()
        curr_game_label.setStyleSheet("color: lime;")

        # Move to the next game (circular loop)
        self.previous_index = self.current_index
        self.current_index = (self.current_index + 1) % self.games_layout.count()

        if self.spin_speed > 300 and curr_game_label.text() == self.rolled_game:
            # Stop spinning and announce the winner
            self.timer.stop()
            self.timer.timeout.disconnect()
            self.result_lbl.setText(f"🎉 Enjoy {self.rolled_game}!")

            # Write the last spin (without outcome yet)
            try:
                if self.db.is_connected:
                    self.db.update_last_spin(self.rolled_game, players=self.last_players)
            except Exception as e:
                print("Failed to update last spin: ", e)

            self.set_last_spin_visibility(True)
        else:
            # Continue spinning
            self.spin_speed = self.spin_speed + self.slowdown_factor
            self.timer.start(self.spin_speed)

    def announce_game(self):
        """ Announces the rolled game via the Discord bot. """
        if self.rolled_game:
            text = f"Going to play {self.rolled_game}, anyone wanna join in?"
            if self.last_players:
                text = f"Going to play {self.rolled_game} with {', '.join(self.last_players)}. Anyone else?"
            asyncio.run_coroutine_threadsafe(self.bot.send_message(text), self.bot.client.loop)

    def open_settings(self):
        """ Opens the settings window. """
        self.settings_window = SettingsWindow(self)
        self.settings_window.show()

    def closeEvent(self, event: QEvent):
        """
        Handles application exit to properly shut down the Discord bot.
        """
        print("Closing application...")

        if self.bot.client.loop.is_running():
            print("Logging out the Discord bot...")
            asyncio.run_coroutine_threadsafe(self.bot.logout(), self.bot.client.loop)
        
        print("Bot thread closing.")
        # Ensure the bot thread properly exits
        self.bot_thread.join()
        print("Bot thread closed.")

        event.accept()  # Allow the window to close

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

    # TODO Wait for the bot to be ready
    # await bot.wait_until_ready()

    main_window = MainWindow(db, bot, bot_thread)
    main_window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    # Create an event loop for the main function
    asyncio.run(main())
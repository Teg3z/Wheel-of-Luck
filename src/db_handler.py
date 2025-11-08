"""
db_handler.py

A module containing the DbHandler class that handles all database operations.

Dependencies:
- Requires pymongo to interact with the MongoDB database.
- Requires ServerApi to specify the server API version.
- Requires env_var_loader to load environment variables.
"""

from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from functools import wraps

from utils import load_config

class Singleton(type):
    """
    Metaclass for implementing the Singleton pattern.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Ensures that only one instance of the class is created.
        """
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class DbHandler(metaclass=Singleton):
    """
    A class that handles all database operations.

    Main Functions:
    - get_last_spin_string: Returns the last spin in a formatted string.
    - update_last_spin: Updates the last spin in the database with the new game and players.
    - is_last_spin_inserted: Checks if the last spin has been inserted into the logs.
    - insert_log_into_database: Inserts the last spin into the logs collection.
    - get_list_of_games: Returns a list of all games in the database.
    - add_game_to_game_list: Adds a new game to the game list in the database.
    """
    def __init__(self, db_name='WheelOfLuck') -> None:
        """
        Initializes the database connection and creates the necessary collections.
        
        Parameters:
            db_name (str): The name of the database to connect to. Defaults to 'WheelOfLuck'.

        Returns:
            None
        """
        self.db_connection_string = load_config().get("DB_CONNECTION_STRING", "")
        if not self.db_connection_string:
            self.is_connected = False
            print("Database connection string not found in config file.")
            return
        
        try:
            # Verify the connection by pinging the server using the 'admin' command
            self.client = MongoClient(
                self.db_connection_string,
                server_api=ServerApi('1'),
            )
            self.client.admin.command('ping')
            self.is_connected = True
            print("Successfully connected to MongoDB!")
        except Exception as e:
            self.is_connected = False
            print("Failed to connect to MongoDB: ", e)

        if self.is_connected:
            self.db = self.client[db_name]
            self.last_spin_collection = self.db['LastSpin']
            self.logs_collection = self.db['Logs']
            self.games_collection = self.db['Games']
            self.players_collection = self.db['Players']

    def requires_connection(func):
        # Decorator to check if the database connection is established
        @wraps(func)
        def wrapper(self, *args: any, **kwargs: any) -> any:
            if not self.is_connected:
                print(f"Cannot execute {func.__name__}: No connection to the database.")
                return
            return func(self, *args, **kwargs)
        return wrapper

    @requires_connection
    def get_last_spin_string(self) -> str:
        """
        Returns the last spin in a formatted string.

        Returns:
            str: The formatted string of the last spin.
        """
        entry = self.last_spin_collection.find_one()
        formatted_time = entry['last_game_date'].strftime("%d/%m/%Y %H:%M:%S")

        return str(entry['players']) + " - " + entry['last_game'] + \
            " [" + formatted_time + "]"

    @requires_connection
    def update_last_spin(self, game: str, players: list[str]) -> None:
        """
        Updates the last spin in the database with the new game and players.
        
        Parameters:
            game (str): The name of the game that was played.
            players (list[str]): The list of players that played the game.

        Returns:
            None
        """
        # Create the time of the spin
        time = datetime.now()

        # Select the correct collection from the DB and create the new data values to enter
        new_values = { "$set": {
            "last_game": game,
            "last_game_date": time,
            "players": players,
            "is_inserted": False
            }
        }
        # Get the single entry that will be updated
        entry = self.last_spin_collection.find_one()
        id_filter = {'_id': entry['_id']}

        self.last_spin_collection.update_one(id_filter, new_values)

    @requires_connection
    def is_last_spin_inserted(self) -> tuple[bool, dict]:
        """
        Checks if the last spin has been inserted into the logs.

        Returns:
            tuple[bool, dict]: A tuple containing a boolean value and the last spin entry.
        """
        entry = self.last_spin_collection.find_one()

        if entry["is_inserted"]:
            return True, entry
        return False, entry

    @requires_connection
    def insert_log_into_database(self, result: str) -> None:
        """
        Inserts the last spin into the logs collection.

        Parameters:
            result (str): The result of the last spin.

        Returns:
            None
        """
        is_inserted, entry = self.is_last_spin_inserted()
        if not is_inserted:
            new_values = { "$set": {
                "is_inserted": True
                }
            }
            id_filter = {'_id': entry['_id']}
            self.last_spin_collection.update_one(id_filter, new_values)
        else:
            return

        post = {
            "game_date": entry['last_game_date'],
            "game": entry['last_game'],
            "result": result,
            "players": entry['players']
        }

        self.logs_collection.insert_one(post)

    @requires_connection
    def get_list_of_games(self) -> list[str]:
        """
        Returns a list of all games in the database.

        Returns:
            list[str]: A list of all games in the database.
        """
        games = []

        for query in self.games_collection.find():
            games.append(query["name"])

        # Sort the games alphabetically
        games.sort()
        return games

    @requires_connection
    def add_game_to_game_list(self, game: str) -> bool:
        """
        Adds a new game to the game list in the database.

        Parameters:
            game (str): The name of the game to add.

        Returns:
            bool: True if the game was added, False otherwise.
        """
        if self.is_in_game_list(game):
            return False

        self.games_collection.insert_one({"name": game})
        return True

    @requires_connection
    def remove_game_from_game_list(self, game: str) -> bool:
        """
        Removes a game from the game list in the database.

        Parameters:
            game (str): The name of the game to remove.

        Returns:
            bool: True if the game was removed, False otherwise.
        """
        if not self.is_in_game_list(game):
            return False

        self.games_collection.delete_one({"name": game})
        return True

    @requires_connection
    def is_in_game_list(self, game: str) -> bool:
        """
        Checks if a game is in the game list.

        Parameters:
            game (str): The name of the game to check.

        Returns:
            bool: True if the game is in the list, False otherwise
        """
        count = self.games_collection.count_documents({"name": game})
        if count == 0:
            return False
        return True

    @requires_connection
    def add_new_player(self, user_name: str) -> dict:
        """
        Adds a new player to the database.

        Parameters:
            user_name (str): The name of the user to add.

        Returns:
            dict: The document of the newly added player.
        """
        new_document = {
            "name": user_name,
            "games": []
            }
        self.players_collection.insert_one(new_document)
        return new_document

    @requires_connection
    def get_list_of_user_games(self, user_name: str) -> list[str]:
        """
        Returns a list of games that the user plays.

        Parameters:
            user_name (str): The name of the user to get the games from.

        Returns:
            list[str]: A list of games that the user plays.
        """
        user = self.players_collection.find_one({"name": user_name})
        if user is None:
            user = self.add_new_player(user_name)
        user_games: list = user["games"]
        # Sort the games alphabetically
        user_games.sort()
        return user_games

    @requires_connection
    def add_game_to_user_game_list(self, user_name: str, game: str) -> None:
        """
        Adds a game to the user's game list.

        Parameters:
            user_name (str): The name of the user to add the game to.
            game (str): The name of the game to add.

        Returns:
            None
        """
        self.create_player_if_not_exists(user_name)

        self.players_collection.update_one(
            {"name": user_name},
            {"$addToSet": {"games": game}}
        )

    @requires_connection
    def remove_game_from_user_game_list(self, user_name: str, game: str) -> None:
        """
        Removes a game from the user's game list.

        Parameters:
            user_name (str): The name of the user to remove the game from.
            game (str): The name of the game to remove.

        Returns:
            None
        """
        self.create_player_if_not_exists(user_name)

        self.players_collection.update_one(
            {"name": user_name},
            {"$pull": {"games": game}}
        )

    @requires_connection
    def create_player_if_not_exists(self, user_name: str) -> None:
        """
        Creates a new player if the player doesn't exist.

        Parameters:
            user_name (str): The name of the user to check.

        Returns:
            None
        """
        user = self.players_collection.find_one({"name": user_name})
        if user is None:
            self.add_new_player(user_name)

def main():
    """
    The main entry point of the script.

    Only used for testing this module.

    Returns:
        None
    """
    db = DbHandler()
    collection = db.get_list_of_user_games("TestUser")

    # Now you can perform operations on the collection, such as finding all players
    for query in collection:
        print(query)

if __name__ == "__main__":
    main()

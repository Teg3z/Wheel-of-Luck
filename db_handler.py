"""
db_handler.py

This module contains database handling functions.

Main Functions:
- connect_to_db: Establishes a connection to the MongoDB database.
- get_list_of_games: Retrieves a list of all games from the database.
- get_list_of_user_games: Retrieves a list of games associated with a specific user.
- add_game_to_user_game_list: Adds a game to a user's list of games in the database.
- remove_game_from_user_game_list: Removes a game from a user's list of games in the database.

Dependencies:
- Requires pymongo for MongoDB interactions.
- Requires env_var_loader to load environment variables.
"""

from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from env_var_loader import get_env_var_value

def connect_to_db():
    """
    Establishes a connection to the MongoDB database.

    Returns:
        pymongo.mongo_client.MongoClient:
            A MongoClient instance connected to the specified database.
    """
    db_connection_string = get_env_var_value("DB_CONNECTION_STRING")
    # Create a new client and connect to the server
    client = MongoClient(db_connection_string, server_api=ServerApi('1'))
    # Connect to database namespace
    return client['WheelOfLuck']

def get_last_spin_string(db):
    """
    Retrieves the whole record of the last spin collection from MongoDB.
    
    Makes the record in a string form that is easily printable for the user,
    so the user can understand it. 

    Parameters:
        db (pymongo.mongo_client.MongoClient):
            An instance of a MongoClient connected to the specified database.

    Returns:
        String: Contains every relevant attribute of the last spin record
            (`last_category`, `last_game`, `last_game_date`) in an easily readable form.
    """
    collection = db['LastSpin']
    entry = collection.find_one()
    formatted_time = entry['last_game_date'].strftime("%d/%m/%Y %H:%M:%S")

    return entry['last_category'] + " - " + entry['last_game'] + \
        " [" + formatted_time + "]"

def update_last_spin(db, game, category = None, players = None):
    """
    Updates the last spin in the MongoDB collection.

    After a wheel spin, the last spin needs to be updated based on which of the two approaches
    was chosen - either a spin based on `category` (group buttons like "DK", "DKKA") or `players`
    (button "REACTION PLAY" - based on message reactions).

    In their respective cases either the parameter `category` or parameter `players` is set,
    but only one of them every time.

    After that the function takes the current time as the time of the spin.
    Game that was rolled during the spin is put in as an argument.
    Both of those are inserted into a dictionary representing a MongoDB document. 

    Parameters:
        db (pymongo.mongo_client.MongoClient):
            An instance of a MongoClient connected to the specified database.
        game (string): The name of the game that was rolled during the spin.
        category (string, optional): The name of the category that initiated the spin.
            Basically the button name.
        players (List, optional): The list of players who participated in the wheel spin.
            (By reacting to the bots Discord message). 

    Returns:
        None
    """
    # Create the time of the spin
    time = datetime.now()

    # Select the correct collection from the DB and create the new data values to enter
    if players is not None:
        collection = db['LastSpinReaction']
        new_values = { "$set": {
            "last_game": game,
            "last_game_date": time,
            "players": players
            }
        }
        # Get the single entry that will be updated
        entry = collection.find_one()
        id_filter = {'_id': entry['_id']}

        collection.update_one(id_filter, new_values)

    elif category is not None:
        collection = db['LastSpin']
        new_values = { "$set": {
            "last_category" : category,
            "last_game": game,
            "last_game_date": time
            }
        }
        # Get the single entry that will be updated
        entry = collection.find_one()
        id_filter = {'_id': entry['_id']}

        collection.update_one(id_filter, new_values)

def insert_log_into_database(db, result):
    """
    Gets all information from the last spin in the database and inserts
    a new document with the `result` parameter into the correspoding collection
    by the category of the last spin. Doesn't yet support "REACTION PLAY"

    Parameters:
        db (pymongo.mongo_client.MongoClient):
            An instance of a MongoClient connected to the specified database.
        result (string): The result of the played game. Either "W" or "L" (Win/Lose).

    Returns:
        None
    """
    collection = db['LastSpin']
    entry = collection.find_one()
    collection = db["Logs" + entry['last_category']]

    post = {"game_date": entry['last_game_date'],
            "game": entry['last_game'],
            "result": result}

    collection.insert_one(post)

def get_list_of_games(db):
    """
    Retrieves a list of all games from the MongoDB database in alphabetically sorted order.

    Parameters:
        db (pymongo.mongo_client.MongoClient):
            An instance of a MongoClient connected to the specified database.

    Returns:
        List: A list of strings containing all game names (alphabetically sorted).
    """
    games = []
    collection = db["Games"]

    for query in collection.find():
        games.append(query["name"])

    # Sort the games alphabetically
    games.sort()
    return games

def get_list_of_user_games(db, user_name):
    """
    Retrieves a list of all games from the MongoDB database in alphabetically sorted order.
    for the specified user.

    Parameters:
        db (pymongo.mongo_client.MongoClient):
            An instance of a MongoClient connected to the specified database.
        user_name (string): Users Dicord name (not server nick).

    Returns:
        List: A list of strings containing all users game names (alphabetically sorted).
    """
    collection = db["Players"]
    user = collection.find_one({"name": user_name})
    user_games = user["games"]
    # Sort the games alphabetically
    user_games.sort()
    return user_games

def add_game_to_user_game_list(db, user_name, game):
    """
    Adds a game name to the users list of games in the database.

    Parameters:
        db (pymongo.mongo_client.MongoClient):
            An instance of a MongoClient connected to the specified database.
        user_name (string): Users Dicord name (not server nick).
        game (string): A name of the game.

    Returns:
        None
    """
    collection = db["Players"]
    collection.update_one(
        {"name": user_name},
        {"$addToSet": {"games": game}}
    )

def remove_game_from_user_game_list(db, user_name, game):
    """
    Removes a game name from the users list of games in the database.   

    Parameters:
        db (pymongo.mongo_client.MongoClient):
            An instance of a MongoClient connected to the specified database.
        user_name (string): Users Dicord name (not server nick).
        game (string): A name of the game.

    Returns:
        None
    """
    collection = db["Players"]
    collection.update_one(
        {"name": user_name},
        {"$pull": {"games": game}}
    )

def main():
    """
    The main entry point of the script.

    Only used for testing this module.

    Returns:
        None 
    """
    db = connect_to_db()
    collection = get_list_of_user_games(db, "tegez")

    # Now you can perform operations on the collection, such as finding all players
    for query in collection:
        print(query)

if __name__ == "__main__":
    main()

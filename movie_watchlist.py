#                                      Movie Watchlist Project

#Smth other than the line i wrote in conflict branch


import requests
import sqlite3

conn = sqlite3.connect("watchlist.db")
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS watchlist(
            id          INTEGER PRIMARY KEY,
            show_id     INTEGER UNIQUE,
            name        TEXT,
            language    TEXT,
            genres      TEXT)""")
# c.execute("ALTER TABLE watchlist ADD COLUMN watched INTEGER DEFAULT 0")

def int_input(prompt):
    try:
        return int(input(prompt))
    except ValueError:
        print("Please enter an integer value")
        return None

def search_result():
    url = "https://api.tvmaze.com/search/shows"

    movie_name = input("Enter the movie name: ").strip()

    if not movie_name:
        print("Please enter the show name.")
        return None

    params = {
        "q": movie_name
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        print("Could not connect to API. Please try again.")
        return None

    data = response.json()

    if not data:
        print("No shows found.")
        return None

    for number, results in enumerate(data[:5], start=1):
        print(f"{number}. Name of show: ", results["show"]["name"])
        print("   Show id: ", results["show"]["id"])
        print("   genres of show: ", results["show"]["genres"])
        print("   Language of show: ", results["show"]["language"])
        print("\n")

    print("Enter the number of movie to be selected: ")
    movie_selection = int_input("(or 0 to cancel): ")

    if movie_selection is None:
        print("Invalid input")
        return None

    elif movie_selection == 0:
        return None

    elif movie_selection < 0 or movie_selection > min(5, len(data)):
        return -1

    else:
        return data[movie_selection - 1]["show"]

def add_wishlist(data):
    name = data["name"]
    show_id = data["id"]
    genres = ", ".join(data["genres"])
    language = data["language"]

    try:
        c.execute("""INSERT INTO watchlist(show_id,name,language,genres)
                    VALUES (:show_id,:name,:language,:genres)""",
                    {"show_id": show_id, "name": name,
                     "language": language, "genres": genres})
        conn.commit()

        print(f"{name} added to wishlist!!\n")

    except sqlite3.IntegrityError:
        print("Selected show already in watchlist!!")

def show_watchlist():
    c.execute("SELECT * FROM watchlist")
    watchlist_content = c.fetchall()

    if not watchlist_content:
        print("Your watchlist is empty!!\n")
    else:
        print("\n========== MY WATCHLIST ==========\n")

        for number, show in enumerate(watchlist_content, start=1):
            print(f"{number}. Name: {show[2]} ")
            print(f"   Show id: {show[1]} ")
            print(f"   Genres: {show[4]} ")
            print(f"   Language: {show[3]} ")

        print("======================================")

def mark_watched():
    c.execute("SELECT name, watched FROM watchlist")
    data = c.fetchall()
    if not data:
        print("Empty watchlist!!")
        return
    
    for number, show in enumerate(data, start=1):
        if show[1] == 0:
            watch_status = "Not Watched"
        elif show[1] == 1:
            watch_status = "Watched"
        print(f"{number}. {show[0]} [{watch_status}]")
    print()

    show_selection = int_input("Enter the show number to mark as watched: ")
    if show_selection is None:
        print("Invalid input")
        return

    if show_selection < 1 or show_selection > len(data):
        print("Invalid selection")
        return

    watch_status = data[show_selection-1]

    if watch_status[1] == 1:
        print("Already watched")
        
    elif watch_status[1] == 0:
        print(f"{watch_status[0]} is marked as watched")
        c.execute("UPDATE watchlist SET watched = 1 WHERE name = ?",(watch_status[0],))
        conn.commit()

def del_show():
    show_watchlist()

    c.execute("SELECT * FROM watchlist")
    watchlist_content = c.fetchall()

    print("Enter the number of the show to be deleted: ")
    selection = int_input("(or 0 to cancel): ")

    if selection is None:
        print("invalid input")
        return

    if selection == 0:
        print("Deletion cancelled!!\n")
        return

    elif selection < 1 or selection > len(watchlist_content):
        print("Invalid selection....\n")
        return

    selected_show = watchlist_content[selection - 1]

    db_id = selected_show[0]
    show_name = selected_show[2]

    c.execute("DELETE FROM watchlist WHERE id = ?", (db_id,))
    conn.commit()

    print(f"The show {show_name} deleted from watchlist\n")

def show_menu():
    print("""1. Search for a show
2. View watchlist
3. Remove from watchlist
4. Mark show as watched
5. Exit""")

while True:
    show_menu()

    user_input = int_input("Choose you option from the menu: ")
    if user_input is None:
        continue

    elif user_input == 1:
        data = search_result()

        if data == -1:
            print("Enter a valid number of show......\n")
            continue

        elif data is not None:
            add_wishlist(data)

    elif user_input == 2:
        show_watchlist()

    elif user_input == 3:
        del_show()

    elif user_input == 4:
        mark_watched()

    elif user_input == 5:
        break

    else:
        print("Choose valid option based on the menu")

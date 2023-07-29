from simple_term_menu import TerminalMenu
import datetime
import sqlite3

# GLOBAL VARIABLES
CUST_ID = None

def main():
    conn = sqlite3.connect('library.db');

    options = ["Find an item in the library", 
            "Return a borrowed item",
            "Donate an item to the library",
            "Find an event in the library",
            "Register for an event in the library",
            "Volunteer for the library",
            "Ask for help from a librarian",
            "Exit"
            ]

    terminal_menu = TerminalMenu(options)
    
    with conn:
        cursor = conn.cursor()
        CUST_ID = loginUser(cursor)
        while True:
            print("\nWelcome to CMPT354 library. What would you like to do?")
            menu_entry_index = terminal_menu.show()

            match menu_entry_index:
                case 0:
                    findItem(cursor)
                case 1:
                    returnItem(cursor)
                case 2:
                    donateItem(cursor)
                case 3:
                    findEvent(cursor)
                case 4:
                    registerEvent(cursor)
                case 5:
                    volunteer(cursor)
                case 6:
                    getHelp(cursor)
                case 7:
                    break
    if conn:
        conn.close()
        print("Closed database successfully")

def loginUser(cursor):
    names = None
    
    while True:
        names = input("Please enter your first name and last name, separated by a space: ")
        names = names.split()
        if (len(names) == 2):
            break

    query = "SELECT * FROM Customer WHERE first_name = :first_name COLLATE NOCASE \
            AND last_name = :last_name COLLATE NOCASE"
    cursor.execute(query, {'first_name': names[0], 'last_name': names[1]})
    rows = cursor.fetchall()
    if (rows):
        print(f"Welcome back, {names[0]}")
        CUST_ID = rows[0][0]
    else:
        print(f"Creating new account for {names[0]} {names[1]}...")
        while True:
            try:
                birthdate = input("Please enter your birthdate (yyyy-mm-dd): ")
                validateDateString(birthdate)
                break
            except ValueError as error:
                print(error)

        query = "INSERT INTO Customer (first_name, last_name, birthdate) VALUES (:first_name, :last_name, :birthdate)"
        cursor.execute(query, {'first_name': names[0], 'last_name': names[1], 'birthdate': birthdate})
        CUST_ID = cursor.lastrowid
    print(CUST_ID)


def findItem(cursor):
    print("Would you like to search by title or author? \n")
    menu_entry_index = getUserInput(["Title", "Author"])
    match menu_entry_index:
        case 0:
            findByTitle(cursor)
        case 1:
            findByAuthor(cursor)

def returnItem(cursor):
    print("Returning")

def donateItem(cursor):
    print("Donating")

def findEvent(cursor):
    print("Finding event")

def registerEvent(cursor):
    print("Registering for event")

def volunteer(cursor):
    print("Volunteering")

def getHelp(cursor):
    print("Asking for help")

def findByTitle(cursor):
    title = input("Please enter the title of the item you are looking for: ")
    query = "SELECT id, title, first_name, last_name, year FROM Item NATURAL JOIN Author WHERE title = :title COLLATE NOCASE"
    cursor.execute(query, {'title': title})
    rows = cursor.fetchall()
    if rows:
        print(f"\nWe have found the following items matching the title \"{title}\":")
        for row in rows:
            print(row)
        itemId = getSelectedItemId(rows)
        if (itemId == -1):
            return
        borrowItem(cursor, itemId)
    else:
        print("Could not find any matching items")


def findByAuthor(cursor):
    author = input("Please enter the name of the author you are looking for:")
    names = author.split()

    # Some authors can only have a first name. For example, "Dr.Seuss"
    if len(names) < 2:
        names += [None]

    query = "SELECT id, title, first_name, last_name, year FROM Item NATURAL JOIN Author WHERE first_name = :first_name COLLATE NOCASE \
             AND last_name IS :last_name COLLATE NOCASE"
    cursor.execute(query, {'first_name': names[0], 'last_name': names[1]})
    rows = cursor.fetchall()

    if rows:
        print(f"\nWe have found the following items matching the author \"{author}\":")
        for row in rows:
            print(row)
    else:
        print("Could not find any matching items")

# PARAMS: a list containing strings representing select menu options
# RETURNS: the index of the selected option in the list
def getUserInput(options):
    terminal_menu = TerminalMenu(options)
    menu_entry_index = terminal_menu.show()
    return menu_entry_index

# PARAMS: a row of tuples returned from a query
# RETURNS: The id attribute of the selected item, or -1 if no item was selected
def getSelectedItemId(rows):
    print("\nWould you like to borrow an item?")
    # Convert tuples in rows array to strings to be used for options
    options = []
    for row in rows:
        option = ', '.join(str(item) for item in row)
        options.append(option)
    
    options.append("Return")

    menu_entry_index = getUserInput(options)

    # If user selects "Return", return -1
    if (menu_entry_index == len(options) - 1):
        return -1
    return rows[menu_entry_index][0]

# PARAMS: a cursor, the id of the item to borrow
# POST: adds to the borrowed table if item is not checked out already
def borrowItem(cursor, itemId):
    query = "SELECT * FROM Borrowed WHERE id = :itemId"
    cursor.execute(query, {'itemId': itemId})
    rows = cursor.fetchall()
    if rows:
        print("Can borrow!")
    else:
        print("Checked out by another customer!")

def validateDateString(dateString):
    try:
        datetime.date.fromisoformat(dateString)
    except ValueError:
        raise ValueError("Date must be in format yyyy-mm-dd")

if __name__ == "__main__":
    main()
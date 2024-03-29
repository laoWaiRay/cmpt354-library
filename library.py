
import datetime
import re
import sqlite3
import sys
import subprocess
import pkg_resources


required = {'simple_term_menu'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed

if missing:
    python = sys.executable
    subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)

from simple_term_menu import TerminalMenu


# GLOBAL VARIABLES
global CUST_ID
global MAX_TITLE_LENGTH
MAX_TITLE_LENGTH = 20
global ITEM_TYPES
ITEM_TYPES = ['print', 'digital', 'magazine', 'journal', 'cd', 'record', 'dvd', 'game']





def main():
    conn = sqlite3.connect('library.db');

    options = ["Find an item in the library", 
            "Return a borrowed item",
            "Donate an item to the library",
            "Find and register for an event",
            "Volunteer for the library",
            "Ask for help from a librarian",
            "List",
            "Exit"
            ]

    terminal_menu = TerminalMenu(options)
    
    with conn:
        cursor = conn.cursor()
        global CUST_ID
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
                    volunteer(cursor)
                case 5:
                    getHelp(cursor)
                case 6:
                    getList(cursor)
                case 7:
                    break
            conn.commit()
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
        return rows[0][0]   # Return the customer ID
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
        return cursor.lastrowid  # Return the customer ID


def findItem(cursor):
    print("Would you like to search by title or author? \n")
    menu_entry_index = getUserInput(["Title", "Author"])
    match menu_entry_index:
        case 0:
            findByTitle(cursor)
        case 1:
            findByAuthor(cursor)

def returnItem(cursor):
    query = "SELECT id, title, A.first_name, A.last_name, year, due_date FROM Borrowed \
                NATURAL JOIN Customer \
                NATURAL JOIN Item I \
                JOIN Author A ON I.aid = A.aid \
             WHERE cid = :custID"
    cursor.execute(query, {'custID': CUST_ID})
    rows = cursor.fetchall()
    print("\nWhich item would you like to return?")
    itemId = getSelectedItemId(rows)
    if (itemId != -1):
        query = "DELETE FROM Borrowed WHERE id = :itemId AND cid = :custId"
        cursor.execute(query, {'itemId': itemId, 'custId': CUST_ID})
        print("Successfully returned item")


def donateItem(cursor):
    print("Please provide some information about the item")
    while True:
        title = input("Title: ")
        if len(title) < MAX_TITLE_LENGTH:
            break
        else:
            print(f"Title must be less than {MAX_TITLE_LENGTH} characters long")

    while True:
        year = input("Year: ")
        if isValidYear(year):
            break
        else:
            print("Please enter a valid year")
    
    while True:
        authorName = input("Author: ")
        names = authorName.split()
        if (len(names) == 2):
            break
        else:
            print("Must follow pattern: FIRSTNAME LASTNAME")
    
    firstName = names[0]
    lastName = names[1]
    
    query = "SELECT aid FROM Author WHERE first_name = :first AND last_name = :last"
    cursor.execute(query, {'first': firstName, 'last': lastName})
    rows = cursor.fetchall()
    if not rows:
        print(f"Creating new entry for author: {firstName} {lastName}...")
        while True:
            try:
                authorBirthdate = input(f"What is {firstName} {lastName}'s birthdate (yyyy-mm-dd)? ")
                validateDateString(authorBirthdate)
                break
            except ValueError:
                print("Invalid date format")
        
        query = "INSERT INTO Author (first_name, last_name, birthdate) VALUES (:first, :last, :birthdate)"
        cursor.execute(query, {'first': firstName, 'last': lastName, 'birthdate': authorBirthdate})
        aid = cursor.lastrowid
    else:
        aid = rows[0][0]

    
    print("Type: ")
    menu_entry_index = getUserInput(ITEM_TYPES)
    itemType = ITEM_TYPES[menu_entry_index]

    query = "INSERT INTO Item (title, year, type, aid) VALUES (:title, :year, :type, :aid)"
    cursor.execute(query, {'title': title, 'year': year, 'type': itemType, 'aid': aid})
    print("Thank you for your donation")
    
def findEvent(cursor):
    query = "SELECT bid, name, e_type, audience, room_number, date, start_time, end_time \
             FROM Event NATURAL JOIN Room_Booking"
    cursor.execute(query)
    rows = cursor.fetchall()
    print("\nWhich event would you like to register for?\n")
    print("BID | Name | Type | Audience | Room Number | Date | Start Time | End Time")
    BID = getSelectedItemId(rows)
    if (BID != -1):
        try:
            query = "INSERT INTO Attendee (bid, cid) VALUES (:bid, :cid)"
            cursor.execute(query, {'bid': BID, 'cid': CUST_ID})
        except sqlite3.IntegrityError as error:
            print(error)

def volunteer(cursor):

    query = "SELECT first_name, last_name, birthdate FROM Customer WHERE cid = :cid"
    cursor.execute(query, {'cid': CUST_ID})
    rows = cursor.fetchall()
    first_name, last_name, birth = rows[0]
    
    query = "SELECT pid FROM Personnel WHERE first_name = :first_name AND last_name = :last_name AND birthdate = :birth"
    cursor.execute(query, {'first_name': first_name, 'last_name': last_name, 'birth': birth})
    rows = cursor.fetchall()
    if rows:
        print("You're already registered as a volunteer!")
    else:
        query = "INSERT INTO Personnel (first_name, last_name, birthdate, role, salary) VALUES (:first_name, :last_name, :birth, :role, :salary)"
        cursor.execute(query, {'first_name': first_name, 'last_name': last_name, 'birth': birth, 'role': 'volunteer', 'salary': 0 })
        print("You've been registered as a volunteer!")

def getHelp(cursor):
    print("These are the available Librarians, who would you like to help you")
    query = "SELECT first_name, last_name FROM Personnel WHERE role = 'supervisor'"
    cursor.execute(query, {})
    rows = cursor.fetchall()
    BID = getSelectedItemId(rows)

    if (BID != 1):
        print("Hi how can I help")




def findByTitle(cursor):
    title = input("Please enter the title of the item you are looking for: ")
    query = "SELECT id, title, first_name, last_name, year FROM Item NATURAL JOIN Author WHERE title LIKE :title"
    cursor.execute(query, {'title': '%'+title+'%'})
    rows = cursor.fetchall()
    if rows:
        print(f"\nWe have found the following items matching the title \"{title}\":")
        for row in rows:
            print(row)
        
        print("\nBorrow an item?\n")
        itemId = getSelectedItemId(rows)
        if (itemId == -1):
            return
        borrowItem(cursor, itemId)
    else:
        print("Could not find any matching items")


def findByAuthor(cursor):
    author = input("Please enter the name of the author you are looking for: ")
    names = author.split()
    print(names)
    print('%'+names[0]+'%')

    # Some authors can only have a first name. For example, "Dr.Seuss"
    if len(names) < 2:
        query = "SELECT id, title, first_name, last_name, year FROM Item NATURAL JOIN Author \
             WHERE first_name LIKE :first_name"
        cursor.execute(query, {'first_name': '%'+names[0]+'%'})
    else:
        query = "SELECT id, title, first_name, last_name, year FROM Item NATURAL JOIN Author \
                 WHERE first_name LIKE :first_name OR last_name LIKE :last_name"
        cursor.execute(query, {'first_name': '%'+names[0]+'%', 'last_name': '%'+names[1]+'%'})
    
    rows = cursor.fetchall()

    if rows:
        print(f"\nWe have found the following items matching the author \"{author}\":")
        for row in rows:
            print(row)
        print("\nWould you like to borrow an item?")
        itemId = getSelectedItemId(rows)
        if (itemId != -1):
            borrowItem(cursor, itemId)
    else:
        print("Could not find any matching items")

# PARAMS: a list containing strings representing select menu options
# RETURNS: the index of the selected option in the list
def getUserInput(options):
    terminal_menu = TerminalMenu(options)
    menu_entry_index = terminal_menu.show()
    return menu_entry_index

# PARAMS: a row of tuples returned from a query, where the first element of the tuple must be ID
# RETURNS: The id attribute of the selected item, or -1 if no item was selected
def getSelectedItemId(rows):
    # Convert tuples in rows array to strings to be used for options
    options = []
    for row in rows:
        option = ', '.join(str(item) for item in row)
        options.append(option)
    
    options.append("Back to main menu")

    menu_entry_index = getUserInput(options)

    # If user selects "Back", return -1
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
        print("Sorry, this has been checked out by another customer.")
    else:
        query = "INSERT INTO Borrowed (id, cid) VALUES (:id, :cid)"
        cursor.execute(query, {'id': itemId, 'cid': CUST_ID})
        query = "SELECT title, due_date FROM Borrowed NATURAL JOIN Item WHERE id = :id"
        cursor.execute(query, {'id': itemId})
        row = cursor.fetchone()
        print(f"Checked out \"{row[0]}\" \t Due date: {row[1]}")

def getList(cursor):
    print("\nWhat do you want to list?\n")
    options = ["Titles", "Authors", "Events", "My Events"]
    menu_entry_index = getUserInput(options)
    print(f"Selected \"{options[menu_entry_index]}\": ")

    match menu_entry_index:
        case 0:
            listTitles(cursor)
        case 1:
            listAuthors(cursor)
        case 2:
            listEvents(cursor)
        case 3:
            listMyEvents(cursor)
    
    rows = cursor.fetchall()
    for row in rows:
        print(row[0])

def listTitles(cursor):
    cursor.execute("SELECT title FROM Item")
    rows = cursor.fetchall()
    for row in rows:
        print(row[0])

def listAuthors(cursor):
    cursor.execute("SELECT first_name, last_name FROM Author")
    rows = cursor.fetchall()
    for row in rows:
        print(f"{row[0]} {row[1] or ''}")

def listEvents(cursor):
    cursor.execute("SELECT name FROM Event")
    rows = cursor.fetchall()
    for row in rows:
        print(row[0])

def listMyEvents(cursor):
    query = "SELECT E.name, date, RB.room_number, start_time, end_time FROM Attendee A \
                 NATURAL JOIN Room_Booking RB \
                 JOIN Event E ON E.eid = RB.eid \
             WHERE cid = :cid"
    cursor.execute(query, {'cid': CUST_ID})
    rows = cursor.fetchall()
    for row in rows:
        print(row)

### HELPER FUNCTIONS ###

def validateDateString(dateString):
    try:
        datetime.date.fromisoformat(dateString)
    except ValueError:
        raise ValueError("Date must be in format yyyy-mm-dd")
    
def isValidAuthor(str):
    parts = str.split()
    if (len(parts) > 2):
        return False
    return True

def isValidYear(str):
    match = re.search(r"^[0-9]{4}$", str)
    if match:
        return True
    return False

if __name__ == "__main__":
    main()
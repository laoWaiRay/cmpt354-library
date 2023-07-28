from simple_term_menu import TerminalMenu
import sqlite3

def main():
    conn = sqlite3.connect('library.db');

    options = ["Find an item in the library", 
            "Borrow an item from the library", 
            "Return a borrowed item",
            "Donate an item to the library",
            "Find an event in the library",
            "Register for an event in the library",
            "Volunteer for the library",
            "Ask for help from a librarian"
            ]

    terminal_menu = TerminalMenu(options)
    print("Welcome to CMPT354 library. What would you like to do?")
    menu_entry_index = terminal_menu.show()
    print(f"You have selected{options[menu_entry_index]}")

    match menu_entry_index:
        case 0:
            findItem()
        case 1:
            borrowItem()
        case 2:
            returnItem()
        case 3:
            donateItem()
        case 4:
            findEvent()
        case 5:
            registerEvent()
        case 6:
            volunteer()
        case 7:
            getHelp()

def findItem():
    print("Finding an item")

def borrowItem():
    print("Borrowing")

def returnItem():
    print("Returning")

def donateItem():
    print("Donating")

def findEvent():
    print("Finding event")

def registerEvent():
    print("Registering for event")

def volunteer():
    print("Volunteering")

def getHelp():
    print("Asking for help")

if __name__ == "__main__":
    main()
import sqlite3

conn = sqlite3.connect('library.db')
cursor = conn.cursor()


def main():
    print("Welcome to the library!")
    
    validRequest = False

    while(validRequest == False):
        validRequest = True
        options = input("Please enter the corresponding number for what you would like to do: " + 
                "\n 1. Find an item in the library" +
                "\n 2. Borrow a library item" +
                "\n 3. Return a borrowed item" +
                "\n 4. Donate an item" +
                "\n 5. Find an event" +
                "\n 6. Register for an event" +
                "\n 7. Volunteer for the Library" +
                "\n 8. Get help from a librarian" +
                "\n 9. Exit \n")

        match options:
            case '1':

                findItem()
            case '2':
                print('2')
            case '3':
                print('3')
            case '4':
                print('4')
            case '5':
                print('5')
            case '6':
                print('6')
            case '7':
                print('7')
            case '8':
                print('8')
            case '9':
                print('9')
            case _:
                validRequest = False
                print("please enter a valid entry"); 
    '''
    with conn:

        cur = conn.cursor()

        myQuery = "SELECT * FROM albums NATURAL JOIN artists WHERE Name=:myArtist"

        cur.execute(myQuery,{"myArtist":myFavArtist})

        rows=cur.fetchall()
        if rows:
            print("We do have the following albums from your favorite artist, " + myFavArtist + ": ")
        else:
            print("Unfortunately, we do not have any albums by " + myFavArtist + "!\n")

        for row in rows:
            print(row[1])
        print("\n")

    '''
    if conn:
        conn.close()
        print("Closed database successfully")


def findItem():
    title = input("Please Enter the title of the item \n")
    query = "SELECT * FROM Item WHERE title = :title"
    cursor.execute(query,{'title':title})

    rows=cursor.fetchall()
    if rows:
        print("We do have the following albums from your favorite artist,  Would you like to borrow it?")
    else:
        print("Unfortunately, we do not have an item by that name ")





if __name__=='__main__':
    main()
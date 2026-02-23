from gui import initialise
from create_db import create_database

def main():
    create_database()
    initialise()
    
if __name__ == "__main__":
    main()
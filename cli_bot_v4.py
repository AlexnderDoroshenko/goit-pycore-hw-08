"""
Доробіть консольного бота помічника з попереднього домашнього завдання.

"""
from address_book import AddressBook, Record, datetime, timedelta, DATE_FORMAT
from io import StringIO 
from unittest.mock import patch

import pickle

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Returns new AddressBook is file not exist

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me your name and phone please."
        except IndexError:
            return "To many names, try the command 'all' to investigate."
        except KeyError:
            return "Give me the correct name please, try the command 'all' to investigate."

    return inner


def parse_input(user_input: str) -> tuple:
    """
    Parses the user input into a command and its arguments.
    
    Parameters:
    - user_input (str): The raw input string from the user.
    
    Returns:
    - tuple: A tuple where the first element is the command (str) and the rest are arguments (list of str).
    """
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args: tuple, contacts: AddressBook) -> str:
    """
    Adds a new contact to the contacts dictionary.
    
    Parameters:
    - args (tuple): A tuple containing the name and phone number of the contact.
    - contacts (Dict[str, str]): The dictionary of contacts.
    
    Returns:
    - str: A message indicating the contact was added.
    """
    name, phone = args
    rec = Record(name=name)
    rec.add_phone(phone=phone)
    contacts.add_record(rec)
    return "Contact added."

@input_error
def change_contact(args: tuple, book: AddressBook) -> str:
    """
    Changes the phone number of an existing contact.
    
    Parameters:
    - args (tuple): A tuple containing the name and new phone number of the contact.
    - book (AddressBook): The address book with contacts.
    
    Returns:
    - str: A message indicating the contact was updated or not found.
    """
    name, old_phone, phone = args
    if book.data:
        if name in book.data:
            rec = book.find(name)
            rec.edit_phone(old_phone, phone)
            return "Contact updated."
    return "Contact not found."

def show_phone(args, book:  AddressBook) -> str:
    """
    Retrieves the phone number of a specified contact.
    
    Parameters:
    - args (tuple): A tuple containing the names of the contact.
    - book (AddressBook): The address book with contacts.
    
    Returns:
    - str: The phone number of the contact or a message indicating the contact was not found.
    """
    name, *_ = args
    if name in book.data:
        rec = book.find(name)
        if rec:
            return [phone.value for phone in rec.phones]
    return []

def show_all(book: AddressBook) -> str:
    """
    Returns a string representation of all contacts.
    
    Parameters:
    - book (AddressBook): The address book with contacts.
    
    Returns:
    - str: A contacts dictionary.
    """
    return {name: show_phone((name,), book) for name in book.data}


@input_error
def add_birthday(args: tuple, contacts:  AddressBook) -> None:
    """
    Adds a birthday to contact.
    
    Parameters:
    - args (tuple): A tuple containing the name of the contact.
    - book (AddressBook): The address book with contacts.
    
    Returns:
    - str: update result.
    """
    name, birthday = args
    record = contacts.find(name)
    record.add_birthday(birthday)
    if record.birthday == birthday:
        return "Contact updated."
    return "Contact is not updated"

@input_error
def show_birthday(args: tuple, book:  AddressBook) -> str:
    """
    Returns a string representation of all contacts.
    
    Parameters:
    - args (tuple): A tuple containing the name of the contact.
    - book (AddressBook): The address book with contacts.
    
    Returns:
    - str: A string representation of the contact birthday.
    """
    name, *_ = args
    return book.find(name).birthday

@input_error
def birthdays(book:  AddressBook) -> str:
    """
    Returns a string representation of all contacts.
    
    Parameters:
    - args (tuple): A tuple containing the name of the contact.
    - book (AddressBook): The address book with contacts.
    
    Returns:
    - str: A string representation of the upcoming contacts birthdays.
    """
    return book.get_upcoming_birthdays()


def main():
    """
    The main function of the assistant bot. It initializes the contacts dictionary and processes user commands.
    """
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command.lower() in ["close", "exit", "quit", "q"]:
            print("Good bye!")
            save_data(book)
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(book))
        else:
            print("Invalid command.")
            
            
# add block with tests for the functions
def test_functions():
    today = datetime.today().date()
    valid_birthday = (today + timedelta(days=3)).strftime(DATE_FORMAT)
    contacts = AddressBook()
    assert add_contact(("John", "1234562345"), contacts) == "Contact added."
    assert add_contact(("Alice", "9876545432"), contacts) == "Contact added."
    assert add_contact(("John", "0987657345"), contacts) == "Contact added."
    assert change_contact(("John", "1234562345", "0987657345"), contacts) == "Contact updated."
    assert change_contact(("Bob", "1234562345", "1234562345"), contacts) == "Contact not found."
    assert "0987657345" in show_phone(("John",), contacts)
    assert "9876545432" in show_phone(("Alice",), contacts)
    assert show_phone(("Bob",), contacts) == []
    assert show_all(contacts) == {'John': ['0987657345'], 'Alice': ['9876545432']}
    assert add_contact(("John"), contacts) == "Give me your name and phone please."
    assert change_contact(("098765"), contacts) == "Give me your name and phone please."
    assert add_birthday(("John", valid_birthday), contacts), "Contact updated."
    assert add_birthday(("John", '23-01-1985'), contacts), "Contact is not updated"
    assert show_birthday(("John",), contacts), valid_birthday
    assert birthdays(contacts), f"{"John": valid_birthday}"
    print("All function tests passed.")
    
def test_main():
    # Define test data as a list of tuples, where each tuple contains a user input and the expected output.
    test_data = [
        ("hello", "How can I help you?"),  # Test greeting
        ("add John 1234563546", "Contact added."),  # Test adding a new contact
        ("phone John", "['1234563546']"),  # Test retrieving a contact's phone number
        ("change John 1234563546 0987652345", "Contact updated."),  # Test changing a contact's phone number
        ("phone John", "['0987652345']"),  # Test retrieving the updated phone number
        ("all", "{'John': ['0987652345']}"),  # Test displaying all contacts
        ("wrong_command", "Invalid command."),  # Wrong command
        ("close", "Good bye!")  # Test closing the application
    ]
    # Patch the input function to simulate user input based on the test data.
    with patch("builtins.input", side_effect=[i[0] for i in test_data]):
        # Patch sys.stdout to capture the output of the main function.
        with patch("sys.stdout", new_callable=StringIO) as fake_out:
            main()  # Call the main function to process the simulated user input.
            # Assert that the captured output matches the expected output defined in the test data.
            expected_output = f"Welcome to the assistant bot!\n{'\n'.join([i[1] for i in test_data])}".strip().split('\n')
            actual_output = fake_out.getvalue().strip().split('\n')
            assert actual_output == expected_output, \
                f"Test main function is failed output \n'{actual_output}' is not equal to expected \n'{expected_output}'"
    print("The main function tests passed.")
            
# Uncomment the line below to run the tests
# test_functions()
# test_main()
            
if __name__ == "__main__":
    main()

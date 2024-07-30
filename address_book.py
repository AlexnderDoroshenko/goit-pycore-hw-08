# AddressBook realization module
from collections import UserDict
from datetime import datetime, timedelta
from typing import List


DATE_FORMAT = "%d.%m.%Y"
DAYS_IN_WEEK = 7
WEEKEND_DAYS = [5, 6]


class Field:
    """
    A base class representing a generic field with a value.
    """
    def __init__(self, value: str) -> None:
        """
        Initializes the Field with a given value.
        
        :param value: The value of the field as a string.
        """
        self.value = value

    def __str__(self):
        """
        Returns a string representation of the field's value.
        
        :return: String representation of the field's value.
        """
        return str(self.value)


class Name(Field):
    """
    Represents the name field of a contact. Inherits from Field.
    """
    pass  # Currently, no additional implementation is needed.


class Phone(Field):
    """
    Represents the phone number field of a contact. Inherits from Field.
    """
    pass  # Currently, no additional implementation is needed.


class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, DATE_FORMAT)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        

class Record:
    """
    Represents a contact record with a name and a list of phone numbers.
    """
    def __init__(self, name: str, birthday: Birthday = None) -> None:
        """
        Initializes the Record with a name and an empty list of phone numbers.
        
        :param name: The name of the contact as a string.
        :param birthday: (Optional) The name of the contact as a string.
        """
        self.name: Name = Name(name)
        self.phones: list[Phone] = []
        self.birthday: Birthday = birthday
        
    def is_phone_valid(self, phone: str) -> bool:
        """
        Checks if the given phone number is valid.
        A valid phone number is 10 digits long and numeric.
        
        :param phone: The phone number to check.
        :return: True if the phone number is valid, otherwise False.
        """
        return len(phone) == 10 and phone.isnumeric()
            
    def add_phone(self, phone: str) -> None:
        """
        Adds a phone number to the contact if it is valid.
        
        :param phone: The phone number to add.
        """
        if self.is_phone_valid(phone):
            self.phones.append(Phone(phone))
        if self.phones:
            return "The phone is added successfully"
        return f"Phone {phone} was not added, it should be 10 digits long and numeric"
        
    def remove_phone(self, phone: str) -> None:
        """
        Removes a phone number from the contact if it exists.
        
        :param phone: The phone number to remove.
        """
        for index, p in enumerate(self.phones):
            if p.value == phone:
                del self.phones[index]
                break
                
    def edit_phone(self, old_value: str, new_value: str) -> None:
        """
        Edits an existing phone number with a new value if the new phone number is valid.
        
        :param old_value: The current phone number to be replaced.
        :param new_value: The new phone number to set.
        """
        if self.is_phone_valid(new_value):
            for index, p in enumerate(self.phones):
                if p.value == old_value:
                    self.phones[index] = Phone(new_value)
                    break
                
    def find_phone(self, phone: str) -> Phone:
        """
        Finds a phone number in the contact.
        
        :param phone: The phone number to find.
        :return: The Phone object if found, otherwise None.
        """
        for p in self.phones:
            if p.value == phone:
                return p
        return None
    
    def add_birthday(self, birthday: Birthday) -> str:
        try:
            self.birthday = Birthday(birthday)
            return "Birthday is added successfully"
        except ValueError as err:
            return f"{err}"
    
    def __str__(self) -> str:
        """
        Returns a string representation of the contact, including name and phone numbers.
        
        :return: String representation of the contact.
        """
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"


class AddressBook(UserDict):
    """
    Represents an address book that stores multiple contact records.
    Inherits from contactDict to utilize dictionary-like functionality.
    """
    def add_record(self, record: Record) -> None:
        """
        Adds a record to the address book.
        
        :param record: The Record to add to the address book.
        """
        self.data.update({record.name.value: record})
        
    def find(self, name: str) -> Record:
        """
        Finds a record by the contact's name.
        
        :param name: The name of the contact to find.
        :return: The Record associated with the given name, or None if not found.
        """
        return self.data.get(name)
    
    def delete(self, name: str) -> None:
        """
        Deletes a record by the contact's name.
        
        :param name: The name of the contact to delete.
        """
        if name in self.data:
            self.data.pop(name)
            
    def get_upcoming_birthdays(self) -> List[dict]:
        """
        Method returns contacts list with birthdays in the next 7 days.
        
        Args:
        contacts (List[dict]): List of contacts with birthdays in string format ('YYYY.MM.DD')
        
        Returns:
        List[dict]: List of contacts with upcoming birthday greetings.
        
        The Method iterates through each contact, parsing their birthday and calculating if their
        birthday occurs within the next 7 days from today. If a birthday falls on a weekend,
        the congratulation date is adjusted to the next Monday.
        """
        today = datetime.today().date()
        upcoming_birthdays = []

        for contact in self.data:
            # Parse the birthday string into a date object
            contact = self.data.get(contact)
            if not contact.birthday:
                continue
            b_value = contact.birthday.value
            if not isinstance(b_value, datetime):
                b_value = datetime.strptime(self.data.get(contact).birthday.value, DATE_FORMAT)
            # Adjust the year to the current year for comparison
            birthday_this_year = b_value.date().replace(year=today.year)

            # If the birthday has already passed this year, consider next year's birthday
            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)

            # Calculate the number of days until the birthday
            delta_days = (birthday_this_year - today).days

            # Skip if the birthday is not within the next 7 days
            if not 0 <= delta_days <= 7:
                continue

            # Adjust the congratulation date if it falls on a weekend
            congratulation_date = self.adjust_for_weekend(birthday_this_year)

            # Add the contact to the list with the adjusted congratulation date
            upcoming_birthdays.append({
                "name": contact.name.value,
                "congratulation_date": congratulation_date.strftime(DATE_FORMAT)
            })

        return upcoming_birthdays

    def adjust_for_weekend(self, date: datetime.date) -> datetime.date:
        """
        Adjusts the date to the next Monday if it falls on a weekend.
        
        Args:
        date (datetime.date): The date to adjust if necessary.
        
        Returns:
        datetime.date: The adjusted date.
        
        This function checks if the given date falls on a weekend (Saturday or Sunday) and
        adjusts it to the following Monday to ensure that birthday greetings are not sent
        over the weekend.
        """
        if date.weekday() in WEEKEND_DAYS:
            # Calculate the adjustment needed to move the date to the next Monday
            return date + timedelta(days=(DAYS_IN_WEEK - date.weekday()))
        return date
            
            
# test part        
    
def test_field():
    field = Field("Test Value")
    assert str(field) == "Test Value"
    print("Field class test passed")

def test_record():
    record = Record("John Doe")
    assert str(record) == "Contact name: John Doe, phones: "
    record.add_phone("1234567890")
    assert "1234567890" in [p.value for p in record.phones]
    record.remove_phone("1234567890")
    assert "1234567890" not in [p.value for p in record.phones]
    record.add_phone("1234567890")
    record.edit_phone("1234567890", "0987654321")
    assert "0987654321" in [p.value for p in record.phones]
    assert not record.find_phone("1234567890")
    assert record.find_phone("0987654321").value == "0987654321"
    print("Record class test passed")

def test_address_book():
    address_book = AddressBook()
    record = Record("Jane Doe")
    address_book.add_record(record)
    assert address_book.find("Jane Doe") == record
    address_book.delete("Jane Doe")
    assert not address_book.find("Jane Doe")
    today = datetime.today().date()
    test_data = [
        # Various test cases with birthdays on different days relative to today
        {"name": "Johny Duke", "birthday": "23-01-1985"},  # Wrong format
        {"name": "John Doe", "birthday": (today - timedelta(days=1)).strftime(DATE_FORMAT)},  # Yesterday
        {"name": "Jane Smith", "birthday": today.strftime(DATE_FORMAT)},  # Today
        {"name": "Alice Wonderland", "birthday": (today + timedelta(days=7)).strftime(DATE_FORMAT)},  # In 7 days
        {"name": "Bob Builder", "birthday": (today + timedelta(days=3)).strftime(DATE_FORMAT)},  # In 3 days
        {"name": "Charlie Brown", "birthday": (today + timedelta(days=8)).strftime(DATE_FORMAT)},  # In 8 days, just outside the range
        {"name": "Diana Prince", "birthday": (today + timedelta(days=10)).strftime(DATE_FORMAT)},  # In 10 days, well outside the range
        {"name": "George Jungle", "birthday": (today + timedelta((5 - today.weekday()) % 7)).strftime(DATE_FORMAT)},  # Next Saturday
        {"name": "Helen Troy", "birthday": (today + timedelta((6 - today.weekday()) % 7)).strftime(DATE_FORMAT)}  # Next Sunday
    ]
    wrong_rec_birthday = Record(test_data[0].get("name", ""))

    err =  wrong_rec_birthday.add_birthday(test_data[0].get("birthday", ""))
    exp_err = 'Invalid date format. Use DD.MM.YYYY'
    exp_success = 'Birthday is added successfully'
    assert str(err) == str(exp_err), f"Expected error '{exp_err}' not match wit actual '{er}'"
    
    for record in test_data[1:]:
        rec = Record(record.get("name", ""))
        act_success = rec.add_birthday(record.get("birthday", ""))
        assert act_success == exp_success, f"Act: '{act_success}', Exp: '{exp_success}'"
        address_book.add_record(rec)
    results = address_book.get_upcoming_birthdays()
    print(results)

    # Expected names of users with upcoming birthdays within the next 7 days
    expected_names = ["Jane Smith", "Alice Wonderland", "Bob Builder", "George Jungle", "Helen Troy"]
    for expected_name in expected_names:
        # Check if each expected user is in the results
        found = any(user["name"] == expected_name for user in results)
        assert found, f"{expected_name} should be in the results: {results}."
        print(f"Test passed for user '{expected_name}'")

    for user in results:
        # Verify that the congratulation date does not fall on a weekend
        congratulation_date = datetime.strptime(user["congratulation_date"], DATE_FORMAT).date()
        assert congratulation_date.weekday() not in WEEKEND_DAYS, f"{user['name']}'s congratulation date falls on a weekend."
        print(f"Test falls on a weekend passed for user '{user['name']}'")
    
    print("AddressBook class test passed")
    
# Uncomment code to run tests
# test_address_book()
# test_field()
# test_record()

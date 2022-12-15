import pickle
import os
import re
from datetime import datetime
from pyCliAddressBook.autocompletion import Invoker
import pyCliAddressBook.validator as validator
# from autocompletion import Invoker
# import validator as validator

from dateutil import parser
from rich.console import Console
from rich.table import Table
from abc import ABC, abstractmethod
from collections import UserDict

CLI_UI = '''
CMD HELPER: 1.Add 2.View all 3.Search 4.Find 5.Sort 6.Update 7.Delete 8.Reset 9.File sort 10. Help 11.Exit
'''

console = Console()


class Application_Dict(ABC, UserDict):
    @abstractmethod
    def __init__(self, dict_application: dict):
        ...

    @abstractmethod
    def add_record(self):
        ...

    @abstractmethod
    def update_record(self, record):
        ...

    @abstractmethod
    def delete_record(self, record):
        ...

    @staticmethod
    @abstractmethod
    def print_in_table():
        ...

    @abstractmethod
    def get_records_dy_key(self):
        ...

    @abstractmethod
    def find_records(self):
        ...


class NoteBook(Application_Dict):
    """
    This class maneges elements of diary.
    """

    def __init__(self, dict_application: dict):
        UserDict.__init__(self)
        if dict_application.get("notes"):
            self.data = dict_application.get("notes")

    def add_record(self):
        value, keyWords = self.get_note()
        note = Note(value, keyWords)
        self.data[note.date] = note

    def update_record(self, record):

        record.print_in_table()
        print("Will be changed")
        value, keyWords = self.get_note()
        self.data[record.date].keyWords = keyWords or record.keyWords
        self.data[record.date].value = value or record.value

    def delete_record(self, record):

        record.print_in_table()
        print("Was deleted")
        self.data.pop(record.date)

    def get_records_dy_key(self):

        keyword = input("Enter the key word to note: ")
        note_list_keyword = []
        for note in self.data.values():
            keywords = note.get_keywords()
            if keyword in keywords:
                note_list_keyword.append(note)

            if note_list_keyword:
                return note_list_keyword

        return None

    def find_records(self):

        keyword = input("What are you looking for?: ")
        note_list = []
        for note in self.data.values():
            keywords = note.get_keywords()
            if keyword.lower() in str(note).lower():
                note_list.append(note)

        return note_list

    @staticmethod
    def get_note():

        userInput = input("Note (keywords as #words#): ")
        keywords = re.findall(r"\#.+\#", userInput)
        value = userInput.strip()
        return value, [keyword.replace("#", "").strip() for keyword in keywords]

    @staticmethod
    def print_in_table(notes: list, table_name: str):

        table = Table(show_header=True,
                      header_style="bold blue", show_lines=True)
        table.add_column(table_name, style="dim",
                         width=5, justify="center")
        table.add_column("DATE", min_width=12, justify="center")
        table.add_column("VALUE", min_width=50, justify="center")

        for idx, note in enumerate(notes, start=1):
            table.add_row(str(
                idx), f'[cyan]{datetime.fromisoformat(note.date).strftime("%m/%d/%Y, %H:%M:%S")}[/cyan]',
                f'[cyan]{note.value}[/cyan]')

        console.print(table)


class AddressBook(Application_Dict):
    """
    This class maneges elements of address book.
    """

    def __init__(self, dict_application: dict):
        UserDict.__init__(self)
        if dict_application.get("persons"):
            self.data = dict_application.get("persons")

    def add_record(self):
        name, _address, _phone, _email, _birthday = self.get_details()
        address = _address or "NULL"
        phone = _phone or "NULL"
        email = _email or "NULL"
        birthday = _birthday or "1900-01-01"
        if name not in self.data:
            self.data[name] = Person(name, address, phone, email, birthday)
        else:
            print("Contact already present")

    def update_record(self, record):

        record.print_tab()
        print("Found. Enter new details and keep empty fields if no any changes")
        _name, _address, _phone, _email, _birthday = self.get_details()
        name = _name or record.name
        address = _address or record.address
        phone = _phone or record.phone
        email = _email or record.email
        birthday = _birthday or str(record.birthday)
        record.__init__(
            name, address, phone, email, birthday)

    def delete_record(self, record):

        record.print_tab()
        print("Was deleted")
        self.data.pop(record.name)

    def get_records_dy_key(self):
        name = input("Enter the name: ")
        if name in self.data:
            return [self.data[name]]

        return None

    def find_records(self):

        obj = input('What do you want to find? ')
        records = []
        for contact in self.data.values():
            if obj.lower() in str(contact).lower():
                records.append(contact)

        return records

    @staticmethod
    def get_details():
        """
        Getting info for fields in address book from user
        :return: tuple
            fields of address book: name, address, phone, email, birthday
        """
        name = validator.name_validator()
        address = input("Address: ")
        phone = validator.phone_check()
        email = validator.email_check()
        birthday = input("Birthday [format yyyy-mm-dd]: ")
        return name, address, phone, email, birthday

    @staticmethod
    def print_in_table(persons: list, table_name: str):

        table = Table(show_header=True,
                      header_style="bold blue", show_lines=True)
        table.add_column(table_name, style="dim", width=5, justify="center")
        table.add_column("NAME", min_width=12, justify="center")
        table.add_column("ADDRESS", min_width=10, justify="center")
        table.add_column("PHONE", min_width=18, justify="center")
        table.add_column("EMAIL", min_width=18, justify="center")
        table.add_column("BIRTHDAY", min_width=15, justify="center")
        for idx, person in enumerate(persons, start=1):
            _ = person.__dict__
            table.add_row(
                str(idx), f'[cyan]{_["name"]}[/cyan]', f'[cyan]{_["address"]}[/cyan]', f'[cyan]{_["phone"]}[/cyan]',
                f'[cyan]{_["email"]}[/cyan]', f'[cyan]{_["birthday"].date()}[/cyan]'
            )
        console.print(table)


class Application:
    """
    This class maneges components of the application.
    """

    def __init__(self, database):

        self.database = database

        dict_application = {}
        if not os.path.exists(self.database):
            file_pointer = open(self.database, 'wb')
            pickle.dump({}, file_pointer)
            file_pointer.close()
        else:
            with open(self.database, 'rb') as Application:
                dict_application = pickle.load(Application)

        self.addressBook = AddressBook(dict_application)
        self.noteBook = NoteBook(dict_application)
        self.components = {'addressBook': self.addressBook,
                           'noteBook': self.noteBook}

    def __del__(self):
        with open(self.database, 'wb') as db:
            pickle.dump({"persons": self.addressBook.data,
                         "notes": self.noteBook.data}, db)

    def __str__(self):
        return CLI_UI


class Person:
    """
    A class is used to create fields to address book.
    ________________________________________________

    Attributes
    __________
    name : str
        name of the contact
    address : str
        address of the contact
    phone : str
        phone of the contact
    email : str
        email of the contact
    birthday : str
        birthday of the contact

    Methods
    _______
    print_tab
        used to show info about the contact as a table

    """

    def __init__(self, name: str = None, address: str = None, phone: str = None, email: str = None,
                 birthday: str = None):
        """
        Creating fields of the address book
        :param name: str
            name of the contact
        :param address: str
            address of the contact
        :param phone: str
            phone of the contact
        :param email: str
            email of the contact
        :param birthday: str
            birthday of the contact
        """
        self.name = name
        self.address = address
        self.phone = phone
        self.email = email
        self.birthday = parser.parse(birthday)

    def __getitem__(self, i):
        return self.__dict__[i]

    def __str__(self):
        """
        Returning all data of the contact as a string
        :return: str
        """
        return f"{self.name}, {self.address}, {self.phone}, {self.email}, {self.birthday.date()}"

    def print_tab(self):
        """
        Printing data of the contact as a formatted table
        :return: None
        """
        table = Table(show_header=False,
                      header_style="bold blue", show_lines=True)
        table.add_row(
            f'[cyan]{self.name}[/cyan]', f'[cyan]{self.address}[/cyan]', f'[cyan]{self.phone}[/cyan]',
            f'[cyan]{self.email}[/cyan]', f'[cyan]{self.birthday.date()}[/cyan]'
        )
        console.print(table)


class Note:
    """
    A class is used to create fields to diary.
    ________________________________________________

    Attributes
    __________
    value : str
        text of the note
    keyWords : list
        a keywords list of the note
    date : datetime
        date of note creating

    Methods
    _______
    print_in_table
        used to show info about the note as a table

    """

    def __init__(self, value: str, keyWords: list) -> None:
        """
        Creating fields of the diary
        :param value: str
            text of the note
        :param keyWords: list
            a keywords list of the note
        """
        self.date = datetime.now().isoformat()
        self.value = value
        self.keyWords = keyWords

    def get_keywords(self):
        """
        Joining all tags of the note in string
        :return: str
            string of keywords
        """
        return ", ".join(self.keyWords)

    def print_in_table(self):
        """
        Printing notes as a formatted table
        :return: None
        """
        table = Table(show_header=False,
                      header_style="bold blue", show_lines=True)
        table.add_row(
            f'[cyan]{datetime.fromisoformat(self.date).strftime("%m/%d/%Y, %H:%M:%S")}[/cyan]',
            f'[cyan]{self.value}[/cyan]')
        console.print(table)

    def __str__(self):
        return "{:<25} {}".format(datetime.fromisoformat(self.date).strftime("%m/%d/%Y, %H:%M:%S"), self.value)


def cli():
    """
    Comparing inputted command with existing ones
    and performing correspondent command
    :return: None
    """
    app = Application('contacts.data')
    invoker = Invoker(app)
    while True:
        print(app)
        command = invoker.choose_command()
        continuation = command.execute()
        if not continuation:
            break


if __name__ == '__main__':
    cli()

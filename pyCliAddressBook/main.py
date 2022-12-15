import re
from datetime import datetime
from abc import ABC, abstractmethod

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_

from models import Note, KeyWord, Person, ContactInformation, ContactInformationTypes
# from pyCliAddressBook.autocompletion import Invoker
from autocompletion import Invoker
# import pyCliAddressBook.validator as validator
import validator as validator

engine = create_engine("sqlite:///../personal_assistant.db")
Session = sessionmaker(bind=engine)
session = Session()

CLI_UI = '''
CMD HELPER: 1.Add 2.View all 3.Search 4.Find 5.Sort 6.Update 7.Delete 8.Reset 9.File sort 10. Help 11.Exit
'''


class ApplicationDict(ABC):
    @abstractmethod
    def __init__(self):
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

    @abstractmethod
    def get_records_dy_key(self):
        ...

    @abstractmethod
    def get_all_records(self):
        ...

    @abstractmethod
    def find_records(self):
        ...


class AddressBook:
    """
    This class maneges elements of address book.
    """

    def __init__(self):
        self.personModel = Person
        self.ContactInformationModel = ContactInformation

    def add_record(self):
        name, _birthday, contact_information_list = self.get_details()
        birthday = _birthday or "1900-01-01"

        person = self.get_records_dy_key(name)
        if not person:

            contact_information = []
            for contact in contact_information_list:
                contact_information.append(self.ContactInformationModel(
                    contactInformationType=contact[0], description=contact[1]))

            person = self.personModel(name=name, birthday=datetime.strptime(birthday, '%Y-%m-%d'))

            person.contactInformation = contact_information

            session.add(person)
            session.commit()

        else:
            print("Contact already present")

    def update_record(self, record):

        _name, _birthday, contact_information_list = self.get_details()
        name = _name or record.name
        birthday = _birthday or record.birthday.strftime('%Y-%m-%d')

        record.name = name
        record.birthday = datetime.strptime(birthday, '%Y-%m-%d')

        record.contactInformation.extend([self.ContactInformationModel(
            contactInformationType=contact[0], description=contact[1]) for contact in contact_information_list])

        session.commit()

    def delete_record(self, record):

        session.delete(record)
        session.commit()

    def get_records_dy_key(self, key=None):
        if not key:
            key = input("Enter the name: ")

        return session.query(self.personModel).filter(self.personModel.name == key).all()

    def get_all_records(self):
        return session.query(self.personModel).all()

    def find_records(self):

        word = input("What are you looking for?: ")
        return session.query(self.personModel).join(self.ContactInformationModel).filter(
            or_(self.personModel.name.like(f"%{word}%"),
                self.ContactInformationModel.description.like(f"%{word}%"))).all()

    @staticmethod
    def get_details():
        """
        Getting info for fields in address book from user
        :return: tuple
        fields of address book: name, address, phone, email, birthday
        """
        name = validator.name_validator()
        birthday = input("Birthday [format yyyy-mm-dd]: ")
        contact_nformation_list = []
        for index, value in ContactInformationTypes.items():
            if value.get("validator"):
                contact_nformation = value.get("validator")()
            else:
                contact_nformation = input(f"{value.get('name')}: ")
            if contact_nformation:
                contact_nformation_list.append((index, contact_nformation))
        return name, birthday, contact_nformation_list


class NoteBook:
    """
    This class maneges elements of diary.
    """

    def __init__(self):
        self.noteModel = Note
        self.KeyWordModel = KeyWord

    def add_record(self):
        value, key_words = self.get_details()

        key_words = [KeyWord(name=key_word) for key_word in key_words]

        note = Note(description=value)
        note.keyWords = key_words

        session.add(note)
        session.commit()

    def update_record(self, record):
        value, key_words = self.get_details()

        key_words = [KeyWord(name=key_word) for key_word in key_words]

        record.description = value or record.value
        record.keyWords.extend(key_words)

        session.commit()

    def delete_record(self, record):
        session.delete(record)
        session.commit()

    def get_records_dy_key(self, key=None):
        if not key:
            key = input("Enter the key word to note: ")
        return session.query(self.noteModel).join(self.KeyWordModel).filter(self.KeyWordModel.name == key).all()

    def get_all_records(self):
        return session.query(self.noteModel).all()

    def find_records(self):
        word = input("What are you looking for?: ")
        return session.query(self.noteModel).filter(self.noteModel.description.like(f"%{word}%")).all()

    @staticmethod
    def get_details():
        user_input = input("Note (keywords as #key_word): ")
        key_words = re.findall(r"#(\w+)", user_input)
        value = user_input.strip().replace("#", "").replace("_", " ")
        return value, [key_word.strip() for key_word in key_words]


class Application:
    """
    This class maneges components of the application.
    """

    def __init__(self):
        self.addressBook = AddressBook()
        self.noteBook = NoteBook()
        self.components = {'addressBook': self.addressBook,
                           'noteBook': self.noteBook}

    def __str__(self):
        return CLI_UI


def cli():
    """
    Comparing inputted command with existing ones
    and performing correspondent command
    :return: None
    """
    app = Application()
    invoker = Invoker(app)
    print_cmd_help = True
    while True:
        if print_cmd_help:
            print(app)
            print_cmd_help = False
        else:
            print("------------------------------------------")
        command = invoker.choose_command()
        continuation = command.execute()
        if not continuation:
            break


if __name__ == '__main__':
    cli()

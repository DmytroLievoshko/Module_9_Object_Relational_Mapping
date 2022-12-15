from datetime import datetime
# import pyCliAddressBook.validator as validator
import validator as validator

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey, Table
from sqlalchemy.sql.sqltypes import DateTime

Base = declarative_base()

ContactInformationTypes = {1: {"name": "Address"},
                           2: {"name": "Phone", "validator": validator.phone_check},
                           3: {"name": "Email", "validator": validator.email_check}}


class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True)
    description = Column(String(150), nullable=False)
    created = Column(DateTime, default=datetime.now())
    keyWords = relationship("KeyWord", cascade="all, delete", backref="note")

    def __str__(self):
        return f"{self.description} --created: {self.created} --keywords: {', '.join([keyWord.name for keyWord in self.keyWords])}"


class KeyWord(Base):
    __tablename__ = "keyWords"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    note_id = Column(Integer, ForeignKey(Note.id, ondelete="CASCADE"), nullable=False)


class Person(Base):
    __tablename__ = "persons"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    birthday = Column(DateTime)
    contactInformation = relationship("ContactInformation", cascade="all, delete", backref="person")

    def __str__(self):
        str_erson = f"{self.name} birthday: {self.birthday.strftime('%d-%m-%Y')}"
        for Contact_information in self.contactInformation:
            str_erson += f"\n{Contact_information}"
        return str_erson


class ContactInformation(Base):
    __tablename__ = "contactInformation"
    id = Column(Integer, primary_key=True)
    contactInformationType = Column(Integer, nullable=False)
    description = Column(String(150), nullable=False)
    person_id = Column(Integer, ForeignKey(Person.id, ondelete="CASCADE"), nullable=False)

    def __str__(self):
        return f"{ContactInformationTypes.get(self.contactInformationType).get('name')} {self.description}"

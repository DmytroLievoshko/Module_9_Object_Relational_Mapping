"""
This module includes functions which are used to validate data inputting a user
"""
from email.policy import default
import phonenumbers
import re


def name_validator():
    """
    Validating inputted name that it consists of only letters
    :return: str
        inputted name
    """
    while True:
        name = input("Name: ")
        if isinstance(name, str) and name.isalpha() or not name:
            return name
        else:
            print("Please enter a valid Name")


def email_check():
    """
    Validating inputted email on pattern with module re
    :return: str
        inputted email
    """
    while True:
        email = input("Email: ")
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if (re.fullmatch(pattern, email)) or not email:
            return email
        else:
            print("Invalid Email")


def phone_check():
    """
    Validating inputted phone on accordance to international format with module phonenumbers
    :return: str
        formatted phone number
    """
    while True:
        phone = input("Phone: ")
        if not phone:
            break
        iso_code = input("ISO country code like UA, GB, PL etc.: ").upper()

        pattern = phonenumbers.parse(phone, iso_code)
        if not phone or phonenumbers.is_valid_number(pattern):
            international_number = phonenumbers.format_number(
                pattern, phonenumbers.PhoneNumberFormat.E164)
            print(international_number)
            return international_number
        else:
            print("Invalid phone number")


# (self.persons[name].__dict__.values())
# (self.persons[name].__dict__["birthday"])

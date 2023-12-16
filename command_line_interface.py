from cli_oop import AddressBook, Record
from csv import DictReader, DictWriter
import re

FILE = "contact.csv"
book = AddressBook()


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Please provide a name and data."

    return inner


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


def load_data():
    with open(FILE, "r") as f:
        dict_reader = DictReader(f, delimiter=";")
        contact_data = list(dict_reader)

    for person in contact_data:
        for key, value in person.items():
            if key == "name":
                record = Record(value)
            elif key == "phone":
                if len(value) > 20:
                    for v in value.split(","):
                        record.add_phone(v.strip())
                else:
                    record.add_phone(value)
            elif key == "birthday":
                if person[key]:
                    record.add_birthday(value)
                else:
                    continue
            else:
                continue
            book.add_record(record)


def write_to_file(book):
    field_names = ["name", "phone", "birthday"]
    users_list = []
    for person in book.data:
        if book.data[person].birthday:
            data = {
                "name": book.data[person].name.value,
                "phone": ", ".join(p.value for p in book.data[person].phones),
                "birthday": book.data[person].birthday.value,
            }
        else:
            data = {
                "name": book.data[person].name.value,
                "phone": ", ".join(p.value for p in book.data[person].phones),
            }
        users_list.append(data)
    with open(FILE, "w") as csvfile:
        writer = DictWriter(csvfile, fieldnames=field_names, delimiter=";")
        writer.writeheader()
        writer.writerows(users_list)


@input_error
def add_contact(args, book):
    name = " ".join(re.findall("[a-zA-Z]+", str(args)))
    phone = " ".join(re.findall("\d{10}", str(args)))
    if name not in book.data:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
    else:
        record = book.find(name)
        record.add_phone(phone)
        book.add_record(record)
    return f"Contact {name} with phone number: {phone} added."


@input_error
def show_phone(args, book):
    name = " ".join(args)
    if name in book.data:
        result = book.find(name)
        message = "{:<25}{:<40}\n".format("Name", "Telephone Number")
        message += "{:.<25}{:<40}\n".format(
            (result.name.value), ("; ".join(p.value for p in result.phones))
        )
        return message
    else:
        return f"No phone number found for {result.name.value}."


@input_error
def edit_phone(args, book):
    try:
        name = " ".join(re.findall("[a-zA-Z]+", str(args)))
        old_number, new_number = re.findall("\d{10}", str(args))
    except ValueError:
        return "Input shoud be in format NAME, OLD NUMBER, NEW NUMBER!"
    if name in book.data:
        record = book.find(name)
        record.edit_phone(old_number, new_number)
        book.add_record(record)
        return f"For contact: {name} telephone number: {old_number} changed to: {new_number}"
    else:
        return f"No contact data with {name} found"


@input_error
def change_phone(args, book):
    try:
        name = " ".join(re.findall("[a-zA-Z]+", str(args)))
        new_number = " ".join(re.findall("\d{10}", str(args)))
    except ValueError:
        return "Input shoud be in format NAME, NEW NUMBER!"
    if name in book.data:
        record = book.find(name)
        for p in record.phones:
            record.remove_phone(p.value)
        old_number = " ".join(p.value for p in record.phones)
        if len(old_number) == 10:
            record.edit_phone(old_number, new_number)
        else:
            record.add_phone(new_number)
        book.add_record(record)
        return f"For contact: {name} has telephone number: {new_number}"


def show_all(book):
    if not book:
        return "No contacts found."
    message = "Hier ist the full list: \n"
    for name, record in book.data.items():
        message += str(record) + "\n"
    return message


@input_error
def add_birthday(args, book):
    try:
        name = " ".join(re.findall("[a-zA-Z]+", str(args)))
        birthday = " ".join(re.findall("\d{2}.\d{2}.\d{4}", str(args)))
    except ValueError:
        return "Input shoud be in format NAME, BIRTHDAY!"
    if name in book.data:
        record = book.find(name)
        record.add_birthday(birthday)
    else:
        return f"No contact data with {name} found"
    return f"For {name} birthday at {birthday} added."


@input_error
def show_birthday(args, book):
    try:
        name = " ".join(re.findall("[a-zA-Z]+", str(args)))
    except ValueError:
        return "Please enter a name!"
    if name in book.data:
        record = book.find(name)
        try:
            birthday = record.show_birthday()
        except ValueError:
            return f"No birthday for {name} saved"
        return f"{name} has birthday at {birthday.value}"
    else:
        return f"No contact data with {name} found"


def birthdays(book):
    return book.get_birthdays_per_week()


def main():
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            write_to_file(book)
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "edit-phone":
            print(edit_phone(args, book))
        elif command == "change":
            print(change_phone(args, book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(book))
        elif command == "all":
            print(show_all(book))
        else:
            print(
                """Invalid command.
                Available commands:
                >>> hello: Get a greeting from the bot.
                >>> add [name] [phone]: Add a new contact
                    with a name and phone number.
                >>> phone [name]: Show the phone number
                    for the specified contact.
                >>> change [name] [new phone]: Change the
                    phone number for the specified contact.
                >>> add-birthday [name] [birthday]: Add a birthday
                    date for the specified contact.
                >>> show-birthday [name]: Show the birthday
                    for the specified contact.
                >>> birthdays: Show upcoming birthdays for the next week.
                >>> all: Show all contacts in the address book.
                >>> close or exit: Close the program.
                """
            )


if __name__ == "__main__":
    load_data()
    main()
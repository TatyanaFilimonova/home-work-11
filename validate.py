from datetime import datetime
from datetime import date
import re


def clean_phone_str(phone):
    phone = (
        phone.replace("-", "")
             .replace("{", "")
             .replace("}", "")
             .replace("[", "")
             .replace("]", "")
             .replace("(", "")
             .replace(")", "")
             .replace(".", "")
             .replace(" ", "")
    )
    return phone


def validate_contact_data(request, form_dict):
    for key in form_dict.keys():
        if re.search("^Hint", request.form.get(key)):
            form_dict[key]['value'] = ""
        else:
            form_dict[key]['value'] = request.form.get(key)
        res_tuple = form_dict[key]['checker'](form_dict[key]['value'])
        form_dict[key]['valid'] = res_tuple[0]
        form_dict[key]['error_message'] = res_tuple[1]
        form_dict[key]['value'] = res_tuple[2]
    return form_dict


def name_checker(name):
    error_message = ""
    valid = True
    if len(name) > 50:
        error_message = "Max len of Name is 50 char"
        valid = False
    elif name == '':
        error_message = "Name have to be at least one symbol "
        valid = False
    return valid, error_message, name


def birthday_checker(birthday):
    error_message = ""
    valid = True
    if birthday != "":
        if re.search('\d{4}\-\d{2}\-\d{2}', birthday) is None:
            error_message = f"Get from form {birthday} type {type(birthday)}"
            valid = False
        else:
            birthday = datetime.strptime(birthday, '%Y-%m-%d')
    else:
        birthday = None
    return valid, error_message, birthday


def phone_checker(phones):
    error_message = ""
    valid = True
    if phones!='':
        phones = clean_phone_str(phones)
        for phone in phones.split(","):
            if re.search('\+{0,1}\d{9,13}', phone.strip()) is None:
                error_message = """Phone should have format: '[+] XXXXXXXXXXXX' (9-12 digits), phones separated by ','"""
                valid = False
    return valid, error_message, phones


def zip_checker(zip):
    error_message = ""
    valid = True
    if len(zip) > 10:
        error_message = "Max len of ZIP is 10 char"
        valid = False
    return valid, error_message, zip


def country_checker(country):
    error_message = ""
    valid = True
    if len(country) > 50:
        error_message = "Max len of Country is 50 char"
        valid = False
    return valid, error_message, country


def region_checker(region_):
    error_message = ""
    valid = True
    if len(region_) > 50:
        error_message = "Max len of Region is 50 char"
        valid = False
    return valid, error_message, region_


def city_checker(city):
    error_message = ""
    valid = True
    if len(city) > 40:
        error_message = "Max len of City is 40 char"
        valid = False
    return valid, error_message, city


def street_checker(street):
    error_message = ""
    valid = True
    if len(street) > 50:
        error_message = "Max len of Street is 50 char"
        valid = False
    return valid, error_message, street


def house_checker(house):
    error_message = ""
    valid = True
    if len(house) > 5:
        error_message = "Max len of House is 5 char"
        valid = False
    return valid, error_message, house


def apartment_checker(apartment):
    error_message = ""
    valid = True
    if len(apartment) > 5:
        error_message = "Max len of House is 5 char"
        valid = False
    return valid, error_message, apartment


def email_checker(email):
    error_message = ""
    valid = True
    if email!='':
        if re.search('[a-zA-Z0-9\.\-\_]+@[a-zA-Z0-9\-\_\.]+\.[a-z]{2,4}', email) is None:
            error_message = "Email should have format: 'name@domain.[domains.]high_level_domain'"
            valid = False
    return valid, error_message, email


form_dict_temp = {
    "Name":
        {
    "value": "Hint: Input first and second name in one row",
    "valid": True,
    "checker": name_checker,
    "error_message": ""
        },
    "Birthday":
        {
            "value": "Hint: Use dd.mm.yyyy format",
            "valid": True,
            "checker": birthday_checker,
            "error_message": ""
        },
    "Email":
        {
            "value": "Hint: Use user@domain format",
            "valid": True,
            "checker": email_checker,
            "error_message": ""
        },
    "Phone":
        {
            "value": "Hint: Use + or digits only, phones separate by ','",
            "valid": True,
            "checker": phone_checker,
            "error_message": ""
        },
    "ZIP":
        {
            "value": "Hint: Up to 10 char",
            "valid": True,
            "checker": zip_checker,
            "error_message": ""
        },
    "Country":
        {
            "value": "Hint: Up to 50 char",
            "valid": True,
            "checker": country_checker,
            "error_message": ""
        },
    "Region":
        {
            "value": "Hint: Up to 50 char",
            "valid": True,
            "checker": region_checker,
            "error_message": ""
        },
    "City":
        {
            "value": "Hint: Up to 40 char",
            "valid": True,
            "checker": city_checker,
            "error_message": ""
        },
    "Street":
        {
            "value": "Hint: Up to 50 char",
            "valid": True,
            "checker": street_checker,
            "error_message": ""
        },
    "House":
        {
            "value": "",
            "valid": True,
            "checker": house_checker,
            "error_message": ""
        },
    "Apartment":
        {
            "value": "",
            "valid": True,
            "checker": apartment_checker,
            "error_message": ""
        },
}

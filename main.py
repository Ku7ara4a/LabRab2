from re import *
import requests

DATE_FORMAT = r"\b[0-3][0-9]\.[0-1][0-9]\.\d{4}\b"

def isCorrect(string: str) -> bool:
    date = string.split('.')
    day = int(date[0])
    month = int(date[1])
    year = int(date[2])
    Leap = False
    if day < 1 or month < 1 or year < 1:
        return False
    if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
        Leap = True
    if month < 1 or month > 12:
        return False
    if day < 1 or day > 31:
        return False
    else:
        if month % 2 == 0:
            if (day <= 29 and Leap == True and month == 2) or (day <= 30 and month != 2):
                return True
            else:
                return False
        else:
            if (day <= 31):
                return True
            else:
                return False

def find_in_text(string : str) -> list:
    list_of_dates = findall(DATE_FORMAT, string)
    new_list = []
    for i in list_of_dates:
        if isCorrect(i):
            new_list.append(i)

    return new_list

def find_in_file(file_name : str) -> list:
    new_list = []

    for encoding in ('utf-8', 'cp1251'):
        try:
            with open(file_name, 'r', encoding=encoding) as file:
                for line in file:
                    matches = findall(DATE_FORMAT, line)
                    for match in matches:
                        if isCorrect(match):
                            new_list.append(match)
            break
        except UnicodeDecodeError:
            continue

    return new_list

def find_in_web(url_name: str) -> list:
    new_list = []
    try:
        response = requests.get(url_name)
        response.raise_for_status()

        content = ""
        for encoding in ('utf-8', 'latin1'):
            try:
                content = response.content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue

        matches = findall(DATE_FORMAT, content)
        for match in matches:
            if isCorrect(match):
                new_list.append(match)
        return new_list

    except requests.RequestException as e:
        print("Ошибка при подключении к URL: ", e)
        return []

print(find_in_web(""))
from re import *
import requests

DATE_FORMAT = compile(r"\b((?:0[1-9]|[12][0-9]|3[01])\.(?:0[1-9]|1[0-2])\.\d{4})\b")
GIST_URL = "https://gist.github.com/Ku7ara4a/3a1d15d71eb5cbf314037f4999b45277/raw"

def isCorrect(string: str) -> bool:
    try:
        day, month, year = map(int, string.split('.'))
        if month < 1 or month > 12 or day < 1 or day > 31:
            return False

        if month in [4, 6, 9, 11] and day > 30:
            return False

        if month == 2:
            leap = (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0))
            if day > 29 or (day == 29 and not leap):
                return False

        return True
    except:
        return False

def find_in_text(string : str) -> list:
    list_of_dates = DATE_FORMAT.findall(string)
    return [date for date in list_of_dates if isCorrect(date)]

def find_in_file(file_name : str) -> list:
    new_list = []
    for encoding in ('utf-8', 'cp1251'):
        try:
            with open(file_name, 'r', encoding=encoding) as file:
                for line in file:
                    matches = DATE_FORMAT.findall(line)
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
        for encoding in ('utf-8', 'cp1251'):
            try:
                content = response.content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue

        matches = DATE_FORMAT.findall(content)
        for match in matches:
            if isCorrect(match):
                new_list.append(match)
        return new_list

    except requests.RequestException as e:
        print("Ошибка при подключении к URL: ", e)
        return []

print(find_in_web(GIST_URL))
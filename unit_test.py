import unittest
from unittest.mock import patch, mock_open
import requests

from main import DATE_FORMAT, is_correct, find_in_text, find_in_file, find_in_web

#Тесты скомпилированного регулярного выражения
class TestDateFormat(unittest.TestCase):
    def setUp(self):
        self.DATE_FORMAT = DATE_FORMAT

    def test_matches_valid_format(self):
        test_cases = [
            "01.01.2023",
            "31.12.1999",
            "15.06.2024",
            "29.02.2020"
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                matches = DATE_FORMAT.findall(test_case)
                self.assertEqual(len(matches), 1)
                self.assertEqual(matches[0], test_case)

    def test_matches_valid_format_in_text(self):
        text_samples = [
            ("Дата: 15.03.2023", ["15.03.2023"]),
            ("Период: с 01.01.2023 по 31.12.2023", ["01.01.2023", "31.12.2023"]),
            ("Даты: 15.03.2023, 20.04.2023", ["15.03.2023", "20.04.2023"]),
            ("Здесь дат нет", []),
            ("Смешанно: 15.03.2023 и 15/03/2023", ["15.03.2023"]),
        ]

        for text, expected in text_samples:
            with self.subTest(text=text):
                matches = DATE_FORMAT.findall(text)
                self.assertEqual(matches, expected)

    def test_reject_invalid_format(self):
        test_cases = [
            "1.1.2023", #нет нулей
            "01/01/2023", #слэш
            "01.01.23", #не полный год
            "2023.01.01", #не тот порядок
            "01.01.20235", #длинный год
            "ab.cd.efgh", #вообще без цифр
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                matches = DATE_FORMAT.findall(test_case)
                self.assertEqual(len(matches), 0)

    def test_boundary_cases(self):
        test_cases = [
            ("00.01.2023", False),  # день 00
            ("01.00.2023", False),  # месяц 00
            ("32.01.2023", False),  # день 32
            ("01.13.2023", False),  # месяц 13
            ("99.99.9999", False),  # невалидные числа
        ]

        for test_case, should_match in test_cases:
            with self.subTest(test_case=test_case):
                matches = DATE_FORMAT.findall(test_case)
                if should_match:
                    self.assertEqual(len(matches), 1)
                else:
                    self.assertEqual(len(matches), 0)

#Тесты валидации дат (високосный год, кривые даты и т.п.)
class TestIsCorrect(unittest.TestCase):
    def setUp(self):
        self.DATE_FORMAT = DATE_FORMAT

    def test_is_correct_valid(self):
        self.assertTrue(is_correct("01.01.2023"))
        self.assertTrue(is_correct("29.02.2020"))
        self.assertTrue(is_correct("28.02.2021"))
        self.assertTrue(is_correct("31.12.2023"))

    def test_is_correct_invalid(self):
        self.assertFalse(is_correct("31.04.2023"))  # апрель 31 дня
        self.assertFalse(is_correct("30.02.2021"))  # февраль 30 дней
        self.assertFalse(is_correct("32.01.2022"))  # день 32
        self.assertFalse(is_correct("29.02.2021"))  # невисокосный
        self.assertFalse(is_correct("15.13.2023"))  # месяц 13

    def test_is_correct_boundary_cases(self):
        self.assertFalse(is_correct("00.01.2023"))
        self.assertFalse(is_correct("01.00.2023"))
        self.assertFalse(is_correct("00.00.0000"))

#Тесты основных функций
class TestFunctions(unittest.TestCase):
    def setUp(self):
        self.DATE_FORMAT = DATE_FORMAT

    def test_find_in_text_with_correct(self):
        text = "15.03.2023, 29.02.2020, 31.04.2023, 30.02.2021"
        result = find_in_text(text)
        expected = ["15.03.2023", "29.02.2020"]
        self.assertEqual(result, expected)

    @patch('main.DATE_FORMAT')
    def test_find_in_text_calls_correct(self, mock_date_format):
        mock_date_format.findall.return_value = ["15.03.2023", "29.02.2021"] #второй заведомо неправильный
        result = find_in_text("test")
        mock_date_format.findall.assert_called_once_with("test")
        self.assertEqual(result, ["15.03.2023"])

    @patch('builtins.open', mock_open(read_data="Даты: 15.03.2023, 31.04.2023"))
    def test_find_in_file_correct(self):
        result = find_in_file("test.txt")
        self.assertEqual(result, ["15.03.2023"])

    @patch('main.requests.get')
    def test_find_in_web_correct(self, mock_get):
        mock_responce = unittest.mock.Mock()
        mock_responce.content = "Даты: 15.03.2023, 31.04.2023".encode("utf-8")
        mock_responce.raise_for_status.return_value = None
        mock_get.return_value = mock_responce
        result = find_in_web("hhtps://example.com")
        self.assertEqual(result, ["15.03.2023"])

    @patch('main.requests.get')
    def test_find_in_web_connection_error(self, mock_get):
        mock_get.side_effect = requests.RequestException("Connection error")
        result = find_in_web("https://example.com")
        self.assertEqual(result, [])

class TestFormatCompilation(unittest.TestCase):
    def setUp(self):
        self.DATE_FORMAT = DATE_FORMAT

    #Проверка на то, что DATE_FORMAT - скомпилированный
    def test_format_type(self):
        from re import Pattern
        self.assertIsInstance(DATE_FORMAT,Pattern)

    #Проверка методов формата
    def test_format_methods(self):
        text = "Даты: 15.03.2023, 20.04.2023"

        self.assertEqual(DATE_FORMAT.findall(text), ["15.03.2023", "20.04.2023"])

        search_result = DATE_FORMAT.search(text)
        self.assertIsNotNone(search_result)
        self.assertEqual(search_result.group(), '15.03.2023')

        matches = list(DATE_FORMAT.finditer(text))
        self.assertEqual(len(matches), 2)
        self.assertEqual(matches[0].group(), '15.03.2023')

def run_tests():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestDateFormat))
    suite.addTests(loader.loadTestsFromTestCase(TestIsCorrect))
    suite.addTests(loader.loadTestsFromTestCase(TestFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestFormatCompilation))

    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)
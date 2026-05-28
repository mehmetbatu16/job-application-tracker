import unittest
import re

def validate_password(password):
    if not re.search(r'[A-Z]', password) or not re.search(r'[0-9]', password):
        return False
    return True

class TestJobTrackerBusinessLogic(unittest.TestCase):
    def test_password_validation_success(self):
        self.assertTrue(validate_password("ValidPassword1"))
        self.assertTrue(validate_password("SecurePass2026"))

    def test_password_validation_no_uppercase(self):
        self.assertFalse(validate_password("lowercase123"))

    def test_password_validation_no_number(self):
        self.assertFalse(validate_password("NoNumberPass"))

    def test_password_validation_empty(self):
        self.assertFalse(validate_password(""))

if __name__ == '__main__':
    unittest.main()
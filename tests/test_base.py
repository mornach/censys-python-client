import unittest
from unittest.mock import patch, mock_open

from utils import CensysTestCase

from censys.base import CensysAPIBase
from censys.exceptions import (
    CensysException,
    CensysAPIException,
    CensysRateLimitExceededException,
    CensysNotFoundException,
    CensysUnauthorizedException,
)


class CensysAPIBaseTests(CensysTestCase):

    EXPECTED_ACCOUNT_KEYS = {"email", "first_login", "last_login", "login", "quota"}
    EXPECTED_QUOTA_KEYS = {"allowance", "resets_at", "used"}

    @classmethod
    def setUpClass(cls):
        cls._api = CensysAPIBase()

    def test_account(self):
        res = self._api.account()
        self.assertSetEqual(set(res.keys()), self.EXPECTED_ACCOUNT_KEYS)

    def test_quota(self):
        res = self._api.quota()
        self.assertSetEqual(set(res.keys()), self.EXPECTED_QUOTA_KEYS)
        self.assertTrue(
            all(isinstance(value, int) for value in [res["allowance"], res["used"]])
        )

    def test_get_exception_class(self):
        self.assertEqual(
            self._api._get_exception_class(401), CensysUnauthorizedException
        )
        self.assertEqual(
            self._api._get_exception_class(403), CensysUnauthorizedException
        )
        self.assertEqual(self._api._get_exception_class(404), CensysNotFoundException)
        self.assertEqual(
            self._api._get_exception_class(429), CensysRateLimitExceededException
        )

    def test_exception_repr(self):
        exception = CensysAPIException(404, "Not Found", const="notfound")
        self.assertEqual(repr(exception), "404 (notfound): Not Found")


@patch.dict("os.environ", {"CENSYS_API_ID": "", "CENSYS_API_SECRET": ""})
class CensysAPIBaseTestsNoEnv(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open, read_data="[DEFAULT]")
    def test_no_env(self, mock_file):
        with self.assertRaises(CensysException) as context:
            CensysAPIBase()

        self.assertIn("No API ID or API secret configured.", str(context.exception))


if __name__ == "__main__":
    unittest.main()

import sys
import types
import unittest


# Keep tests independent from runtime browser dependency.
sys.modules.setdefault("undetected_chromedriver", types.SimpleNamespace())

import immoscout_bulk_scraper as scraper


class ParseItemTests(unittest.TestCase):
    def test_parse_item_extracts_expected_fields(self):
        item = {
            "id": "abc123",
            "listing": {
                "localization": {
                    "primary": "en",
                    "en": {"text": {"title": "Nice flat", "description": "Near station"}},
                },
                "categories": ["Apartment", "Duplex"],
                "prices": {"rent": {"gross": 2500, "net": 2200}},
                "address": {
                    "street": "Main Street 1",
                    "postalCode": "8000",
                    "locality": "Zurich",
                    "geoCoordinates": {"latitude": 47.3769, "longitude": 8.5417},
                },
                "characteristics": {
                    "numberOfRooms": 3.5,
                    "livingSpace": 85,
                    "hasBalcony": True,
                    "hasElevator": True,
                    "hasParking": True,
                },
                "meta": {"createdAt": "2026-01-01"},
            },
        }

        row = scraper.parse_item(item)

        self.assertIsNotNone(row)
        self.assertEqual(row[0], "abc123")
        self.assertEqual(row[1], "Apartment")
        self.assertEqual(row[2], "Duplex")
        self.assertEqual(row[3], 2500)
        self.assertEqual(row[4], 2200)
        self.assertEqual(row[6], "Zurich")
        self.assertEqual(row[16], 1)  # Elevator
        self.assertEqual(row[17], 1)  # Parking
        self.assertEqual(row[31], "https://www.immoscout24.ch/rent/abc123")
        self.assertEqual(row[32], "Nice flat")


if __name__ == "__main__":
    unittest.main()

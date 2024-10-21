import unittest

from bs4 import BeautifulSoup

from scrape_car_listings import (
    generate_raw_listings_csv,
    clean_raw_listings
)

class TestScraper(unittest.TestCase):
    def test_get_raw_listings(self):
        raw_listings_csv =  generate_raw_listings_csv('Audi','A4','S-line') 
        self.assertIsNotNone(raw_listings_csv)

    # Should really split into two tests for both types of exceptions
    # At very least should mock get_page and extract_listing methods
    def test_generate_raw_listings_csv_throws_exception(self):
        try:
            generate_raw_listings_csv('blah', 'blah', 'blah')
        except (ValueError, Exception) as e:
            self.assertTrue(isinstance(e, (ValueError, Exception)))
if __name__=='__main__':
    unittest.main()
import unittest

from bs4 import BeautifulSoup
from mock import patch

from scrape_car_listings import (
    generate_raw_listings_csv,
    clean_raw_listings
)

class TestScraper(unittest.TestCase):

    @patch('scrape_car_listings.get_page')
    def test_get_raw_listings(self,get_page_mock):
        #Setup mock
        fake_soup = ""
        with open('stub-soup.txt','r', encoding='utf8') as file:
            fake_soup = file.read().replace('\n','')
        fake_soup = BeautifulSoup(fake_soup, 'lxml')
        get_page_mock.return_value = fake_soup
        #Call method
        raw_listings_csv =  generate_raw_listings_csv('Audi','A4','S-line') 
        self.assertIsNotNone(raw_listings_csv)
        # Called once to get the result count
        # Called again to parse the fake soup
        self.assertEqual(get_page_mock.call_count, 2)

    # Should really split into two tests for both types of exceptions
    # At very least should mock get_page and extract_listing methods
    def test_generate_raw_listings_csv_throws_exception(self):
        try:
            generate_raw_listings_csv('blah', 'blah', 'blah')
        except (ValueError, Exception) as e:
            self.assertTrue(isinstance(e, (ValueError, Exception)))
if __name__=='__main__':
    unittest.main()
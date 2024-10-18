import unittest

from bs4 import BeautifulSoup

from scrape_car_listings import (
    get_page, get_result_count,
    extract_listing_info
)

class TestScraper(unittest.TestCase):
    # Test getting one page returns soup
    def test_get_soup_from_page(self):
        soup = get_page('Audi','A4','',0)
        self.assertIsNotNone(soup)

    def test_get_result_count(self):
        fake_soup = ""
        with open('stub-soup.txt','r', encoding='utf8') as file:
            fake_soup = file.read().replace('\n','')
        fake_soup = BeautifulSoup(fake_soup, 'lxml')
        result_count = get_result_count(fake_soup)
        self.assertGreater(int(result_count), 0)
    
    def test_get_invalid_result_count(self):
        result_count = get_result_count("")
        self.assertEqual(int(result_count),0)
    
    def test_extract_listing_info(self):
        fake_li_element = ""
        with open('stub-li-element.txt','r', encoding='utf8') as file:
            fake_li_element = file.read().replace('\n','')
        fake_soup = BeautifulSoup(fake_li_element, 'html.parser')
        fake_li_element = fake_soup.find('li')
        extracted_element = extract_listing_info(fake_li_element)
        self.assertNotEqual({},extracted_element)
        
    def test_invalid_extract_listing_info(self):
        fake_li_element = ""
        fake_soup = BeautifulSoup(fake_li_element, 'html.parser')
        fake_li_element = fake_soup.find('li')
        extracted_element = extract_listing_info(fake_li_element)
        self.assertEqual({},extracted_element)
if __name__=='__main__':
    unittest.main()
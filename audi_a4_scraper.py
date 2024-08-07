from bs4 import BeautifulSoup
import requests
import re
import time
import csv
import datetime

def dealer_dictionary_generator():
    dealer_count = 0
    dealer_dictionary = {}

    start_from = 0
    soup = get_page(start_from)
    result_count = get_result_count(soup)
    result_count = int(result_count)
    page_count = 1
    rows = []

    while start_from <= result_count:
        soup = get_page(start_from)
        
        # Find all li elements with data-testid starting with 'listing-card-index-'
        li_elements = soup.find_all('li', attrs={'data-testid': re.compile(r'listing-card-index-\d+')})

        # Iterate over each li element and extract the data
        for li_element in li_elements:
            row = extract_listing_info(li_element)
            rows.append(row)
        
        page_count += 1
        print(f"Processed page starting at: {start_from}")
        start_from += 30
    
        # time.sleep(3)

    # Specify the CSV file path
    csv_file_path = 'car_listings.csv'

    # Write data to CSV
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['title', 'engine_size', 'engine_type', 'total_kms', 'price', 'link'])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Data successfully saved to {csv_file_path}.")
    return dealer_dictionary

def get_result_count(soup):
    h2_element = soup.find('h2', {'data-testid': 'h2-details-text'})

    if h2_element:
        strong_tag = h2_element.find('strong')
        if strong_tag:
            important_text = strong_tag.get_text(strip=True)
            print(f"Number of results: {important_text}")
            return important_text
        else:
            print("Number of results not found.")
    else:
        print("h2 element with data-testid 'h2-details-text' not found.")
    return 0

def get_page(start_from):
    url = f"https://www.donedeal.ie/cars?year_from=2014&year_to=2016&make=Audi%3Bmodel%3AA4&start={start_from}"
    headers = {'User-Agent': 'Mozilla/5.0'}

    page = requests.get(url, headers=headers)
    html_length = len(page.content)
    print(f"Length of HTML content: {html_length} bytes")

    soup = BeautifulSoup(page.content, 'lxml')
    li_count = len(soup.find_all('li'))
    print(f"Number of <li> elements: {li_count}")

    listing_card_count = len(soup.find_all('li', attrs={'data-testid': re.compile(r'listing-card-index-\d+')}))
    print(f"Number of listing card elements: {listing_card_count}")

    return soup

def extract_listing_info(li_element):
    data = {}

    # Extract the title
    title_element = li_element.find('p')
    data['title'] = title_element.get_text(strip=True) if title_element else 'No title found'

    # Extract details from the list
    details_list = li_element.find_all('li')
    if details_list and len(details_list) >= 3:
        data['engine_size'] = details_list[0].get_text(strip=True)
        data['engine_type'] = details_list[1].get_text(strip=True)
        data['total_kms'] = details_list[2].get_text(strip=True)
    else:
        data['engine_size'] = 'No details found'
        data['engine_type'] = 'No details found'
        data['total_kms'] = 'No details found'

    # Extract the price
    price_element = li_element.find('p', text=re.compile(r'€\d+'))
    data['price'] = price_element.get_text(strip=True) if price_element else 'No price found'

    # Extract the link
    link_element = li_element.find('a', href=True)
    data['link'] = link_element['href'] if link_element else 'No link found'

    return data

def calculate_average_price(input_csv, output_csv):
    total_price = 0
    count = 0

    with open(input_csv, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            price_text = row['price']
            price_match = re.search(r'€(\d+,\d+|\d+)', price_text.replace(',', ''))
            if price_match:
                price = int(price_match.group(1).replace(',', ''))
                total_price += price
                count += 1

    average_price = total_price / count if count > 0 else 0
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['timestamp', 'average_price'])
        writer.writerow([timestamp, f"€{average_price:,.2f}"])

    print(f"Average price calculated and saved to {output_csv}.")

# Example usage:
dealer_dictionary_generator()
calculate_average_price('car_listings.csv', 'average_price.csv')

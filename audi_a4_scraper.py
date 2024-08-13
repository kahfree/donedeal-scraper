import urllib.parse
from bs4 import BeautifulSoup
import requests
import re
import time
import csv
import datetime

def dealer_dictionary_generator(make, model):
    dealer_count = 0
    dealer_dictionary = {}

    start_from = 0
    soup = get_page(make, model, start_from)
    result_count = get_result_count(soup)
    result_count = int(result_count)
    page_count = 1
    rows = []

    while start_from <= result_count:
        soup = get_page(make, model, start_from)
        
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
    csv_file_path = f'{make}_{model}_listings.csv'

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

def get_page(make, model, start_from):
    base_url = "https://www.donedeal.ie/cars"
    
    # Manually construct the URL parameters
    make_model_param = f"{urllib.parse.quote(make)};model:{urllib.parse.quote(model)}"
    params = {
        'year_from': 2014,
        'year_to': 2016,
        'make': make_model_param,
        'start': start_from
    }

    # Manually construct the query string
    query_string = f"year_from={params['year_from']}&year_to={params['year_to']}&make={params['make']}&start={params['start']}"
    url = f"{base_url}?{query_string}"
    print(f"Fetching URL: {url}")

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

def calculate_average_price(input_csv, output_csv, make_model):
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

    # Check if the file exists before writing the header
    file_exists = False
    try:
        with open(output_csv, 'r', newline='', encoding='utf-8') as file:
            file_exists = True
    except FileNotFoundError:
        pass

    with open(output_csv, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['timestamp','make-model', 'average_price'])  # Write header if file does not exist
        writer.writerow([timestamp, make_model, f"€{average_price:,.2f}"])

    print(f"Average price calculated and appended to {output_csv}.")

# Example usage:
makes_and_models = [
    ('Audi', 'A4'),
    ('BMW', '3-Series'),
    ('Mercedes-Benz', 'C-Class')
]

for make, model in makes_and_models:
    dealer_dictionary_generator(make, model)
    calculate_average_price(f'{make}_{model}_listings.csv', 'average_price.csv', f'{make}-{model}')

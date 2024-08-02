import requests
import bs4
import time
import re
import csv

# this function generates a dictionary of dealers and their href.
def dealer_dictionary_generator():
    dealer_count = 0
    dealer_dictionary={}

	# requests url and stores webpage as soup var
	#https://www.donedeal.ie/cars?year_from=2014&year_to=2016&make=Audi%3Bmodel%3AA4&start=0
#.find("ul", id="dealers-list")
    start_from = 0
    soup = get_page(start_from)
    result_count = get_result_count(soup)
    result_count = int(result_count)
    page_count = 1
    rows = []
    while start_from <= result_count:
        soup = get_page(start_from)
  # Find all li elements with data-testid starting with 'listing-card-index-'
        # Find all li elements with data-testid starting with 'listing-card-index-'
        li_elements = soup.find_all('li', attrs={'data-testid': re.compile(r'listing-card-index-\d+')})

        # Iterate over each li element
        for li_element in li_elements:
            # Extract and print the data-testid
            row = extract_data(li_element)
            rows.append(row)
            # data_testid = li_element.get('data-testid', 'No data-testid attribute')
            # print(f"Data-testid: {data_testid}")

            # # Extract and print the title
            # title_element = li_element.find('p', class_='sc-AHTeh')
            # title = title_element.get_text(strip=True) if title_element else 'No title found'
            # print(f"Title: {title}")

            # # Extract and print the details from the list
            # details_list = li_element.find('ul', class_='sc-eWzREE')
            # if details_list:
            #     details = [li.get_text(strip=True) for li in details_list.find_all('li')]
            #     engine_size, engine_type, total_kms = details[:3]  # Assuming these are always present and in order
            #     print(f"Engine Size: {engine_size}")
            #     print(f"Engine Type: {engine_type}")
            #     print(f"Total Kms: {total_kms}")
            # else:
            #     print("No details list found")

            # # Extract and print the price
            # price_element = li_element.find('p', class_='sc-cvalOF kTpCrP')
            # price = price_element.get_text(strip=True) if price_element else 'No price found'
            # print(f"Price: {price}")

            # print('-' * 40)
        # print(li_elements)
        # print("END OF PAGE ",page_count)
        page_count += 1
        print(start_from)
        start_from += 30
    
        time.sleep(3)

    # Specify the CSV file path
    csv_file_path = 'car_listings.csv'

    # Write data to CSV
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write header
        writer.writerow(['Data-testid', 'Title', 'Engine Size', 'Engine Type', 'Total Kms', 'Price'])
        # Write data rows
        writer.writerows(rows)

    print(f"Data successfully saved to {csv_file_path}.")
    return dealer_dictionary

def get_result_count(soup):
    h2_element = soup.find('h2', {'data-testid': 'h2-details-text'})

    # Check if the h2 element was found
    if h2_element:
        # Find the strong tag within the h2 element
        strong_tag = h2_element.find('strong')
        if strong_tag:
            # Extract and print the text from the strong tag
            important_text = strong_tag.get_text(strip=True)
            print(f"Number of results: {important_text}")
            return important_text
        else:
            print("Number of results not found.")
    else:
        print("h2 element with data-testid 'h2-details-text' not found.")

def get_page(start_from):
    url = "https://www.donedeal.ie/cars?year_from=2014&year_to=2016&make=Audi%3Bmodel%3AA4&start="+str(start_from)
    headers={'User-Agent':'Mozilla/5'}

    page = requests.get(url, headers = headers)
	# print(page.content)
    soup = bs4.BeautifulSoup(page.content,'lxml')
    return soup

def extract_data(li_element):
    # Extract the data-testid
    data_testid = li_element.get('data-testid', 'No data-testid attribute')

    # Extract the title
    title_element = li_element.find('p', class_='sc-AHTeh')
    title = title_element.get_text(strip=True) if title_element else 'No title found'

    # Extract details from the list
    details_list = li_element.find('ul', class_='sc-eWzREE')
    if details_list:
        details = [li.get_text(strip=True) for li in details_list.find_all('li')]
        engine_size, engine_type, total_kms = details[:3]  # Assuming these are always present and in order
    else:
        engine_size, engine_type, total_kms = 'No engine size found', 'No engine type found', 'No total kms found'

    # Extract the price
    price_element = li_element.find('p', class_='sc-cvalOF kTpCrP')
    price = price_element.get_text(strip=True) if price_element else 'No price found'

    return [data_testid, title, engine_size, engine_type, total_kms, price]
dealer_dictionary_generator()
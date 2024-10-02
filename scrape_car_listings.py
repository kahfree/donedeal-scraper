import urllib.parse
from bs4 import BeautifulSoup
import requests
import re
import time
import os
import csv
import datetime
import matplotlib.pyplot as plt
import smtplib
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

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
    
    # Specify the CSV file path
    csv_file_path = f'raw_listings/{make}_{model}_listings_raw.csv'

    # Write data to CSV
    os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)
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
    query_string = f"year_from={params['year_from']}&year_to={params['year_to']}&make={params['make']}&start={params['start']}&country=Ireland"
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
    price_element = li_element.find('div', text=re.compile(r'€\d+'))
    # price_element = li_element.find('p')
    data['price'] = price_element.get_text(strip=True) if price_element else 'No price found'

    # Extract the link
    link_element = li_element.find('a', href=True)
    data['link'] = 'donedeal.ie' + link_element['href'] if link_element else 'No link found'

    return data

def calculate_average_price(input_csv, make_model):
    # Load the cleaned data into a pandas DataFrame
    df = pd.read_csv(input_csv)

    # Calculate the average price
    average_price = df['price'].mean()

    # Get the current timestamp
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    # Create the 'averages' directory if it doesn't exist
    os.makedirs('averages', exist_ok=True)

    # Path to the make-model specific CSV in the 'averages' directory
    output_csv = f'averages/{make_model}_average.csv'

    # Write the average price to the make-model specific CSV
    file_exists = os.path.exists(output_csv)
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    with open(output_csv, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['timestamp', 'make_model', 'average_price'])  # Write header if file does not exist
        writer.writerow([timestamp, make_model, f"€{average_price:,.2f}"])

    print(f"Average price calculated and saved to {output_csv}.")
    return average_price

def calculate_average_of_averages(make_model_csv):
    # Read the CSV file containing the averages for the specific make and model
    df = pd.read_csv(make_model_csv)

    # Ensure the 'average_price' column exists
    if 'average_price' in df.columns:
        # Convert the 'average_price' column to numeric, removing any non-numeric characters
        df['average_price'] = df['average_price'].replace({'€': '', ',': ''}, regex=True).astype(float)
        
        # Calculate the average of the averages in the file
        avg_of_avg = df['average_price'].mean()

        return avg_of_avg
    else:
        print("The 'average_price' column was not found in the CSV.")
        return 0

def calculate_percentage_difference(current_average, historical_average):
    if historical_average == 0:
        return float('inf')  # Avoid division by zero
    return ((current_average - historical_average) / historical_average) * 100

def generate_graph(output_csv, make_model):
    timestamps = []
    averages = []

    # Read the CSV file to extract timestamps and average prices
    with open(output_csv, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Check if the row matches the current make and model
            if row['make_model'] == make_model:
                timestamps.append(row['timestamp'])
                avg_price_text = row['average_price'].replace('€', '').replace(',', '')
                averages.append(float(avg_price_text))

    # Create the plot
    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, averages, marker='o')
    plt.xlabel('Timestamp')
    plt.ylabel('Average Price (€)')
    plt.title(f'Average Price for {make_model} Over Time')
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
    plt.tight_layout()  # Adjust layout to fit labels

    # Save the graph as an image file
    graph_path = f'graphs/{make_model}_average_price_graph.png'
    os.makedirs(os.path.dirname(graph_path), exist_ok=True)
    plt.savefig(graph_path)
    plt.close()
    return graph_path


def find_cheapest_cars(input_csv, average_price):
    data = pd.read_csv(input_csv)
    ideal_values = {
    'price': 10000,
    'total_kms': 130000
    }

    data['price_diff'] = (data['price'] - ideal_values['price']).abs()
    data['total_kms_diff'] = (data['total_kms'] - ideal_values['total_kms']).abs()

    print(data)

    scaler = StandardScaler()
    data[['price_diff','total_kms_diff']] = scaler.fit_transform(data[['price_diff','total_kms_diff']])

    data['score'] = data['price_diff'] + data['total_kms_diff']

    data = data.sort_values(by='score')
    # print(data)
    # # Load the cleaned data into a pandas DataFrame
    # df = pd.read_csv(input_csv)

    # # Filter out cars with a price less than 2000
    # df = df[df['price'] >= 2000]

    # # Sort by price first, then mileage
    # df_sorted = df.sort_values(by=['price', 'total_kms'], ascending=[True, True])

    # # Select the top 3 cheapest cars
    top_deals = data.head(3)

    # # Convert the top deals into a list of tuples for compatibility
    cars = [(row['price'], row['total_kms'], row) for _, row in top_deals.iterrows()]

    return cars

def send_email(graph_path, percentage_diff, cheapest_cars):
    from_address = "ethancaff@gmail.com"
    to_address = "ethancaff@gmail.com"
    subject = "Daily Car Listings Report"

    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = subject

    # Add text content
    body = f"""
    Today's average price is {percentage_diff:.2f}% different from the historical average.

    The 3 cheapest cars with lower than average mileage are:
    """
    for car in cheapest_cars:
        price, mileage, data = car
        body += f"\n- {data['title']}: {data['price']} with {data['total_kms']} (Link: {data['link']})"

    msg.attach(MIMEText(body, 'plain'))

    # Attach the graph
    with open(graph_path, 'rb') as f:
        img = MIMEImage(f.read())
        img.add_header('Content-Disposition', f'attachment; filename="{graph_path}"')
        msg.attach(img)

    # Send email
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_address, 'ehgd wvjn hlpk rsyj')
    server.send_message(msg)
    server.quit()

    print(f"Email sent to {to_address}.")

def clean_raw_listings(raw_csv):
    df = pd.read_csv(raw_csv)
    print("Test 1", df)
    column_data_types = df.dtypes
    print("Data types of each column:\n", column_data_types)
    # Step 1: Clean the 'price' column
    df['price'] = df['price'].replace({'€': '', ',': ''}, regex=True)
    print("Test 2", df)
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    print("Test 3", df)
    df = df.dropna(subset=['price'])
    print("Test 4", df)
    # Step 2: Clean the 'total_kms' column
    # Convert miles to kilometers where necessary
    def convert_to_kms(value):
        try:
            value = str(value).replace(',', '')
            if 'mi' in value:
                kms = float(value.replace(' mi', '')) * 1.60934
            elif 'km' in value:
                kms = float(value.replace(' km', ''))
            else:
                return None  # For values that are not valid
            return kms
        except ValueError:
            return 0.0

    df['total_kms'] = df['total_kms'].apply(convert_to_kms)
    print("Test 5", df)
    df = df.dropna(subset=['total_kms'])
    print("Test 6", df)

    # Step 3: Drop the 'engine_size' column
    df = df.drop(columns=['engine_size'])
    print("Test 7", df)
    # Step 4: Get the value counts of 'engine_type'
    engine_type_counts = df['engine_type'].value_counts()

    # Display the cleaned DataFrame and the value counts for 'engine_type'
    print("Cleaned DataFrame:\n", df)
    print("\nValue counts for 'engine_type':\n", engine_type_counts)

    column_data_types = df.dtypes
    print("Data types of each column:\n", column_data_types)

    new_csv_path = raw_csv.replace('raw','clean')
    os.makedirs(os.path.dirname(new_csv_path), exist_ok=True)
    df.to_csv(f"{new_csv_path}",index=False)

    print(f"\nCleaned data has been saved to '{new_csv_path}'")

def main():
    # Example usage:
    makes_and_models = [
        ('Audi', 'A4'),
        ('BMW', '3-Series'),
        ('Mercedes-Benz', 'C-Class')
    ]

    for make, model in makes_and_models:
        dealer_dictionary = dealer_dictionary_generator(make, model)
        clean_raw_listings(f'raw_listings/{make}_{model}_listings_raw.csv')
        avg_price = calculate_average_price(f'clean_listings/{make}_{model}_listings_clean.csv', f'{make}_{model}')
        historical_avg = calculate_average_of_averages(f'averages/{make}_{model}_average.csv')
        percentage_diff = calculate_percentage_difference(avg_price, historical_avg)

        graph_path = generate_graph(f'averages/{make}_{model}_average.csv', f'{make}_{model}')
        cheapest_cars = find_cheapest_cars(f'clean_listings/{make}_{model}_listings_clean.csv', avg_price)

        send_email(graph_path, percentage_diff, cheapest_cars)

if __name__ == "__main__":
    main()

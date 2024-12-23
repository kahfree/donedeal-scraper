import csv
import datetime
import os
import re
import smtplib
import urllib.parse

from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import matplotlib.pyplot as plt
import pandas as pd
import requests
from bs4 import BeautifulSoup
from sklearn.preprocessing import StandardScaler


makes_and_models = [
    ('Audi', 'A4', 'S-line'),
    ('BMW', '3-Series', 'F30'),
    ('Skoda', 'Octavia', 'VRS')
]
# Script will find 3 cars closest these values
ideal_values = {
    'price': 10000,
    'total_kms': 130000
}

filters = {
    'year_from': 2014,
    'year_to': 2016,
    'fuelType': 'Diesel',
    'transmission': 'Manual',
    'country': 'Ireland',
}

def generate_raw_listings_csv(make, model, words):
    csv_file_path  = ''

    try:
        start_from = 0
        soup = get_page(make, model, words, start_from)
        result_count = get_result_count(soup)
        result_count = int(result_count)
        page_count = 1
        rows = []

        while start_from <= result_count:

            soup = get_page(make, model, words, start_from)
            # Find all li elements with data-testid
            # starting with 'listing-card-index-'
            li_elements = soup.find_all(
                'li',
                attrs={'data-testid': re.compile(r'listing-card-index-\d+')}
                )

            # Iterate over each li element and extract the data
            for li_element in li_elements:
                print(type(li_element))
                row = extract_listing_info(li_element)
                rows.append(row)

            page_count += 1
            print(f"Processed page starting at: {start_from}")
            start_from += 30

        # Specify the CSV file path
        csv_file_path = f'raw_listings/{make}_{model}_{words}_listings_raw.csv'

        # Write data to CSV
        os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:

            writer = csv.DictWriter(
                file,
                fieldnames=[
                    'title', 'engine_size', 'engine_type',
                    'total_kms', 'price', 'link'
                ]
            )

            writer.writeheader()
            writer.writerows(rows)

        print(f"Data successfully saved to {csv_file_path}.")
        return csv_file_path
    except:
        raise Exception('An error occurred when fetching listings') 


def get_result_count(soup):
    if soup:
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


def get_page(make, model, words, start_from):

    base_url = "https://www.donedeal.ie/cars"

    # Manually construct the URL parameters
    # https://www.donedeal.ie/cars?year_from=2011&year_to=2016&make=BMW;
    # model:3-Series&words=F30&fuelType=Diesel&transmission=Manual&
    # country=Ireland&verifications=manufacturerApproved&
    # verifications=greenlightVerified&verifications=trustedDealer
    make_model_param = (f"{urllib.parse.quote(make)};"
                        f"model:{urllib.parse.quote(model)}")
    params = {
        'year_from': filters['year_from'],
        'year_to': filters['year_to'],
        'make': make_model_param,
        'start': start_from,
        'words': words,
        'fuelType': filters['fuelType'],
        'transmission': filters['transmission'],
        'country': filters['country'],
    }

    # Manually construct the query string
    # Verifications are hardcoded in for everyones sake
    query_string = (f"year_from={params['year_from']}"
                    f"&year_to={params['year_to']}"
                    f"&make={params['make']}&start={params['start']}"
                    f"&words={params['words']}&fuelType={params['fuelType']}"
                    f"&transmission={params['transmission']}"
                    f"&country={params['country']}"
                    f"&verifications=manufacturerApproved"
                    "&verifications=greenlightVerified"
                    "&verifications=trustedDealer")

    url = f"{base_url}?{query_string}"
    print(f"Fetching URL: {url}")

    headers = {'User-Agent': 'Mozilla/5.0'}

    page = requests.get(url, headers=headers)
    html_length = len(page.content)
    print(f"Length of HTML content: {html_length} bytes")

    soup = BeautifulSoup(page.content, 'lxml')
    li_count = len(soup.find_all('li'))
    print(f"Number of <li> elements: {li_count}")

    listing_card_count = len(soup.find_all(
        'li',
        attrs={'data-testid': re.compile(r'listing-card-index-\d+')})
    )

    print(f"Number of listing card elements: {listing_card_count}")

    return soup


def extract_listing_info(li_element):
    data = {}
    if li_element is None:
        return data
    # Extract the title
    title_element = li_element.find('p')
    data['title'] = (
        title_element.get_text(strip=True)
        if title_element
        else 'No title found'
    )

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
    data['price'] = (
        price_element.get_text(strip=True)
        if price_element
        else 'No price found'
    )

    # Extract the link
    link_element = li_element.find('a', href=True)
    data['link'] = (
        'donedeal.ie' + link_element['href']
        if link_element
        else 'No link found'
    )

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
            # Write header if file does not exist
            writer.writerow(['timestamp', 'make_model', 'average_price'])
        writer.writerow([timestamp, make_model, f"€{average_price:,.2f}"])

    print(f"Average price calculated and saved to {output_csv}.")
    return average_price


def calculate_average_of_averages(make_model_csv):
    # Read the CSV file containing the averages for the specific make and model
    df = pd.read_csv(make_model_csv)

    # Ensure the 'average_price' column exists
    if 'average_price' in df.columns:
        # Convert the 'average_price' column to numeric
        # removing any non-numeric characters
        df['average_price'] = (
            df['average_price'].replace(
                {'€': '', ',': ''},
                regex=True
            ).astype(float)
        )

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
                dt = (
                    datetime.datetime.strptime(
                        row['timestamp'],
                        "%Y-%m-%d_%H-%M-%S"
                    )
                )
                fmt_dt = formatted_timestamp = dt.strftime("%m/%d/%Y\n%H:%M")
                timestamps.append(fmt_dt)
                avg_price_text = (
                    row['average_price']
                    .replace('€', '')
                    .replace(',', '')
                )
                averages.append(float(avg_price_text))

    # Create the plot
    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, averages, marker='o')
    plt.xlabel('Timestamp')
    plt.ylabel('Average Price (€)')
    plt.title(f'Average Price for {make_model} Over Time')
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=0)
    # Adjust layout to fit labels
    plt.tight_layout()

    # Save the graph as an image file
    graph_path = f'graphs/{make_model}_average_price_graph.png'
    os.makedirs(os.path.dirname(graph_path), exist_ok=True)
    plt.savefig(graph_path)
    plt.close()
    return graph_path


def find_cheapest_cars(input_csv, average_price):

    data = pd.read_csv(input_csv)

    data['price_diff'] = (
        (data['price'] - ideal_values['price'])
        .abs()
    )
    data['total_kms_diff'] = (
        (data['total_kms'] - ideal_values['total_kms'])
        .abs()
    )

    print(data)

    scaler = StandardScaler()

    data[['price_diff', 'total_kms_diff']] = (
        scaler.fit_transform(data[['price_diff', 'total_kms_diff']])
    )

    data['score'] = data['price_diff'] + data['total_kms_diff']

    data = data.sort_values(by='score')

    # # Select the top 3 cheapest cars
    top_deals = data.head(3)

    # Convert into a list of car dicts
    cars = (
        [(row)
            for _, row in top_deals.iterrows()]
    )

    return cars


def send_email(graph_path, percentage_diff, cheapest_cars, car_type):

    from_address = "ethancaff@gmail.com"
    to_address = "ethancaff@gmail.com"

    date = datetime.datetime.today().strftime('%d-%m-%Y')
    subject = f"{car_type}'s prices {date}"

    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = subject

    body = (
        f"""
        <html>
            <body>
                <p>Today's average price is
                 <strong>{percentage_diff:.2f}%</strong> different from the
                 historical average.</p>
                <p>The 3 cheapest cars with lower than average mileage are:</p>
                <ul>
        """
    )
    # Add each car as a list item with a clickable link
    for car in cheapest_cars:
        body += f"""
            <li>
                 <a href="{car['link']}">
                    {car['title']}: €{car['price']:,}
                     with {car['total_kms']:,} KMs
                </a>
            </li>
        """

    # Close the HTML tags
    body += """
            </ul>
        </body>
    </html>
    """

    msg.attach(MIMEText(body, 'html'))

    # Attach the graph
    with open(graph_path, 'rb') as f:
        img = MIMEImage(f.read())
        img.add_header(
            'Content-Disposition',
            f'attachment; filename="{graph_path}"'
        )
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

    column_data_types = df.dtypes
    print("Data types of each column:\n", column_data_types)

    # Step 1: Clean the 'price' column
    df['price'] = df['price'].replace({'€': '', ',': ''}, regex=True)

    df['price'] = pd.to_numeric(df['price'], errors='coerce')

    df = df.dropna(subset=['price'])

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
    df = df.dropna(subset=['total_kms'])

    # Step 3: Drop the 'engine_size' column
    df = df.drop(columns=['engine_size'])

    # Step 4: Get the value counts of 'engine_type'
    engine_type_counts = df['engine_type'].value_counts()

    # Display the cleaned DataFrame and the value counts for 'engine_type'
    print("Cleaned DataFrame:\n", df)
    print("\nValue counts for 'engine_type':\n", engine_type_counts)

    column_data_types = df.dtypes
    print("Data types of each column:\n", column_data_types)

    new_csv_path = raw_csv.replace('raw', 'clean')
    os.makedirs(os.path.dirname(new_csv_path), exist_ok=True)
    df.to_csv(f"{new_csv_path}", index=False)

    print(f"\nCleaned data has been saved to '{new_csv_path}'")


def main():
    # Example usage:
    

    for make, model, words in makes_and_models:
        # Creates raw csv of filtered listings
        generate_raw_listings_csv(
            make,
            model, 
            words
        )
        # Transform raw listings into clean and creates new csv
        clean_raw_listings(
            f'raw_listings/{make}_{model}_{words}_listings_raw.csv'
        )
        # Calculate the average price of the clean listings
        avg_price = calculate_average_price(
            f'clean_listings/{make}_{model}_{words}_listings_clean.csv',
            f'{make}_{model}_{words}'
        )
        # Generate latest average of price averages
        historical_avg = calculate_average_of_averages(
            f'averages/{make}_{model}_{words}_average.csv'
        )
        # Get the % difference of todays average from historic average
        percentage_diff = calculate_percentage_difference(
            avg_price,
            historical_avg
        )
        # Generate graph with including todays average
        graph_path = generate_graph(
            f'averages/{make}_{model}_{words}_average.csv',
            f'{make}_{model}_{words}'
        )
        # Find the 3 best deals on specified car
        cheapest_cars = find_cheapest_cars(
            f'clean_listings/{make}_{model}_{words}_listings_clean.csv',
            avg_price
        )
        # Send the mail
        send_email(
            graph_path,
            percentage_diff,
            cheapest_cars,
            f'{make} {model} {words}'
        )

if __name__ == "__main__":
    main()

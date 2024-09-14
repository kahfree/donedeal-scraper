# 🚗 DoneDeal Car Listings Scraper

## 📝 Overview

This project is a Python-based web scraper that extracts car listings from DoneDeal.ie for specified makes and models, processes the data to calculate average prices, and sends an email report with the findings. The script also generates graphs 📊 to visualize price trends over time and identifies the best deals based on price and mileage data.

## ✨ Features

- 🏎️ Scrapes car listings from DoneDeal.ie for selected makes and models.
- 🛠️ Cleans and processes raw listings data.
- 💰 Calculates average prices of the cars listed.
- 📈 Generates graphs showing the trend in average prices over time.
- 🔍 Identifies the best deals based on price and mileage using a scoring system.
- 📧 Automatically sends an email report with the graph and summary of the findings, including the top 3 cheapest cars with lower-than-average mileage.
- ⏰ Option for automated daily execution via cron job (optional).

## ⚙️ Installation

### 📋 Prerequisites

- **Python 3.x** installed.
- Required Python libraries: `requests`, `BeautifulSoup`, `pandas`, `matplotlib`, `scikit-learn`, `smtplib`, `email`.
  - You can install them using `pip`:
    ```bash
    pip install requests beautifulsoup4 pandas matplotlib scikit-learn
    ```
- **SMTP server** credentials for sending emails (e.g., Gmail).
- **Raspberry Pi or Linux-based server** (if planning to automate the script execution via cron job).

### 🔧 Setting Up the Project

1. Clone the repository or download the script to your local machine:
    ```bash
    git clone https://github.com/yourusername/DoneDealScraper.git
    ```

2. Install the required libraries (as mentioned above).

3. Set up email credentials for sending reports:
    - In the `send_email()` function, replace the `from_address` and `to_address` variables with your email addresses.
    - Use an [App Password](https://support.google.com/accounts/answer/185833) if you're using Gmail and 2FA.
    - Replace the `server.login` credentials in the `send_email()` function with your email and app-specific password.

4. Update the car makes and models you want to track in the `main()` function of the script:
    ```python
    makes_and_models = [
        ('Audi', 'A4'),
        ('BMW', '3-Series'),
        ('Mercedes-Benz', 'C-Class')
    ]
    ```

5. (Optional) Set up a cron job for daily automation (Linux or Raspberry Pi):
    - Open your crontab by running:
        ```bash
        crontab -e
        ```
    - Add the following line to run the script daily at a specific time (e.g., 8:00 AM):
        ```bash
        0 8 * * * /usr/bin/python3 /path/to/your/project/main.py
        ```

## ⚙️ How It Works

### 🌐 Web Scraping

The script scrapes car listings from DoneDeal.ie by constructing search queries for specified makes and models. It then extracts relevant details such as the car's title, engine size, engine type, mileage, price, and link to the listing.

### 🧹 Data Processing

The raw listings data is cleaned and transformed:
- 💸 Price values are normalized (removing currency symbols and commas).
- 📏 Mileage values are converted to kilometers, where applicable.
- The cleaned data is saved as a CSV file for further analysis.

### 💵 Average Price Calculation

- The script calculates the average price of all listings in a given search.
- 📊 Historical averages are stored and updated over time, allowing the script to calculate price trends and compare current prices with historical data.

### 🔎 Best Deals Identification

Using price and mileage data, the script identifies the top 3 cheapest cars with mileage lower than the average, making them potential best deals. A scoring system is applied to rank cars based on how close they are to ideal price and mileage values.

### 📉 Graph Generation

A line graph showing the trend of average prices for the specific make and model over time is generated using `matplotlib` and saved as an image.

### 📧 Email Report

An email containing the following is sent:
- A graph of average price trends over time.
- A percentage difference between the current and historical average prices.
- The top 3 best deals based on price and mileage, with links to the listings.

## 🔧 Customization

You can easily adjust the following aspects:
- **Car makes and models**: Add or remove makes and models from the `makes_and_models` list in the `main()` function.
- **Search year range**: Modify the year range in the `get_page()` function by adjusting the `year_from` and `year_to` parameters.
- **Ideal price and mileage**: Change the values in the `find_cheapest_cars()` function to adjust what the script considers an "ideal" deal.

## 📧 Example Email Report

The email report includes:
1. 📈 A graph of average price trends for the selected make and model.
2. 📊 A percentage difference between today's average price and the historical average.
3. 🚗 The top 3 cheapest cars with lower-than-average mileage, including links to the listings.

## 🚀 Future Enhancements

- **🔧 Additional Filtering Options**: Allow users to filter by fuel type, transmission, and other car features.
- **🤖 Advanced Deal Identification**: Use machine learning models to identify cars that are significantly underpriced.
- **🌍 Broader Listings Sources**: Integrate other car listing websites for a wider selection of vehicles.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

# DoneDeal Car Listings Scraper

## Overview

This project is a Python script that scrapes car listings from DoneDeal.ie for specified makes and models, processes the data to calculate average prices, and sends an email report with the findings. The script also generates graphs to visualize price trends over time and highlights the cheapest cars with lower-than-average mileage.

## Features

- **Scrapes car listings** from DoneDeal.ie for selected makes and models.
- **Calculates average prices** of the cars listed.
- **Generates graphs** showing the trend in average prices over time.
- **Identifies the cheapest cars** with lower-than-average mileage.
- **Sends an email report** containing the graph and a summary of the findings.
- **Automated daily execution** via cron job (optional).

## Installation

### Prerequisites

- Python 3.x installed
- SMTP server for sending emails (e.g., Gmail)
- Raspberry Pi or Linux-based server (for automation via cron job)

### Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/donedeal-scraper.git
   cd donedeal-scraper

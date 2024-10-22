# 📊 Insider Data Scraper and Visualization Panel

This project scrapes insider transaction data from [Dataroma](https://www.dataroma.com) and stores it in MongoDB. It also provides a Flask web application to visualize and filter the data.

## 🚀 How to Run the Project

### 1. Clone the repository
```bash
git clone https://github.com/radoslavatanasov1/Insider-trading.git
cd Insider-trading
```
### 2. Install Dependencies
Ensure you have Python 3.x installed and use pip to install the required packages:
```bash
pip install -r requirements.txt
```
### 3. MongoDB Setup
This project uses MongoDB to store parsed data. Make sure to set your MongoDB connection URI in the code:

```bash
# MongoDB connection
mongo_uri = "your_mongodb_connection_string"
```
### 4. Running the Scraper
You can scrape insider data using the scraper script. It uses multi-threading for efficient data extraction:
```bash
python main.py
```
Parameters:
You’ll be prompted to enter the start and end page for scraping. Dataroma currently has around 2100 pages.

### 5. Running the Flask Web App
You can visualize the parsed data through a modern, interactive web panel:
```bash
python app.py
```
Open your browser and navigate to http://127.0.0.1:5000.
Use the date filter to view transactions within a specific range.

```bash
Enter the start page number (1-2103): 1
Enter the end page number (1-2103): 10
```

## 🧰 Features
#### Multithreaded scraping for efficient data collection.
#### Data storage in MongoDB for easy querying and scalability.
#### Beautiful web interface built with Flask for visualizing insider trades.
#### Pagination and filtering to easily navigate the data.



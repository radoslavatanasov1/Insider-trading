import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import concurrent.futures
import time
import random
#            <!-- CODED BY RADOSLAV -->

# MongoDB connection
mongo_uri = "test"
client = MongoClient(mongo_uri)
db = client["insiderdata"]
collection = db["parsed_data"]

# List of user agents
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0",
    "Mozilla/5.0 (Linux; Android 10; Pixel 3 XL Build/QP1A.190711.020) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 12; Nexus 5 Build/SQ1A.220205.002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Mobile Safari/537.36"
]

def parse_page(page):
    base_url = "https://www.dataroma.com/m/ins/ins.php?t=y2&am=0&sym=&o=fd&d=d&L="
    url = f"{base_url}{page}"
    
    # Select a random user agent
    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    print(f"Fetching data from: {url}")
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to retrieve data from {url}. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the table rows
    rows = soup.find_all('tr')[1:]  # Skip the header row
    print(f"Found {len(rows)} rows on page {page}")

    page_data = []
    for row in rows:
        data_row = {}
        try:
            filing_date_cell = row.find('td', class_='f_date')
            filing_date = filing_date_cell.get_text(strip=True)

            # Check if the filing date contains a time immediately after it
            if filing_date[-5].isdigit():  # Checking if the character before last 5 characters is a digit
                filing_date = filing_date[:-5] + ' ' + filing_date[-5:]

            # Split date and time if they are concatenated
            date_parts = filing_date.split(' ')
            if len(date_parts) > 2 and len(date_parts[-1]) == 5:  # Assuming time is always in HH:MM format
                filing_date = ' '.join(date_parts[:-1]) + ' ' + date_parts[-1]

            data_row['Filing Date'] = filing_date
            data_row['Filing Link'] = filing_date_cell.find('a')['href'] if filing_date_cell.find('a') else None
            
            data_row['Symbol'] = row.find('td', class_='iss_sym').get_text(strip=True)
            data_row['Security'] = row.find('td', class_='iss_name').get_text(strip=True)
            data_row['Reporting Name'] = row.find('td', class_='rep_name').get_text(strip=True)
            data_row['Relationship'] = row.find('td', class_='rel').get_text(strip=True)
            data_row['Transaction Date'] = row.find('td', class_='t_date').get_text(strip=True)
            data_row['Transaction Code'] = row.find('td', class_='tran_code').get_text(strip=True)
            data_row['Shares'] = row.find('td', class_='sh').get_text(strip=True)
            data_row['Price'] = row.find('td', class_='pr').get_text(strip=True)
            data_row['Amount'] = row.find('td', class_='amt').get_text(strip=True)
            data_row['D/I'] = row.find('td', class_='dir_ind').get_text(strip=True)

            page_data.append(data_row)

        except AttributeError:
            # Skip the row silently if an AttributeError occurs
            continue

    return page_data

def parse_dataroma(start_page, end_page):
    all_data = []
    total_pages = end_page - start_page + 1
    start_time = time.time()  # Start timing the overall operation

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(parse_page, page): page for page in range(start_page, end_page + 1)}
        
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            page = futures[future]
            try:
                page_data = future.result()
                all_data.extend(page_data)  # Add the page data to the main list
                
                # Calculate and print ETA
                elapsed_time = time.time() - start_time
                avg_time_per_page = elapsed_time / (i + 1)
                remaining_pages = total_pages - (i + 1)
                eta = remaining_pages * avg_time_per_page
                print(f"Processed page {page}. ETA: {eta:.2f} seconds")

            except Exception as exc:
                print(f"Page {page} generated an exception: {exc}")

    # Insert all collected data into MongoDB in a single batch
    if all_data:
        collection.insert_many(all_data)
        print(f"Inserted {len(all_data)} rows into MongoDB.")

# Example usage
if __name__ == "__main__":
    start_page = int(input("Enter the start page number (1-2103): "))
    end_page = int(input("Enter the end page number (1-2103): "))
    parse_dataroma(start_page, end_page)

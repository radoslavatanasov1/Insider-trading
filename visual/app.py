from flask import Flask, render_template, request
from pymongo import MongoClient
from datetime import datetime
#            <!-- CODED BY RADOSLAV -->

app = Flask(__name__)

mongo_uri = "test"
client = MongoClient(mongo_uri)
db = client["insiderdata"]
collection = db["parsed_data"]

@app.route("/", methods=["GET", "POST"])
def index():
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")
    query = {}

    if start_date and end_date:
        query = {
            "Transaction Date": {
                "$gte": datetime.strptime(start_date, "%Y-%m-%d"),
                "$lte": datetime.strptime(end_date, "%Y-%m-%d")
            }
        }

    # Pagination parameters
    page = int(request.args.get("page", 1))  # Get the page number, default to 1
    limit = 50  # Number of entries per page
    skip = (page - 1) * limit  # Calculate how many entries to skip

    # Fetch the data with pagination
    data = list(collection.find(query).skip(skip).limit(limit))

    # Count total entries for pagination
    total_entries = collection.count_documents(query)

    # Initialize summary variables
    summary = {
        "total_buy_transactions": 0,
        "total_sell_transactions": 0,
        "total_buy_amount": 0.0,
        "total_sell_amount": 0.0,
    }

    # Calculate summary data
    for item in data:
        amount_str = item['Amount'].replace('Amount $', '').replace('▲▼', '').replace(',', '').strip()
        
        if not amount_str:
            print(f"Skipping empty amount: {item['Amount']}")
            continue
        
        try:
            amount = float(amount_str)
        except ValueError:
            print(f"Skipping invalid amount: {item['Amount']}")
            continue

        if item['Transaction Code'] == 'Purchase':
            summary['total_buy_transactions'] += 1
            summary['total_buy_amount'] += amount
        elif item['Transaction Code'] == 'Sale':
            summary['total_sell_transactions'] += 1
            summary['total_sell_amount'] += amount

    # Format summary amounts for display
    summary['total_buy_amount'] = f"{summary['total_buy_amount']:,.2f}"
    summary['total_sell_amount'] = f"{summary['total_sell_amount']:,.2f}"

    # Format amounts in data for display
    for item in data:
        amount_str = item['Amount'].replace('Amount $', '').replace('▲▼', '').replace(',', '').strip()
        
        if not amount_str:
            item['Amount'] = '0.00'
        else:
            item['Amount'] = f"{float(amount_str):,.2f}"

    # Calculate total pages
    total_pages = (total_entries // limit) + (1 if total_entries % limit > 0 else 0)

    # Pass the `min` function to the template
    return render_template("index.html", data=data, summary=summary, page=page, total_pages=total_pages, min=min)


if __name__ == "__main__":
    app.run(debug=True)

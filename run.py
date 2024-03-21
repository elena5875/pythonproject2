import gspread
import logging
from google.oauth2.service_account import Credentials
from datetime import datetime

# Import the logging module to handle logging
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def authenticate_google_sheets():
    """Authenticate with Google Sheets using service account credentials."""
    SCOPE = ["https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive.file",
             "https://www.googleapis.com/auth/drive"]
    CREDS = Credentials.from_service_account_file('creds.json')
    scoped_credentials = CREDS.with_scopes(SCOPE)
    gspread_client = gspread.authorize(scoped_credentials)
    return gspread_client


def add_item(gspread_client, item_name, quantity, sheet_name):
    """Add item to the specified sheet."""
    try:
        sheet = gspread_client.open(sheet_name).sheet1
        sheet.append_row([item_name, quantity, datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        logging.info(f"Item '{item_name}' added to {sheet_name}.")
    except Exception as e:
        logging.error(f"Failed to add item '{item_name}' to {sheet_name}: {e}")
        raise

def calculate_inventory_status(gspread_client):
    """Calculate inventory status by subtracting stocks used from stocks in."""
    try:
        stocks_in= gspread_client.open('stocks_in').sheet1
        stocks_used = gspread_client.open('stocks_used').sheet1
        stocks_in_data = stocks_in.get_all_values()
        stocks_used_data = stocks_used.get_all_values()

        inventory_status = {}

        # Calculate total stocks in
        for row in stocks_in_data[1:]:
            item_name, quantity, _ = row
            inventory_status[item_name] = int(quantity)

        # Subtract total stocks used
        for row in stocks_used_data[1:]:
            item_name, quantity, _ = row
            inventory_status[item_name] -= int(quantity)

        return inventory_status

    except Exception as e:
        logging.error(f"Failed to calculate inventory status: {e}")
        raise

def display_inventory_status(inventory_status):
    """Display inventory status."""
    try:
        logging.info("\nInventory Status:")
        for item, quantity in inventory_status.items():
            logging.info(f"{item}: {quantity}")
    except Exception as e:
        logging.error(f"Failed to display inventory status: {e}")
        raise

def main():
    """Main function to interact with the inventory management system."""
    try:
        gspread_client = authenticate_google_sheets()
        spreadsheet = gspread_client.open('Inventory_of_stocks')
        stocks_in = spreadsheet.worksheet('stocks_in')
        stocks_used = spreadsheet.worksheet('stocks_used')
        inventory = spreadsheet.worksheet('inventory')
        items = ["FLOUR", "SUGAR", "EGG", "MILK", "COFFEE", "RICE"]
        
        while True:
            logging.info("\nMenu:")
            logging.info("1. Add stocks coming in")
            logging.info("2. Record stocks used")
            logging.info("3. Display inventory")
            logging.info("4. Update stocks_in with previous inventory data")
            logging.info("5. Display inventory status")
            logging.info("6. Exit")
            choice = input("\nEnter your choice (1-6): ")

            if choice == '1':
                logging.info("Select item from the list:")
                for index, item in enumerate(items, start=1):
                    logging.info(f"{index}. {item}")
                item_index = input("Enter item number: ")
                if item_index.isdigit() and 1 <= int(item_index) <= len(items):
                    item_name = items[int(item_index) - 1]
                    quantity = input("Enter quantity: ")
                    if quantity.isdigit() and int(quantity) > 0:
                        add_item(gspread_client, item_name, int(quantity), stocks_in)
                    else:
                        logging.error("Invalid quantity. Please enter a valid positive number.")
                else:
                    logging.error("Invalid item number. Please enter a valid number.")

            elif choice == '2':
                logging.info("Select item from the list:")
                for index, item in enumerate(items, start=1):
                    logging.info(f"{index}. {item}")
                item_index = input("Enter item number: ")
                if item_index.isdigit() and 1 <= int(item_index) <= len(items):
                    item_name = items[int(item_index) - 1]
                    quantity = input("Enter quantity: ")
                    if quantity.isdigit() and int(quantity) > 0:
                        add_item(gspread_client, item_name, int(quantity), stocks_used)
                    else:
                        logging.error("Invalid quantity. Please enter a valid positive number.")
                else:
                    logging.error("Invalid item number. Please enter a valid number.")

            # Remaining code...
                
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

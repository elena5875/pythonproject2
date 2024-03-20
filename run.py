import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)  

def authenticate_google_sheets():
    """Authenticate with Google Sheets using service account credentials."""
    try:
        SCOPE = ["https://www.googleapis.com/auth/spreadsheets",
                 "https://www.googleapis.com/auth/drive.file",
                 "https://www.googleapis.com/auth/drive"]
        CREDS = Credentials.from_service_account_file('creds.json')
        scoped_credentials = CREDS.with_scopes(SCOPE)
        gspread_client = gspread.authorize(scoped_credentials)
        logging.info("Successfully authenticated with Google Sheets.")
        return gspread_client
    except Exception as e:
        logging.error(f"Authentication failed: {e}")
        raise

def add_item(gspread_client, item_name, quantity, sheet_name):
    """Add item to the specified sheet."""
    try:
        sheet = gspread_client.open(sheet_name).sheet1
        sheet.append_row([item_name, quantity, datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        logging.info(f"Item '{item_name}' added to {sheet_name}.")
    except Exception as e:
        logging.error(f"Failed to add item '{item_name}' to {sheet_name}: {e}")
        raise

def main():
    """Main function to interact with the inventory management system."""
    gspread_client = authenticate_google_sheets()
    items = ["FLOUR", "SUGAR", "EGG", "MILK", "COFFEE", "RICE"]
    
    while True:
        logging.info("\nMenu:")
        logging.info("1. Add stocks coming in")
        logging.info("2. Record stocks used")
        logging.info("3. Display inventory")
        logging.info("4. Update stocks_in with previous inventory data")
        logging.info("5. Exit")

        choice = input("\nEnter your choice (1-5): ")

        if choice == '1':
            logging.info("Select item from the list:")
            for index, item in enumerate(items, start=1):
                logging.info(f"{index}. {item}")
            item_index = int(input("Enter item number: ")) - 1
            item_name = items[item_index]
            quantity = int(input("Enter quantity: "))
            add_item(gspread_client, item_name, quantity, 'stocks_in')

        elif choice == '2':
            logging.info("Select item from the list:")
            for index, item in enumerate(items, start=1):
                logging.info(f"{index}. {item}")
            item_index = int(input("Enter item number: ")) - 1
            item_name = items[item_index]
            quantity = int(input("Enter quantity: "))
            add_item(gspread_client, item_name, quantity, 'stocks_used')

        elif choice == '3':
            sheet_name = 'inventory'
            try:
                sheet = gspread_client.open(sheet_name).sheet1
                data = sheet.get_all_values()
                logging.info(f"\n{sheet_name}:\n{data}")
            except Exception as e:
                logging.error(f"Failed to display {sheet_name}: {e}")

        elif choice == '4':
            sheet_name = 'stocks_in'
            try:
                sheet = gspread_client.open(sheet_name).sheet1
                previous_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                data = sheet.get_all_values()
                for row in data[1:]:
                    item_name, quantity, _ = row
                    add_item(gspread_client, item_name, quantity, sheet_name)
                logging.info("Previous day's inventory data added to stocks_in.")
            except Exception as e:
                logging.error(f"Failed to update stocks_in with previous inventory data: {e}")

        elif choice == '5':
            logging.info("Exiting...")
            break

        else:
            logging.info("Invalid choice. Please choose a valid option.")

if __name__ == "__main__":
    main()

    
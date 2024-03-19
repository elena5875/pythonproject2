import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)  # Set logging level to INFO

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

def update_sheet(sheet, menu_list, quantity_type):
    """Update a sheet with quantity information for all items."""
    try:
        current_date = datetime.today().strftime("%Y-%m-%d")
        logging.info(f"Placing items in sheet with the date: {current_date}")

        items_data = []  # List to store items and their quantities

        for menu_item in menu_list:
            quantity_input = int(input(f"Enter {quantity_type} quantity for {menu_item}: "))
            items_data.append((menu_item, quantity_input))

        # Update the sheet with the collected data
        for i, (menu_item, quantity) in enumerate(items_data, start=1):
            cell = sheet.find(menu_item)
            column_index = len(sheet.row_values(cell.row)) + 1
            sheet.update_cell(cell.row, column_index, quantity)
            if i == 1:
                sheet.update_cell(1, column_index, current_date)

        logging.info("Items placed successfully.")

        # Update inventory after updating stocks_in sheet
        update_inventory(sheet, menu_list)

        return items_data, current_date
    except Exception as e:
        logging.error(f"An error occurred while updating the sheet: {e}")
        

def update_inventory(stocks_in_sheet, menu_list):
    """Update the inventory sheet based on the stocks_in data."""
    inventory_sheet = None
    for sheet in stocks_in_sheet.spreadsheet.worksheets():
        if sheet.title == 'inventory':
            inventory_sheet = sheet
            break

    if inventory_sheet:
        current_date = datetime.today().strftime("%Y-%m-%d")
        logging.info(f"Placing items in inventory sheet with the date: {current_date}")

        items_data = []  # List to store items and their quantities

        for menu_item in menu_list:
            stocks_in_value = stocks_in_sheet.cell(menu_list.index(menu_item) + 2, 2).value
            if stocks_in_value is None:
                stocks_in_value = 0
            items_data.append((menu_item, stocks_in_value))

        # Find the next available column
        next_column = len(inventory_sheet.row_values(1)) + 1

        # Update the sheet with the collected data
        for i, (menu_item, quantity) in enumerate(items_data, start=1):
            inventory_sheet.update_cell(i + 1, next_column, quantity)
            if i == 1:
                inventory_sheet.update_cell(1, next_column, current_date)

        logging.info("Inventory updated successfully.")
    else:
        logging.error("Inventory sheet not found.")


def main():
    try:
        gspread_client = authenticate_google_sheets()
        spreadsheet = gspread_client.open('Inventory_of_stocks')

        # Get or create worksheets
        stocks_in_sheet = None
        delivered_sheet = None
        inventory_sheet = None
        for sheet in spreadsheet.worksheets():
            if sheet.title == 'stocks_in':
                stocks_in_sheet = sheet
            elif sheet.title == 'stocks_used':
                delivered_sheet = sheet
            elif sheet.title == 'inventory':
                inventory_sheet = sheet

        if not stocks_in_sheet:
            logging.error("Sheet 'stocks_in' not found.")
            return
        if not delivered_sheet:
            logging.error("Sheet 'stocks_used' not found.")
            return
        if not inventory_sheet:
            logging.error("Sheet 'inventory' not found.")
            return

        print("Welcome to the Inventory Management System!")
        print("This will allow you to update and manage your stocks in your pantry.")

        while True:
            print("Menu List:")
            menu_list = stocks_in_sheet.col_values(1)[1:]

            items_data, current_date = update_sheet(stocks_in_sheet, menu_list, "stocks_in")

            print(f"\nItems placed on {current_date}:")
            for item, quantity in items_data:
                print(f"{item}: {quantity}")
            
            print("\nWhat would you like to do next?")
            print("1. Exit the program")
            print("2. Edit the data input")
            print("3. Proceed to update 'stocks_used'")
            
            choice = input("Enter your choice (1/2/3): ")
            if choice == '1':
                print("Thank you for using the Inventory Management System. Goodbye!")
                return
            elif choice == '2':
                continue
            elif choice == '3':
                break
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")

        while True:
            print("\nMenu List for 'stocks_used':")
            print("\n".join(menu_list))
            items_data, current_date = update_sheet(delivered_sheet, menu_list, "stocks_used")

            print(f"\nItems used on {current_date}:")
            for item, quantity in items_data:
                print(f"{item}: {quantity}")
            
            print("\nWhat would you like to do next?")
            print("1. Exit the program")
            print("2. Edit the data input")
            print("3. Finish updating 'stocks_used' and proceed to inventory calculation")
            
            choice = input("Enter your choice (1/2/3): ")
            if choice == '1':
                print("Thank you for using the Inventory Management System. Goodbye!")
                return
            elif choice == '2':
                continue
            elif choice == '3':
                break
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")

        # Calculate the difference and update the "inventory" sheet
        update_inventory(stocks_in_sheet, menu_list)

        # Display the inventory list
        inventory_list = inventory_sheet.get_all_values()
        print("\nInventory List:")
        for row in inventory_list:
            print(row)

        print("Thank you for using the Inventory Management System. Goodbye!")
    
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()


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
        return items_data, current_date
    except Exception as e:
        logging.error(f"An error occurred while updating the sheet: {e}")


def update_stocks_used(sheet, menu_list):
    """Update a sheet with quantity information for stocks_used."""
    current_date = datetime.today().strftime("%Y-%m-%d")
    print(f"Placing items in stocks_used sheet with the date: {current_date}")

    items_data = []  # List to store items and their quantities

    for menu_item in menu_list:
        while True:
            quantity_input = input(f"Enter quantity used for {menu_item}: ")
            if quantity_input.isdigit():
                quantity_input = int(quantity_input)
                items_data.append((menu_item, quantity_input))
                break
            else:
                print("Error: Quantity should be a whole number (including 0). Please try again.")

    print("Items placed successfully.")
    return items_data, current_date  # Return the items data and current date

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
        inventory_values = []
        for i, item in enumerate(menu_list, start=1):
            stocks_in_value = stocks_in_sheet.cell(i + 1, 2).value
            stocks_used_value = delivered_sheet.cell(i + 1, 2).value

            if stocks_in_value is None:
                stocks_in_value = 0
            if stocks_used_value is None:
                stocks_used_value = 0

            difference = int(stocks_in_value) - int(stocks_used_value)
            inventory_values.append([item, difference])

        inventory_sheet.clear()
        inventory_sheet.append_rows([["Quatntity left in the stockroom"]] + inventory_values)

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

    
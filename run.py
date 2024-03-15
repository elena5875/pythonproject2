#run.py
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

def authenticate_google_sheets():
    """Authenticate with Google Sheets using service account credentials."""
    SCOPE = ["https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive.file",
             "https://www.googleapis.com/auth/drive"]
    CREDS = Credentials.from_service_account_file('creds.json')
    scoped_credentials = CREDS.with_scopes(SCOPE)
    gspread_client = gspread.authorize(scoped_credentials)
    return gspread_client

def update_sheet(sheet, menu_item, quantity_type):
    """Update a sheet with quantity information."""
    try:
        cell = sheet.find(menu_item)
    except gspread.exceptions.CellNotFound:
        sheet.append_row([menu_item, 0])
        cell = sheet.find(menu_item)

    column_index = len(sheet.row_values(cell.row)) + 1

    while True:
        quantity_input = input(f"Enter {quantity_type} quantity for {menu_item}: ")
        if quantity_input.isdigit():
            quantity_input = int(quantity_input)
            break
        else:
            print("Error: Quantity should be a positive integer.")

    current_date = date.today().strftime("%Y-%m-%d")

    sheet.update_cell(cell.row, column_index, quantity_input)
    sheet.update_cell(1, column_index, current_date)

    print(f"{menu_item} updated on {current_date}")

def calculate_inventory(stocks_in_sheet, delivered_sheet, menu_list):
    """Calculate inventory values."""
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

    return inventory_values

def main():
    gspread_client = authenticate_google_sheets()
    spreadsheet = gspread_client.open('Inventory_of_stocks')
    stocks_in_sheet = spreadsheet.worksheet('stocks_in')
    delivered_sheet = spreadsheet.worksheet('stocks_used')

    try:
        inventory_sheet = spreadsheet.add_worksheet(title='inventory', rows='100', cols='20')
    except gspread.exceptions.APIError:
        inventory_sheet = spreadsheet.worksheet('inventory')

    print("Welcome to the Inventory Management System!")
    print("This will allow you to update and manage your stocks in your pantry.")

    while True:
        print("Menu List:")
        menu_list = stocks_in_sheet.col_values(1)[1:]

        for i, item in enumerate(menu_list, start=1):
            print(f"{i}. {item}")
        print(f"{len(menu_list) + 1}. Exit")

        try:
            choice = int(input("Choose a menu item (Enter the number): "))
            if choice == len(menu_list) + 1:
                print("Exiting the Inventory Management System. Goodbye!")
                break
            elif 1 <= choice <= len(menu_list):
                update_sheet(stocks_in_sheet, menu_list[choice - 1], "stocks_in")
                update_sheet(delivered_sheet, menu_list[choice - 1], "stocks_used")
            else:
                print("Invalid choice. Enter a valid menu item number.")

        except ValueError:
            print("Error: Invalid input. Please enter a valid number.")

        continue_input = input("Do you want to continue? (yes/no): ").lower()
        if continue_input != 'yes':
            inventory_values = calculate_inventory(stocks_in_sheet, delivered_sheet, menu_list)
            # Update the "inventory" sheet with inventory values
            update_inventory_sheet(inventory_sheet, inventory_values)
            # Display the inventory list
            display_inventory(inventory_sheet)
            break

if __name__ == "__main__":
    main()

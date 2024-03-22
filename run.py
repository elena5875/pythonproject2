#run.py
import gspread
from google.oauth2.service_account import Credentials
from datetime import date
import datetime

def authenticate_google_sheets():
    """Authenticate with Google Sheets using service account credentials."""
    SCOPE = ["https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive.file",
             "https://www.googleapis.com/auth/drive"]
    CREDS = Credentials.from_service_account_file('creds.json')
    scoped_credentials = CREDS.with_scopes(SCOPE)
    gspread_client = gspread.authorize(scoped_credentials)
    return gspread_client

# Function to update stock in or stock used
def update_sheet(sheet, menu_list, quantity_type):
    print(f"Updating {quantity_type}:")
    data = []
    for item in menu_list:
        while True:
            try:
                quantity_input = input(f"Enter {quantity_type} quantity for {item}: ")
                quantity = int(quantity_input) if quantity_input.isdigit() and int(quantity_input) >= 0 else 0
                break
            except ValueError:
                print("Error: Quantity should be a non-negative integer.")
        data.append([item, quantity])

    # Update the Google Sheet
    for row, (item, quantity) in enumerate(data, start=2):
        sheet.update_cell(row, 2, quantity)

    print(f"{quantity_type.capitalize()} updated.")


# Function to calculate inventory by subtracting stocks_used from stocks_in
def calculate_inventory(stocks_in_sheet, stocks_used_sheet):
    inventory_values = []
    stocks_in_data = stocks_in_sheet.get_all_values()[1:]
    stocks_used_data = stocks_used_sheet.get_all_values()[1:]

    for stock_in, stock_used in zip(stocks_in_data, stocks_used_data):
        item = stock_in[0]
        stock_in_quantity = int(stock_in[1]) if stock_in[1].isdigit() else 0
        stock_used_quantity = int(stock_used[1]) if stock_used[1].isdigit() else 0
        difference = stock_in_quantity - stock_used_quantity
        inventory_values.append([item, max(0, difference)])

    return inventory_values


# Function to update inventory sheet with inventory values
def update_inventory_sheet(inventory_sheet, inventory_values):
    inventory_sheet.clear()
    inventory_sheet.append_row(["Item", "Inventory"])
    for item, quantity in inventory_values:
        inventory_sheet.append_row([item, quantity])

# Function to display inventory data
def print_inventory_data(inventory_sheet):
    print("Inventory data:")
    data = inventory_sheet.get_all_values()[1:]
    for item, quantity in data:
        print(f"{item}: {quantity}")

# Function to update inventory with calculated values
def update_inventory_sheet(inventory_sheet, inventory_values):
    inventory_sheet.clear()
    inventory_sheet.append_row(["Item", "Inventory"])
    for item, quantity in inventory_values:
        inventory_sheet.append_row([item, quantity])

# Function to display inventory
def display_inventory(inventory_sheet):
    inventory_data = inventory_sheet.get_all_values()
    for row in inventory_data:
        print("\t".join(row))

# Function to monitor stock supply in the warehouse
def monitor_stock_supply(stocks_in_sheet, inventory_sheet):
    try:
        stocks_in_data = stocks_in_sheet.get_all_values()[1:]
        inventory_data = inventory_sheet.get_all_values()[1:]
        
        print("Stock Supply in Warehouse:")
        for item_in, quantity_in in stocks_in_data:
            for item_inv, quantity_inv in inventory_data:
                if item_in == item_inv:
                    total_stock = int(quantity_in) + int(quantity_inv)
                    print(f"{item_in}: {total_stock} units available")
                    break
    except gspread.exceptions.APIError as e:
        print("Error fetching data:", e)
        
# Function to validate user choice
def validate_choice(choice):
    valid_choices = ['1', '2', '3', '4', '5']
    return choice in valid_choices



# Update main() function to include monitoring stock supply
def main():
    gspread_client = authenticate_google_sheets()
    spreadsheet = gspread_client.open('Inventory_of_stocks')
    stocks_in_sheet = spreadsheet.worksheet('stocks_in')
    stocks_used_sheet = spreadsheet.worksheet('stocks_used')
    inventory_sheet = spreadsheet.worksheet('inventory')
    updated_stocks_sheet = spreadsheet.worksheet('updated_stocks')

    menu_list = ["FLOUR", "SUGAR", "EGG", "MILK", "COFFEE", "RICE"]

    print("Welcome to the Warehouse Management System!")

    while True:
        print("Menu:")
        print("1. Update stock in")
        print("2. Update stocks used")
        print("3. Update inventory")
        print("4. Monitor stock supply")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if validate_choice(choice):
            if choice == '1':
                update_sheet(stocks_in_sheet, menu_list, "stock in")
                print("Updated stocks in:")
                for item in menu_list:
                    print(f"{item}: {stocks_in_sheet.acell('B' + str(menu_list.index(item) + 2)).value}")
            elif choice == '2':
                update_sheet(stocks_used_sheet, menu_list, "stocks used")
                print("Updated stocks used:")
                for item in menu_list:
                    print(f"{item}: {stocks_used_sheet.acell('B' + str(menu_list.index(item) + 2)).value}")
            elif choice == '3':
                inventory_values = calculate_inventory(stocks_in_sheet, stocks_used_sheet)
                update_inventory_sheet(inventory_sheet, inventory_values)
                print_inventory_data(inventory_sheet)
            elif choice == '4':
                monitor_stock_supply(stocks_in_sheet, inventory_sheet)
            elif choice == '5':
                print("Thank you for using the Warehouse Management System. Have a nice day!")
                break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    main()

    
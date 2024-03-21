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

# Function to update stock in or stock used
def update_sheet(sheet, menu_list, quantity_type):
    print(f"Updating {quantity_type}:")
    data = []
    for item in menu_list:
        while True:
            try:
                quantity_input = int(input(f"Enter {quantity_type} quantity for {item}: "))
                if quantity_input >= 0:
                    break
                else:
                    print("Error: Quantity should be a non-negative integer.")
            except ValueError:
                print("Error: Quantity should be a positive integer.")
        data.append([item, quantity_input])

    # Update the Google Sheet
    for row, (item, quantity) in enumerate(data, start=2):
        sheet.update_cell(row, 2, quantity)

    print(f"{quantity_type.capitalize()} updated.")

# Function to display the data for the user to see
def print_data(sheet, menu_list, quantity_type):
    print(f"{quantity_type.capitalize()} data:")
    data = sheet.get_all_values()[1:]
    for item, quantity in zip(menu_list, data):
        print(f"{item}: {quantity[1]}")


# Function to calculate inventory
def calculate_inventory(stocks_in_sheet, delivered_sheet):
    inventory_values = []
    stocks_in_values = stocks_in_sheet.get_all_values()[1:]
    delivered_values = delivered_sheet.get_all_values()[1:]

    for stock_in, delivered in zip(stocks_in_values, delivered_values):
        item = stock_in[0]
        stock_in_quantity = int(stock_in[1]) if stock_in[1].isdigit() else 0
        delivered_quantity = int(delivered[1]) if delivered[1].isdigit() else 0
        inventory_values.append([item, stock_in_quantity - delivered_quantity])

    return inventory_values

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
        print("4. Update inventory with the latest stock in")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            update_sheet(stocks_in_sheet, menu_list, "stock in")
            print_data(stocks_in_sheet, menu_list, "stock in")
        elif choice == '2':
            update_sheet(stocks_used_sheet, menu_list, "stocks used")
            print_data(stocks_used_sheet, menu_list, "stocks used")
        elif choice == '3':
            print_data(stocks_in_sheet, menu_list, "stock in")
            print_data(stocks_used_sheet, menu_list, "stocks used")
        elif choice == '4':
            # Update inventory with the latest stock in
            pass
        elif choice == '5':
            print("Thank you for using the Warehouse Management System. Have a nice day!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    main()

    
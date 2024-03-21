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
    print("Menu List:")
    for i, item in enumerate(menu_list, start=1):
        print(f"{i}. {item}")

    while True:
        try:
            choice = int(input("Choose an item number to update (Enter the number): "))
            if 1 <= choice <= len(menu_list):
                menu_item = menu_list[choice - 1]
                break
            else:
                print("Invalid choice. Enter a valid menu item number.")
        except ValueError:
            print("Error: Invalid input. Please enter a valid number.")

    try:
        cell = sheet.find(menu_item)
    except gspread.exceptions.CellNotFound:
        sheet.append_row([menu_item, 0])
        cell = sheet.find(menu_item)

    while True:
        quantity_input = input(f"Enter {quantity_type} quantity for {menu_item}: ")
        if quantity_input.isdigit():
            quantity_input = int(quantity_input)
            break
        else:
            print("Error: Quantity should be a positive integer. Setting quantity to 0.")
            quantity_input = 0
            break

    sheet.update_cell(cell.row, 2, quantity_input)
    print(f"{menu_item} {quantity_type} updated.")

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
    delivered_sheet = spreadsheet.worksheet('stocks_used')

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
            print("Updating Stock In:")
            update_sheet(stocks_in_sheet, menu_list, "stock in")
            print("Stock in updated.")
        elif choice == '2':
            print("Updating Stocks Used:")
            update_sheet(delivered_sheet, menu_list, "stocks used")
            print("Stocks used updated.")
        elif choice == '3':
            print("Updating Inventory:")
            inventory_values = calculate_inventory(stocks_in_sheet, delivered_sheet)
            update_inventory_sheet(spreadsheet.worksheet('inventory'), inventory_values)
            print("Inventory updated.")
            display_inventory(spreadsheet.worksheet('inventory'))
        elif choice == '4':
            update_choice = input("Do you want to update the inventory with the latest stock in? (yes/no): ")
            if update_choice.lower() == 'yes':
                inventory_values = calculate_inventory(stocks_in_sheet, delivered_sheet)
                update_inventory_sheet(spreadsheet.worksheet('inventory'), inventory_values)
                print("Inventory updated with the latest stock in.")
                display_inventory(spreadsheet.worksheet('inventory'))
            else:
                print("Inventory not updated.")
        elif choice == '5':
            print("Thank you for using the Warehouse Management System. Have a nice day!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    main()

    
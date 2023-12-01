import gspread
from google.oauth2.service_account import Credentials
from datetime import date

# Set up Google Sheets authentication
SCOPE = ["https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]
CREDS = Credentials.from_service_account_file('creds.json')
scoped_credentials = CREDS.with_scopes(SCOPE)
gspread_client = gspread.authorize(scoped_credentials)
spreadsheet = gspread_client.open('Inventory_of_stocks')
stocks_in_sheet = spreadsheet.worksheet('stocks_in')
delivered_sheet = spreadsheet.worksheet('stocks_used')

# Create or get the "inventory" sheet
try:
    inventory_sheet = spreadsheet.add_worksheet(title='inventory', rows='100', cols='20')
except gspread.exceptions.APIError:
    inventory_sheet = spreadsheet.worksheet('inventory')

# Function to update a sheet with quantity information
def update_sheet(sheet, menu_item, quantity_type):
    try:
        cell = sheet.find(menu_item)
    except gspread.exceptions.CellNotFound:
        sheet.append_row([menu_item, 0])
        cell = sheet.find(menu_item)

    column_index = len(sheet.row_values(cell.row)) + 1

    quantity_input = int(input(f"Enter {quantity_type} quantity for {menu_item}:"))
    current_date = date.today().strftime("%Y-%m-%d")

    sheet.update_cell(cell.row, column_index, quantity_input)
    sheet.update_cell(1, column_index, current_date)

    print(f"{menu_item} updated on {current_date}")

# Display a welcome message
print("Welcome to the Inventory Management System!")
print("This will allow you to update and manage your stocks in your pantry.")

# Main loop for user interaction
while True:
    print("Menu List:")
    menu_list = stocks_in_sheet.col_values(1)[1:]

    for i, item in enumerate(menu_list, start=1):
        print(f"{i}. {item}")
    print(f"{len(menu_list) + 1}. Exit")

    choice = int(input("Choose a menu item (Enter the number):"))

    # Check if the user chose the "Exit" option
    if choice == len(menu_list) + 1:
        print("Exiting the Inventory Management System. Goodbye!")
        break

    # Update "stocks_in" and "stocks_used" sheets based on the user's choice
    if 1 <= choice <= len(menu_list):
        update_sheet(stocks_in_sheet, menu_list[choice - 1], "stocks_in")
        update_sheet(delivered_sheet, menu_list[choice - 1], "stocks_used")
    else:
        print("Invalid choice. Enter a valid menu item number.")

    # Ask the user if they want to continue
    continue_input = input("Do you want to continue? (yes/no): ").lower()
    if continue_input != 'yes':
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
        break



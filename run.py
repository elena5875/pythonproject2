import gspread
from google.oauth2.service_account import Credentials
from datetime import date

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

CREDS = Credentials.from_service_account_file('creds.json')

scoped_credentials = CREDS.with_scopes(SCOPE)
gspread_client = gspread.authorize(scoped_credentials)
spreadsheet = gspread_client.open('Inventory_of_stocks')
stocks_in_sheet = spreadsheet.worksheet('stocks_in')
delivered_sheet = spreadsheet.worksheet('delivered')

    #define update sheet
def update_sheet(sheet, menu_item, quantity_type):
    quantity_input = int(input(f"Please enter the quantity for {quantity_type} - {menu_item}:"))
    current_date = date.today().strftime("%Y-%m-%d")


    cell = sheet.find(menu_item)
    column_index = len(sheet.row_values(cell.row)) + 1
    sheet.update_cell(cell.row, column_index, quantity_input)
    sheet.update_cell(1, column_index, current_date)

    print(f"{menu_item} updated on {current_date}")


def update_inventory():
    # Display menu list from Stocks-In sheet
    menu_list = stocks_in_sheet.col_values(1)[1:]
    print("Menu List:")
    for i, item in enumerate(menu_list, start=1):
        print(f"{i}. {item}")

    choice = int(input("Choose a menu item Please enter the number: "))

    
    if choice < 1 or choice > len(menu_list):
        print("Invalid choice. Please enter a valid menu item number.")
        return

    # Update stocks_in sheet
    update_sheet(stocks_in_sheet, menu_list[choice - 1], "stocks_in")

    # Update delivered sheet
    update_sheet(delivered_sheet, menu_list[choice - 1], "delivered")


update_inventory()
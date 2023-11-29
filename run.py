import gspread
from google.oauth2.service_account import Credentials
from datetime import date

SCOPE = ["https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]
CREDS = Credentials.from_service_account_file('creds.json')
scoped_credentials = CREDS.with_scopes(SCOPE)
gspread_client = gspread.authorize(scoped_credentials)
spreadsheet = gspread_client.open('Inventory_of_stocks')
stocks_in_sheet = spreadsheet.worksheet('stocks_in')
delivered_sheet = spreadsheet.worksheet('stocks_used')

#define update sheet with date
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

    #display the menu list
    menu_list = stocks_in_sheet.col_values(1)[1:]
    print("Menu List:")
    for i, item in enumerate(menu_list, start=1):
        print(f"{i}. {item}")

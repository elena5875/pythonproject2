import gspread
from google.oauth2.service_account import Credentials
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

credentials = Credentials.from_service_account_file('creds.json')

scoped_credentials = credentials.with_scopes(SCOPE)
gspread_client = gspread.authorize(scoped_credentials)
spreadsheet = gspread_client.open('Inventory_of_stocks')
stocks_in_sheet = spreadsheet.worksheet('stocks_in')
delivered_sheet = spreadsheet.worksheet('delivered')

def update_inventory():
    # Display menu list from Stocks-In sheet
    menu_list = stocks_in_sheet.col_values(1)[1:] 
    print("Menu List:")
    for i, item in enumerate(menu_list, start=1):
        print(f"{i}. {item}")

    
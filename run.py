
import gspread
from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]
    
CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('Inventory_of_stocks').sheet1

#Get the items in the sheet columns

products = SHEET.col_values(1)[1:]


# Function to display the menu
def display_menu():
    print("Menu:")
    for i, product in enumerate(products, start=1):
        print(f"{i}. {product}")

# Function to add stock
def add_stock(product, quantity):
    # Check if the product is already in the sheet
    if product in products:
        # Get the index of the product in the list
        index = products.index(product) + 1  # Adjusted to start from index 1
        # Get the current quantity and add the new quantity
        current_quantity = int(SHEET.cell(index, 2).value)
        new_quantity = current_quantity + quantity
        # Update the sheet with the new quantity
        sheet.update_cell(index, 2, str(new_quantity))
    else:
        # If the product is not in the sheet, add a new row
        sheet.append_row([product, quantity])

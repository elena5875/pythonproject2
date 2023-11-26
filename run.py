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
        index = products.index(product) + 1  
        current_quantity = int(SHEET.cell(index, 2).value)
        new_quantity = current_quantity + quantity
        # Update the sheet with the new quantity
        sheet.update_cell(index, 2, str(new_quantity))
    else:
        # If the product is not in the sheet, add a new row
        sheet.append_row([product, quantity])

# Function to add delivery
def update_delivery(product, delivered_quantity):
    # Check if the product is in the sheet
    if product in products:
        # Get the index of the product in the list
        index = products.index(product) + 1  
        current_quantity = int(sheet.cell(index, 2).value)
        new_quantity = max(current_quantity - delivered_quantity, 0)
        # Update the sheet with the new quantity
        sheet.update_cell(index, 2, str(new_quantity))
    else:
        print(f"Product '{product}' not found in the inventory.")

# Function for inventory
def check_inventory(product):
    # Check if the product is in the sheet
    if product in products:
        # Get the index of the product in the list
        index = products.index(product) + 1  
        current_quantity = int(sheet.cell(index, 2).value)
        print(f"Current inventory of {product}: {current_quantity}")
    else:
        print(f"Product '{product}' not found in the inventory.")
        
# Main program
while True:
    display_menu()
    print("Enter the number corresponding to the product (0 to exit): ")
    choice = input()

    if choice == '0':
        break

    try:
        # Convert the choice to an integer and subtract 1 to get the index
        choice_index = int(choice) - 1
        selected_product = products[choice_index]
    except (ValueError, IndexError):
        print("Invalid choice. Please enter a valid number.")
        continue
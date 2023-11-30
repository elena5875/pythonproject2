import gspread
from google.oauth2.service_account import Credentials
from datetime import date

# Google Sheet API setup
SCOPE = ["https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]
CREDS = Credentials.from_service_account_file('creds.json')
scoped_credentials = CREDS.with_scopes(SCOPE)
gspread_client = gspread.authorize(scoped_credentials)
spreadsheet = gspread_client.open('Inventory_of_stocks')
stocks_in_sheet = spreadsheet.worksheet('stocks_in')
stocks_used_sheet = spreadsheet.worksheet('stocks_used')

# Function to update the sheet
def update_sheet(sheet, menu_item, quantity_input, quantity_type):
    current_date = date.today().strftime("%Y-%m-%d")

    cell = sheet.find(menu_item)
    col_index = len(sheet.row_values(cell.row)) + 1
    sheet.update_cell(cell.row, col_index, quantity_input)
    sheet.update_cell(1, col_index, current_date)

    print(f"{menu_item} {quantity_type} updated on {current_date}")

# Create a menu list from "stocks_in" sheet
menu_list = stocks_in_sheet.col_values(1)[1:]

# Display the menu to the user
print("Menu List:")
for index, item in enumerate(menu_list, start=1):
    print(f"{index}. {item}")

# Add an option to exit
print(f"{len(menu_list) + 1}. Exit")

# Get user input for stocks_in
while True:
    try:
        user_choice = int(input("Choose a menu item (enter the number): "))
        
        if 1 <= user_choice <= len(menu_list):
            chosen_item = menu_list[user_choice - 1]
            print(f"You've chosen: {chosen_item}")

            # Prompt the user for quantity input for stocks_in
            while True:
                quantity_input = input(f"Enter quantity for {chosen_item} (stocks_in): ")

                # Validate the quantity input
                if quantity_input.isdigit():
                    quantity_input = int(quantity_input)
                    update_sheet(stocks_in_sheet, chosen_item, quantity_input, "Quantity Type")
                    break
                else:
                    print("Invalid quantity input. Please enter a valid integer.")
            break
        elif user_choice == len(menu_list) + 1:
            print("Exiting the program. Goodbye!")
            exit()
        else:
            print("Invalid choice. Please enter a valid number.")
    except ValueError:
        print("Invalid input. Please enter a number.")

# Get user input for stocks_used
while True:
    used_menu_list = stocks_used_sheet.col_values(1)[1:]
    used_chosen_item = menu_list[user_choice - 1]  # using the same chosen_item for simplicity

    # Prompt the user for quantity input for stocks_used
    while True:
        used_quantity_input = input(f"Enter quantity for {used_chosen_item} (stocks_used): ")

        # Validate the quantity input
        if used_quantity_input.isdigit():
            used_quantity_input = int(used_quantity_input)
            update_sheet(stocks_used_sheet, used_chosen_item, used_quantity_input, "Quantity Used")
            break
        else:
            print("Invalid quantity input. Please enter a valid integer.")
    break


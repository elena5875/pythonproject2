import gspread
from google.oauth2.service_account import Credentials
from datetime import date
from datetime import datetime


def authenticate_google_sheets():
    """Authenticate with Google Sheets using service account credentials."""
    SCOPE = ["https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive.file",
             "https://www.googleapis.com/auth/drive"]
    CREDS = Credentials.from_service_account_file('creds.json')
    scoped_credentials = CREDS.with_scopes(SCOPE)
    gspread_client = gspread.authorize(scoped_credentials)
    return gspread_client

def update_sheet(sheet, menu_list):
    """Update a sheet with quantity information for all items."""
    current_date = datetime.today().strftime("%Y-%m-%d")
    print(f"Placing items in sheet with the date: {current_date}")

    items_data = []  # List to store items and their quantities

    for menu_item in menu_list:
        while True:
            quantity_input = input(f"Enter quantity for {menu_item}: ")
            if quantity_input.isdigit():
                quantity_input = int(quantity_input)
                items_data.append((menu_item, quantity_input))
                break
            else:
                print("Error: Quantity should be a whole number (including 0). Please try again.")

    print("Items placed successfully.")
    return items_data, current_date  # Return the items data and current date


def main():
    gspread_client = authenticate_google_sheets()
    spreadsheet = gspread_client.open('Inventory_of_stocks')
    stocks_in_sheet = spreadsheet.worksheet('stocks_in')
    delivered_sheet = spreadsheet.worksheet('stocks_used')

    print("Welcome to the Inventory Management System!")
    print("This will allow you to update and manage your stocks in your pantry.")

    while True:
        print("Menu List:")
        menu_list = stocks_in_sheet.col_values(1)[1:]

        for i, item in enumerate(menu_list, start=1):
            print(f"{i}. {item}")
        print(f"{len(menu_list) + 1}. Exit")

        try:
            choice = int(input("Choose a menu item (Enter the number): "))
            if choice == len(menu_list) + 1:
                print("Thank you for using the Inventory Management System. Goodbye!")
                return  # Exiting the program gracefully
            elif 1 <= choice <= len(menu_list):
                items_data, current_date = update_sheet(stocks_in_sheet, menu_list)
                print(f"\nItems placed on {current_date}:")
                for item, quantity in items_data:
                    print(f"{item}: {quantity}")
                
                print("Task for stocks-in is done.")

                while True:
                    edit_choice = input("Do you want to edit the items' stock numbers? (yes/no): ").lower()
                    if edit_choice == 'yes':
                        break
                    elif edit_choice == 'no':
                        continue_choice = input("Do you want to continue with stocks_used? (yes/no): ").lower()
                        if continue_choice == 'yes':
                            break
                        elif continue_choice == 'no':
                            print("Thank you for using the Inventory Management System. Goodbye!")
                            return  # Exiting the program gracefully
                        else:
                            print("Invalid choice. Enter 'yes' or 'no'.")
                    else:
                        print("Invalid choice. Enter 'yes' or 'no'.")

                if edit_choice == 'yes':
                    continue

                if continue_choice == 'no':
                    print("Thank you for using the Inventory Management System. Goodbye!")
                    return  # Exiting the program gracefully
            else:
                print("Invalid choice. Enter a valid menu item number.")

        except ValueError:
            print("Error: Invalid input. Please enter a valid number.")

if __name__ == "__main__":
    main()

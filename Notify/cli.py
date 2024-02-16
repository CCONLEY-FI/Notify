from selenium.common.exceptions import WebDriverException, TimeoutException
from scraper import setup_driver, login_to_linkedin, fetch_notifications
from database_setup import Unsorted, Sorted, setup_database, Category
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from rich.console import Console
from rich.prompt import Prompt
import os
import sys
from utils import (
    session_scope,
    prompt_for_integer_input,
    prompt_for_importance_level,
    prompt_for_note,
    display_notifications
)

console = Console()

def reset_table_sequencing():
    '''
    This function resets the order of the notification IDs in the database.
    Example.  When the first item of one of our 3 tables is moved/deleted/altered, this will leave a gap in the ID order.
    this function will then reorder the IDs so that they are sequential IN THEIR RESPECTIVE TABLES.
    '''
    with session_scope() as session:
        unsorted_notifications = session.query(Unsorted).all()
        sorted_notifications = session.query(Sorted).all()
        categories = session.query(Category).all()
        
        for idx, notification in enumerate(unsorted_notifications, start=1):
            notification.id = idx
        for idx, notification in enumerate(sorted_notifications, start=1):
            notification.id = idx
        for idx, category in enumerate(categories, start=1):
            category.id = idx
        session.commit()
        console.print("[bold green]Table sequencing reset successfully.[/]")

def add_category():
    '''
    Add a new category to the database.
    '''
    category_name = console.input("[bold green]Enter the name of the category:[/] ")
    with session_scope() as session:
        new_category = Category(name=category_name)
        session.add(new_category)
        session.commit()
        console.print(f"[bold green]Category '{category_name}' added successfully.[/]")
        press_any_key_to_continue()

def remove_category():
    #console.print all categories and their ids
    with session_scope() as session:
        category_notification_count = session.query(Sorted.category_id, func.count(Sorted.category_id)).group_by(Sorted.category_id).all() # category_notification_count is a list of tuples: [(category_id, count), ...]
        categories = session.query(Category).all()
        if not categories:
            console.print("[bold red]No categories found.[/]")
            return
        for category in categories:
            console.print(f"ID: {category.id}, Name: {category.name} - {next((count for cat_id, count in category_notification_count if cat_id == category.id), 0)} notifications") # this 
    category_id = prompt_for_integer_input("[bold green]Enter the ID of the category to remove:[/] ")
    category_to_remove = session.query(Category).filter_by(id=category_id).first()
    if not category_to_remove:
        console.print("[bold red]Category not found.[/]")
        return
    affected_notifications = session.query(Sorted).filter_by(category_id=category_id).count()
    console.print(f"[bold yellow]This will affect {affected_notifications} notifications. They will be moved back to unsorted[/]")
    confirm = console.input("[bold red]Are you sure you want to remove this category? (y/n):[/] ")
    if confirm.lower() == 'y':
        affected = session.query(Sorted).filter_by(category_id=category_id).all()
        for notification in affected:
            unsorted_notification = Unsorted(
                title=notification.title,
                content=notification.content
            )
            session.add(unsorted_notification)
            session.delete(notification)
        
        session.delete(category_to_remove)
        session.commit()
        reset_table_sequencing()
        for notification in session.query(Sorted).all():
            if notification.category_id > category_id:
                notification.category_id -= 1
        session.commit()
        console.print(f"[bold green]Category '{category_to_remove.name}' removed successfully.[/]")
        press_any_key_to_continue()
    else:
        console.print("Category removal cancelled.")
    # the commented code below is the original code for removing a category by name.
    # category_name = console.input("[bold green]Enter the name of the category to remove:[/] ")
    # with session_scope() as session:
    #     category = session.query(Category).filter_by(name=category_name).first()
    #     if category:
    #         affected_notifications = session.query(Sorted).filter_by(category_id=category.id).count()
    #         console.print(f"[bold yellow]This will affect {affected_notifications} notifications. They will be moved back to unsorted[/]")
    #         confirm = console.input("[bold red]Are you sure you want to remove this category? (y/n):[/] ")
    #         if confirm.lower() == 'y':
    #             affected = session.query(Sorted).filter_by(category_id=category.id).all()
    #             for notification in affected:
    #                 unsorted_notification = Unsorted(
    #                     title=notification.title,
    #                     content=notification.content
    #                 )
    #                 session.add(unsorted_notification)
    #                 session.delete(notification)
                
    #             session.delete(category)
    #             session.commit()
    #             reset_table_sequencing()
    #             console.print(f"[bold green]Category '{category_name}' removed successfully.[/]")
    #         else:
    #             console.print("Category removal cancelled.")
    #     else:
    #         console.print(f"[bold red]Category '{category_name}' not found.[/]")          
    
def press_any_key_to_continue():
    console.print(
        "[bold green]                Press any key to continue...[/bold green]")
    input()

def display_splash_screen():
    # Notify This stylized ASCII text
    splash_screen = """
    [bold magenta]
    ███╗   ██╗ ██████╗ ████████╗████████╗███████╗██╗   ██╗
    ██╔██╗ ██║██╔═══██╗╚══██╔══╝╚══██╔══╝██╔════╝╚██╗ ██╔╝
    ██║╚██╗██║██║   ██║   ██║      ██║   █████╗   ╚████╔╝
    ██║ ╚████║██║   ██║   ██║      ██║   ██╔══╝    ╚██╔╝
    ██║  ╚███║╚██████╔╝   ██║   ████████╗██║        ██║   
    ╚═╝   ╚══╝ ╚═════╝    ╚═╝   ╚═══════╝╚═╝        ╚═╝
    [/bold magenta]
    """

    console.print(splash_screen)
    press_any_key_to_continue()

def main_menu():
    '''
    Display the main menu and prompt the user for a choice.
    Returns: str(The user's choice.)
    '''
    while True:
        console.print(
            "\n[bold magenta]                    | Main Menu |[/bold magenta]")
        menu = """
             ----------------------------
            | 1. Display Notifications   |
            | 2. Fetch All Notifications |
            | 3. Modify Notifications    |
            | 4. Exit                    |
             ----------------------------
        """
        console.print(menu, style="bold yellow")  # Display the menu
        choice = Prompt.ask("[bold green]Enter choice[/bold green]",
                            choices=["1", "2", "3", "4"], default="1")
        return choice

def display_notifications_menu():
    '''
    Display the notifications menu and prompt the user for a choice.
    works as a sub-menu for the main menu to choose either to display unsorted or sorted notifications.
    '''
    console.print(
        "\n[bold magenta]                                            | Display Notifications |[/bold magenta]")
    menu = """                         **** Choose to display either unsorted or sorted notifications. ****
             --------------------------------------------------------------------------------------------
            | 1. Display Unsorted Notifications -- View notifications that have not been categorized yet.|
            | 2. Display Sorted Notifications -- View notifications that have been categorized.          |
            | 3. Go Back                                                                                 |
             --------------------------------------------------------------------------------------------
            """
    console.print(menu, style="bold yellow")
    choice = Prompt.ask("[bold green]Enter choice[/bold green]",
                        choices=["1", "2", "3"], default="1")
    if choice == "1":
        display_unsorted_notifications()
    elif choice == "2":
        display_sorted_notifications()
    elif choice == "3":
        return

def modify_notifications_menu():
    '''
    Display the modify notifications menu and prompt the user for a choice.
    then it works as a sub-menu for the main menu to choose either to categorize, update notes, or delete notifications.
    or to go back to the main menu.
    '''
    console.print(
        "\n[bold magenta]                                      | Modify Notifications |[/bold magenta]")
    menu = """
                        **** Choose an action to perform on the notifications. ****
         -----------------------------------------------------------------------------------------
        | 1. Categorize Unsorted Notifications -- Categorize newly fetched notifications.         |
        | 2. Update Notes -- Update the notes for sorted notifications.                           |
        | 3. Delete Notifications -- Delete notifications from either the unsorted or sorted list.|
        | 4. Add Category -- Add a new category.                                                  |
        | 5. Remove Category -- Remove a category.                                                |
        | 6. Go Back                                                                              |    
         -----------------------------------------------------------------------------------------
        """
    console.print(menu, style="bold yellow")
    choice = Prompt.ask("[bold green]Enter choice[/bold green]",
                        choices=["1", "2", "3", "4", "5", "6"], default="1")
    if choice == "1":
        categorize_notifications_cli()
    elif choice == "2":
        update_notes_cli()
    elif choice == "3":
        delete_notifications_menu()
    elif choice == "4":
        add_category()
    elif choice == "5":
        remove_category()
    elif choice == "6":
        return

def delete_notifications_menu():
    '''
    Display the delete notifications menu and prompt the user for a choice.
    then it works as a sub-menu for the modify notifications menu to choose either to delete from sorted list,
    delete from unsorted list, delete all unsorted notifications, or to go back to the modify notifications menu.
    '''
    console.print(
        "\n[bold magenta]                      Delete Notifications[/bold magenta]")
    menu = """
                     ****Choose the type of list to delete notifications from.****
         ---------------------------------------------------------------------------------------------
        | 1. Delete from Sorted List -- Delete notifications that have already been categorized.      |
        | 2. Delete from Unsorted List -- Delete notifications that have not been categorized yet.    |
        | 3. Delete All Unsorted Notifications -- Delete all notifications from the unsorted list.    |
        | 4. Delete All Sorted Notifications -- Delete all notifications from the sorted list.        |
        | 5. Go Back                                                                                  |
         ---------------------------------------------------------------------------------------------
        """
    console.print(menu, style="bold yellow")
    choice = Prompt.ask("[bold green]Enter choice[/bold green]",
                        choices=["1", "2", "3", "4", "5"], default="1")
    if choice == "1":
        delete_notification_cli(sorted=True)
    elif choice == "2":
        delete_notification_cli(sorted=False)
    elif choice == "3":
        delete_all_unsorted_notifications()
    elif choice == "4":
        delete_all_sorted_notifications()
    elif choice == "5":
        return

def fetch_notifications_cli():
    '''
    Fetch notifications from LinkedIn via scraper and save them to the database.
    '''
    email = console.input("[bold green]Enter your LinkedIn email:[/] ")
    password = console.input(
        "[bold green]Enter your LinkedIn password (input will be hidden):[/]", password=True)
    driver = None
    try:
        driver = setup_driver()
        login_success = login_to_linkedin(driver, email, password)
        if login_success:
            console.print("[bold green]Logged in successfully.[/]")
            fetch_notifications(driver)
        else:
            console.print(
                "[bold red]Login failed. Please check your credentials.[/]")
    except TimeoutException:
        console.print(
            "[bold red]Timeout occurred while trying to access LinkedIn.[/]")
    except WebDriverException as e:
        console.print(f"[bold red]Web driver error occurred: {e}[/]")
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred: {e}[/]")
    finally:
        if driver:
            driver.quit()

def display_sorted_notifications():
    '''helper function to display sorted notifications.'''
    with session_scope() as session:
        notifications = session.query(Sorted).all()
        display_notifications(notifications, sorted=True)

def display_unsorted_notifications():
    '''helper function to display unsorted notifications.'''
    with session_scope() as session:
        notifications = session.query(Unsorted).all()
        display_notifications(notifications)

def categorize_notifications_cli():
    '''
    Categorize unsorted notifications and save them to the database.
    This also removes the categorized notifications from the unsorted list while adding them to the sorted list.
    '''
    with session_scope() as session:
        offset = 0 # offset for pagination
        batch_size = 5  # amount of notifications to display at a time
        while True:
            # Fetch a batch of unsorted notifications
            unsorted_notifications = session.query(Unsorted).offset(offset).limit(batch_size).all()
            if not unsorted_notifications:
                console.print("[bold red]No more unsorted notifications to display.[/]")
                break

            # Display the notifications using the utility function
            display_notifications(unsorted_notifications)

            # Prompt the user for a choice
            console.print("[bold green]Enter the number of the notification to categorize, 'n' for next page, or 'm' to return to Main Menu:[/]")
            choices = [str(i) for i in range(1, len(unsorted_notifications) + 1)] + ['n', 'm']
            choice = Prompt.ask("", choices=choices)

            # Handle pagination and returning to the main menu
            if choice.lower() == 'n':
                offset += batch_size
                continue
            elif choice.lower() == 'm':
                break

            # At this point, choice should be a notification number, so we can proceed to categorize
            selected_index = int(choice) - 1
            selected_notification = unsorted_notifications[selected_index]

            # Categorize the notification
            categories = session.query(Category).all()
            if not categories:
                console.print("[bold red]No categories found. Please add a category first.[/]")
                return # Exit the function
            
            for idx, category in enumerate(categories, start=1):
                console.print(f"{idx}. {category.name}")
            category_index = prompt_for_integer_input("select the category number: ")
            if not (1 <= category_index <= len(categories)):
                console.print("[bold red]Invalid category number. Please try again.[/]")
                continue # Restart the loop
            selected_category = categories[category_index - 1]
            
            importance_level = prompt_for_importance_level()
            note = prompt_for_note()

            # Create a new Sorted instance and update the database
            sorted_notification = Sorted(
                title=selected_notification.title,
                content=selected_notification.content,
                category_id=selected_category.id,
                importance_level=importance_level,
                note=note,
                notification_id=selected_notification.id
            )
            session.add(sorted_notification)
            session.delete(selected_notification)
            session.commit()
            reset_table_sequencing()
            console.print("[bold green]Notification categorized successfully.[/]")
            press_any_key_to_continue()

def update_notes_cli():
    '''
    Update the user's custom notes for sorted notifications and save them to the database.
    '''
    with session_scope() as session:
        offset = 0
        batch_size = 5
        while True:
            sorted_notifications = session.query(
                Sorted).offset(offset).limit(batch_size).all()
            if not sorted_notifications:
                console.print("[bold red]No more notifications to display.[/]")
                break

            # Display the notifications with their index and title
            for i, notification in enumerate(sorted_notifications, start=1):
                console.print(
                    f"{i}. {notification.title}: current note: {notification.note}")

            # Generate a list of valid choices based on the notifications displayed
            valid_choices = [str(i) for i in range(
                1, len(sorted_notifications) + 1)]
            valid_choices.append('m')
            console.print("[bold green]Enter the number of the notification to update the note, or 'm' to return to Main Menu:[/]")
            choice = Prompt.ask("", choices=valid_choices, default="m")

            # Handle returning to the main menu
            if choice.lower() == 'm':
                return

            # Convert the choice to an integer index and update the note
            try:
                choice_index = int(choice) - 1
                if 0 <= choice_index < len(sorted_notifications):
                    selected_notification = sorted_notifications[choice_index]
                    note = prompt_for_note()
                    selected_notification.note = note
                    session.commit()
                    press_any_key_to_continue()
                    console.print("[bold green]Note updated successfully.[/]")
                else:
                    console.print("[bold red]Invalid choice. Please try again.[/]")
            except ValueError:
                console.print("[bold red]Please enter a valid number.[/]")

def delete_notification_cli(sorted=False):
    '''
    Delete a notification from the database.
    or to delete all unsorted notifications.
    '''
    with session_scope() as session:
        try:
            if sorted:
                notifications = session.query(Sorted).all()
            else:
                notifications = session.query(Unsorted).all()
            if not notifications:
                console.print("[bold red]No notifications to delete.[/]")
                return
            for notification in notifications:
                console.print(f"ID: {notification.id}, Title: {notification.title}")
            notification_id = prompt_for_integer_input("[bold green]Enter the ID of the notification to delete:[/] ")
            notification_to_delete = session.query(
                Sorted if sorted else Unsorted).filter_by(id=notification_id).first()
            if not notification_to_delete:
                console.print("Notification not found.", style="bold red")
                return
            session.delete(notification_to_delete)
            session.commit()
            reset_table_sequencing()
            press_any_key_to_continue()
            console.print("Notification deleted successfully.",style="bold green")
        except SQLAlchemyError as e:
            console.print(f"An error occurred: {e}", style="bold red")
        except Exception as e:
            console.print(f"An error occurred: {e}", style="bold red")

def delete_all_unsorted_notifications():
    '''helper function to delete all unsorted notifications.
    used in the delete_notifications_menu function.'''
    with session_scope() as session:
        try:
            session.query(Unsorted).delete()
            session.commit()
            press_any_key_to_continue()
            console.print("[bold green]All unsorted notifications deleted successfully.[/]")
        except SQLAlchemyError as e:
            console.print(f"An error occurred: {e}", style="bold red")
        except Exception as e:
            console.print(f"An error occurred: {e}", style="bold red")

def delete_all_sorted_notifications():
    '''helper function to delete all sorted notifications. used in the delete_notifications_menu function.'''
    with session_scope() as session:
        try:
            session.query(Sorted).delete()
            session.commit()
            press_any_key_to_continue
            console.print("[bold green]All sorted notifications deleted successfully.[/]")
        except SQLAlchemyError as e:
            console.print(f"An error occurred: {e}", style="bold red")
        except Exception as e:
            console.print(f"An error occurred: {e}", style="bold red")

def main():
    setup_database()  # Ensure the database is setup
    os.system('clear') # Clear the console so that the splash screen is displayed cleanly
    display_splash_screen() # Display the splash screen
    while True:
        choice = main_menu()
        if choice == "1":
            display_notifications_menu()
        elif choice == "2":
            fetch_notifications_cli()
        elif choice == "3":
            modify_notifications_menu()
        elif choice == "4":
            console.print("[bold red]Exiting...[/bold red]")
            sys.exit()
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__": # Run the main function if this script is executed
    main()

# utils.py
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from rich.console import Console
from rich.table import Table
from rich import print as rprint
import config

console = Console()

@contextmanager
def session_scope():
    """
    Provides a transactional scope around a series of operations.
    """
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=create_engine(config.DATABASE_URI))
    session = session_local()
    try:
        yield session
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        console.print(f"[bold red]Database error occurred:[/] {e}", style="red")
        raise
    except Exception as e:
        session.rollback()
        console.print(f"[bold red]An error occurred:[/] {e}", style="red")
        raise
    finally:
        session.close()
        
def prompt_for_integer_input(prompt_message):
    """
    Prompts the user for an integer input. Re-prompts until a valid integer is provided.
    Args:
        prompt_message (str): The message to display to the user.
    Returns:
        int: The valid integer input.
    """
    while True:
        user_input = console.input(prompt_message)
        try:
            return int(user_input)
        except ValueError:
            console.print("[bold red]Invalid input. Please enter a valid integer.[/bold red]")

def prompt_for_importance_level():
    """
    Prompts the user to enter an importance level until a valid one is provided.
    Returns the valid importance level as an integer.
    """
    while True:
        importance_level = console.input("[bold]Enter level of importance (1-5):[/] ")
        if validate_importance_level(importance_level):
            return int(importance_level)
        else:
            console.print("[bold red]Invalid importance level. Please try again.[/]", style="red")

def validate_importance_level(importance_level_input):
    """
    Validates if the input importance level is valid based on the levels defined in config.py.
    Returns True if valid, False otherwise.
    """
    try:
        importance_level = int(importance_level_input)
        return importance_level in config.IMPORTANCE_LEVELS
    except ValueError:
        return False
    
def prompt_for_note():
    """
    Prompts the user to enter a note. Allows for an empty note.
    Returns the note.
    """
    return console.input("[bold]Enter a note (optional):[/]")

def display_notifications(notifications, sorted=False, start=0, batch_size=10):
    """
    Displays a list of notifications using rich for formatted output.
    If sorted is True, additional details are displayed.
    Displays notifications in batches of 10, starting from the start index.
    """
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=8)
    table.add_column("Title")

    # Adjust columns based on whether notifications are sorted or unsorted
    if sorted:
        # For sorted notifications, display category, importance level, and optional notes
        table.add_column("Category")
        table.add_column("Importance Level")
        table.add_column("Note", overflow="fold")
    else:
        # For unsorted notifications, just display the content
        table.add_column("Content", overflow="fold")
        
    end = start + batch_size
    current_batch = notifications[start:end]

    # Populate the table with notification data
    for notification in current_batch:
        if sorted:
            category_name = notification.category.name if notification.category else "No category"
            content = (notification.content[:87] + '...') if len(notification.content) > 90 else notification.content
            note = notification.note or "N/A"
            note = (note[:87] + '...') if len(note) > 90 else note
            
            table.add_row(
                str(notification.id),
                notification.title,
                category_name, # Display category name instead of ID
                str(notification.importance_level),
                note
            )
        else:
            content = (notification.content[:87] + '...') if len(notification.content) > 90 else notification.content
            table.add_row(
                str(notification.id),
                notification.title,
                content  # Only display content for unsorted notifications
            )

    # Print the table to the console
    console.print(table)
    
    if end < len(notifications):
        console.print("[bold green]Press 'n' to view the next batch of notifications, 'x' to view all, or any other key to return.[/bold green]")
        key = console.input()
        if key.lower() == 'n':
            display_notifications(notifications, sorted, start=end, batch_size=batch_size)
        elif key.lower() == 'x':
            display_notifications(notifications, sorted, start=0, batch_size=len(notifications))
        else:
            return
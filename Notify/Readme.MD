# Notify This

Notify This is a Python application designed to fetch, categorize, and manage LinkedIn notifications. It utilizes Selenium for web scraping, SQLAlchemy for object-relational mapping (ORM), and a command-line interface (CLI) for interaction.

## Features

- **Fetch LinkedIn Notifications**: Automatically retrieves your LinkedIn notifications using Selenium.
- **Categorize Notifications**: Allows categorization of notifications into predefined categories with importance levels.
- **Manage Notifications**: Update notes on notifications, delete notifications, and view categorized notifications through a user-friendly CLI.
- **Display Notifications**: View both sorted and unsorted notifications directly from the CLI.

### Prerequisites

- Python 3.6 or higher
- pip for Python 3
- A web driver compatible with Selenium (ChromeDriver is used in this project)

### Setup

1. Clone the repository:

- git clone https://github.com/CCONLEY-FI/Notify_This.git
- cd Notify_This

3. Run the application:

- python cli.py

## Usage

After starting the application, you will be presented with the main menu:

### Main Menu

1. Display Notifications
   - 1. Display Unsorted Notifications
   - 2. Display Sorted Notifications
2. Fetch All Notifications
3. Modify Notifications
   - 1. Categorize Unsorted Notifications
   - 2. Update Notes
   - 3. Delete Notifications
      - 1. Delete from Sorted List
      - 2. Delete from Unsorted List
4. Exit

Choose an option by entering the corresponding number. Follow the on-screen prompts to interact with the application.

## Project Structure

- `config.py`: Contains configuration settings for the application.
- `database_setup.py`: Defines the database schema and ORM models.
- `scraper.py`: Contains functions for fetching notifications from LinkedIn.
- `cli.py`: Implements the command-line interface for interacting with the application, including the hierarchical menu system.
- `utils.py`: Provides utility functions for input validation, session management, and other tasks

Choose an option by entering the corresponding number. Follow the on-screen prompts to interact with the application.

This project is licensed under the MIT License - see the LICENSE file for details.
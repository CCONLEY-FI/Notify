CHROME_DRIVER_PATH = "./chromedriver" # Path to the ChromeDriver executable

DATABASE_URI = "sqlite:///notify_this.db"  # Example for SQLite, adjust for other DBMS if needed

# Levels of Importance
IMPORTANCE_LEVELS = {
    1: "Not important",
    2: "Might matter",
    3: "Check it out",
    4: "Very important",
    5: "Of immediate concern"
}

# Additional Configuration
# Add any additional configuration that might be relevant for the project here.
# This could include logging settings, retry logic for web scraping, etc.

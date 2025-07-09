
from selenium import webdriver  # Imports the Selenium WebDriver, which allows interaction with web browsers.
from selenium.webdriver.chrome.service import Service  # Imports Service for managing the ChromeDriver process.
from selenium.webdriver.chrome.options import Options  # Imports Options to configure Chrome browser behavior (e.g., headless mode).
from selenium.webdriver.common.by import By  # Imports By for specifying how to locate elements (e.g., by CSS selector, ID).
from selenium.webdriver.common.keys import Keys # Not used in the provided code, but typically for simulating keyboard presses.
from selenium.webdriver.support.ui import WebDriverWait  # Imports WebDriverWait for explicit waits, allowing the browser to load content.
from selenium.webdriver.support import expected_conditions as EC  # Imports expected_conditions for defining conditions to wait for.
from webdriver_manager.chrome import ChromeDriverManager  # Imports ChromeDriverManager to automatically manage ChromeDriver binaries.
import time  # Imports the time module for adding delays.
import re  # Imports the regular expression module for pattern matching.

def get_product_links(product_name, max_retries=5):
    """Search Google for Flipkart product links and extract the first few."""
    # Define a function to get product links, taking product name and max retries as input.
    links = []  # Initialize an empty list to store found links.
    search_query = f"{product_name} site:flipkart.com"  # Constructs the Google search query to specifically search Flipkart.
    url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"  # Formats the search query into a Google search URL.

    print(f"Searching Google with query: {search_query}")  # Prints the search query for debugging.

    options = Options()  # Initializes an Options object for Chrome browser configuration.
    options.add_argument("--headless=new")  # Configures Chrome to run in headless mode (without a GUI).
    options.add_argument("--no-sandbox")  # Disables the sandbox, often needed in containerized environments.
    options.add_argument("--disable-dev-shm-usage")  # Disables the use of /dev/shm, important for some Linux setups.
    options.add_argument("--disable-gpu")  # Disables GPU hardware acceleration.
    options.add_argument("--window-size=1920x1080")  # Sets the browser window size.
    options.add_argument("--disable-features=NetworkService") # Disables NetworkService, a Chrome feature.
    options.add_argument("--disable-blink-features=AutomationControlled") # Prevents detection as an automated browser.
    options.add_argument("--disable-extensions")  # Disables browser extensions.
    options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.6834.111 Safari/537.36")  # Sets a custom User-Agent header to mimic a real browser.

    for attempt in range(max_retries):  # Loops through a number of retries in case of failure.
        driver = None  # Initializes driver to None for proper cleanup.
        try:
            # Initialize ChromeDriver
            driver = webdriver.Chrome(  # Creates a new Chrome WebDriver instance.
                service=Service(ChromeDriverManager().install()),  # Automatically downloads and sets up ChromeDriver.
                options=options  # Applies the configured options.
            )
            
            # Set page load timeout
            driver.set_page_load_timeout(30)  # Sets a timeout for page loading.
            print("Chrome WebDriver initialized successfully")  # Confirms WebDriver initialization.
            
            # Navigate to Google search URL
            print(f"Navigating to Google search URL: {url}")  # Prints the URL being navigated to.
            driver.get(url)  # Opens the Google search URL in the browser.
            time.sleep(5)  # Pauses execution for 5 seconds to allow content to load.

            # Wait for and find search results
            wait = WebDriverWait(driver, 20)  # Initializes a WebDriverWait with a 20-second timeout.
            search_results = wait.until(  # Waits until the specified condition is met.
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.tF2Cxc"))  # Waits for search result elements.
            )

            print(f"Found {len(search_results)} search results")  # Reports the number of search results found.

            for result in search_results:  # Iterates through each found search result element.
                try:
                    link_element = result.find_element(By.CSS_SELECTOR, "a")  # Finds the anchor tag (link) within the result.
                    link = link_element.get_attribute('href')  # Extracts the 'href' attribute (URL) from the link.

                    # Flipkart URL pattern matching
                    if re.search(r'flipkart\.com.*?/p/', link) and "google.com" not in link:  # Checks if the link is a valid Flipkart product page.
                        links.append(link)  # Adds the valid Flipkart link to the list.
                        print(f"Found valid Flipkart link: {link}")  # Confirms a valid Flipkart link was found.
                except Exception as e:  # Catches any errors during link extraction for a single result.
                    print(f"Error extracting link from result: {str(e)}")  # Prints the error message.
                    continue  # Continues to the next search result.

                if len(links) >= 5:  # Checks if 5 or more links have been found.
                    break  # Exits the loop if enough links are found.

            if links:  # Checks if any links were found in the current attempt.
                break  # Exits the retry loop if links were successfully found.
            
        except Exception as e:  # Catches any general exceptions during the scraping process for an attempt.
            print(f"Attempt {attempt + 1} failed: {str(e)}")  # Prints the failure message for the current attempt.
            if attempt == max_retries - 1:  # Checks if it's the last retry attempt.
                print("Failed to fetch product links after maximum retries")  # Informs about total failure.
                return []  # Returns an empty list if all retries fail.
            time.sleep(2 * (attempt + 1))  # Adds an increasing delay before the next retry.
            
        finally:  # Ensures cleanup code runs regardless of success or failure.
            if driver:  # Checks if the WebDriver instance was created.
                try:
                    driver.quit()  # Closes the browser and quits the WebDriver session.
                    print("Chrome WebDriver closed successfully")  # Confirms WebDriver closure.
                except Exception as e:  # Catches errors during driver closure.
                    print(f"Error closing driver: {str(e)}")  # Prints the error message.

    print(f"\nTotal Flipkart links found: {len(links)}")  # Prints the total number of unique links found.
    for i, link in enumerate(links, 1):  # Iterates through the found links to print them.
        print(f"{i}. {link}")  # Prints each found link with its sequential number.

    return links  # Returns the list of extracted Flipkart product links.

 # Prompts user for a product name to search.


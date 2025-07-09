from datetime import datetime # Imports the datetime module to work with dates and times (e.g., for timestamps).
import time # Imports the time module for adding delays in execution.
import re # Imports the regular expression module for pattern matching and text manipulation.
import random # Imports the random module to generate random numbers (used for random delays).
import os # Imports the os module for interacting with the operating system (e.g., creating directories).
import requests # Imports the requests library for making HTTP requests to fetch web page content.
import pandas as pd # Imports the pandas library, commonly used for data manipulation and analysis, especially with DataFrames.
from bs4 import BeautifulSoup # Imports BeautifulSoup for parsing HTML and XML documents.
import nltk # Imports the Natural Language Toolkit (NLTK) for various NLP operations.
from nltk.corpus import stopwords # Imports stopwords from NLTK, common words to be filtered out.
from nltk.stem import WordNetLemmatizer # Imports WordNetLemmatizer from NLTK for lemmatization.
from nltk.tokenize import sent_tokenize # Imports sent_tokenize from NLTK for splitting text into sentences.
from Link_Extractor import get_product_links # Imports the get_product_links function from your custom linkExtractor module.

# Download necessary NLTK datasets
# These lines ensure that the required NLTK data (stopwords, WordNet, and tokenizers)
# are available for the text preprocessing steps. They will download if not already present.
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt')

# Headers to avoid request blocking
headers = {
    # This dictionary defines HTTP headers to be sent with requests.
    # A User-Agent header makes the request appear as if it's coming from a web browser,
    # which can help in bypassing some basic bot detection mechanisms.
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# -------------------- REVIEW EXTRACTION --------------------
def modify_reviews_url(reviews_url):
    """Convert product URL to reviews URL format"""
    # This function takes a product URL (e.g., .../p/...) and transforms it
    # into the corresponding product reviews URL (e.g., .../product-reviews/...).
    return reviews_url.replace("/p/", "/product-reviews/")

def get_reviews_from_page(html):
    """Extract reviews from a single Flipkart page."""
    reviews_data = [] # Initializes an empty list to store dictionaries of extracted review data.
    # Finds all HTML div elements with the class 'cPHDOP'. This class is assumed to be
    # the container for individual reviews on Flipkart's review pages.
    review_containers = html.find_all('div', {'class': 'cPHDOP'})
    
    for container in review_containers: # Loops through each identified review container.
        try:
            # Extract rating
            # Attempts to find a div with specific classes for the rating.
            rating_div = container.find('div', {'class': 'XQDdHH Ga3i8K'})
            # Extracts the text content of the rating div, strips whitespace,
            # and defaults to 'N/A' if not found.
            rating = rating_div.text.strip() if rating_div else 'N/A'
            
            # Extract review title
            # Finds a paragraph tag with the class 'z9E0IG' for the review title.
            title_div = container.find('p', {'class': 'z9E0IG'})
            # Extracts and cleans the title text.
            title = title_div.text.strip() if title_div else 'N/A'
            
            # Extract review text
            # Finds a div with class 'ZmyHeo' for the main review text.
            review_div = container.find('div', {'class': 'ZmyHeo'})
            # Extracts the text from the first child div within review_div, cleans it.
            review_text = review_div.find('div').text.strip() if review_div and review_div.find('div') else 'N/A'
            
            # Extract reviewer name
            # Finds a paragraph tag with specific classes for the reviewer's name.
            name_div = container.find('p', {'class': '_2NsDsF AwS1CA'})
            # Extracts and cleans the name text.
            name = name_div.text.strip() if name_div else 'N/A'
            
            # Extract review date
            # Finds a paragraph tag with class '_2NsDsF' for the review date.
            # It also checks to ensure it's not the same element as the name_div.
            date_div = container.find('p', {'class': '_2NsDsF'})
            date = date_div.text.strip() if date_div and not date_div.get('class') == '_2NsDsF AwS1CA' else 'N/A'
            
            # Extract certified buyer status
            # Finds a paragraph tag with class 'MztJPv' to check for "Certified Buyer".
            certified_div = container.find('p', {'class': 'MztJPv'})
            # Sets 'Yes' or 'No' based on whether "Certified Buyer" text is present.
            is_certified = 'Yes' if certified_div and 'Certified Buyer' in certified_div.text else 'No'
            
            # Get helpful votes
            # Finds a span tag with class 'tl9VpF' for helpful votes.
            helpful_div = container.find('span', {'class': 'tl9VpF'})
            # Extracts and cleans the helpful vote count, defaults to '0'.
            helpful_count = helpful_div.text.strip() if helpful_div else '0'
            
            # Appends a dictionary containing all extracted review details to the reviews_data list.
            reviews_data.append({
                'Name': name,
                'Rating': rating,
                'Title': title,
                'Description': review_text,
                'Date': date,
                'Certified_Buyer': is_certified,
                'Helpful_Votes': helpful_count
            })
            
        except Exception as e: # Catches any exception that occurs during the extraction of a single review.
            print(f"Error processing review: {e}") # Prints the error message.
            continue # Continues to the next review container.
    
    return reviews_data # Returns the list of extracted review dictionaries.

def get_reviews(base_url, max_pages=10):
    """Extract reviews from multiple pages."""
    all_reviews = [] # Initializes an empty list to store reviews from all pages.
    page = 1 # Starts page counter at 1.
    
    while page <= max_pages: # Loops as long as the current page is within the maximum allowed pages.
        try:
            # Construct page URL
            # Builds the URL for the current page, appending '&page={page}' for subsequent pages.
            page_url = f"{base_url}&page={page}" if page > 1 else base_url
                
            print(f"Fetching reviews from page {page}") # Prints the current page being fetched.
            
            # Makes an HTTP GET request to the page URL with the defined headers.
            response = requests.get(page_url, headers=headers)
            if response.status_code != 200: # Checks if the HTTP request was successful (status code 200).
                print(f"Failed to fetch page {page}. Status code: {response.status_code}") # Prints an error if fetching fails.
                break # Exits the loop if a page cannot be fetched.
                
            # Parses the content of the fetched page using BeautifulSoup.
            soup = BeautifulSoup(response.content, 'html.parser')
            print(f"Page HTML length: {len(response.content)}")  # Debug info: prints the size of the HTML content.
            
            # Get reviews from current page
            page_reviews = get_reviews_from_page(soup) # Calls the helper function to extract reviews from the current page's HTML.
            
            if not page_reviews: # Checks if no reviews were found on the current page.
                print(f"No reviews found on page {page}") # Prints a message if no reviews are found.
                break # Exits the loop if no reviews are found (suggests end of reviews).
                
            all_reviews.extend(page_reviews) # Adds the reviews from the current page to the overall list.
            print(f"Successfully scraped {len(page_reviews)} reviews from page {page}") # Confirms successful scraping for the page.
            
            # Random delay to avoid being blocked
            time.sleep(random.uniform(2, 4)) # Pauses execution for a random duration to avoid triggering bot detection.
            page += 1 # Increments the page counter.
            
        except Exception as e: # Catches any general exception during the page processing.
            print(f"Error processing page {page}: {e}") # Prints the error message.
            break # Exits the loop on error.
    
    return all_reviews # Returns the list of all extracted reviews.

def get_product_details(product_url):
    """Extract product price and image from Flipkart."""

    # Checks if the provided URL is a valid string and starts with 'http'.
    if not isinstance(product_url, str) or not product_url.startswith('http'):
        print(f"Invalid product URL: {product_url}") # Prints an error for invalid URL.
        return "N/A", "N/A" # Returns 'N/A' for price and image if URL is invalid.
    
    print(f"\nFetching product details from: {product_url}") # Prints the URL for product details.
    
    try:
        # Makes an HTTP GET request to the product URL.
        response = requests.get(product_url, headers=headers)
        if response.status_code != 200: # Checks for successful HTTP response.
            print(f"Failed to fetch product page. Status code: {response.status_code}") # Prints error if page fetch fails.
            return "N/A", "N/A" # Returns 'N/A' if page cannot be fetched.
        
        # Parses the product page HTML.
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract price with better error handling
        try:
            # Finds the div containing the price.
            price_div = soup.find('div', {'class': 'Nx9bqj'})
            # Extracts and cleans the price text, defaults to "N/A".
            price = price_div.text.strip() if price_div else "N/A"
        except Exception as e: # Catches errors during price extraction.
            print(f"Error extracting price: {e}") # Prints the error.
            price = "N/A" # Sets price to "N/A" on error.

        # Extract product image with better error handling
        try:
            # Finds the image tag with specific classes.
            img_tag = soup.find('img', {'class': 'DByuf4 IZexXJ jLEJ7H'})
            # Extracts the 'src' attribute (image URL), defaults to "N/A".
            image_url = img_tag['src'] if img_tag else "N/A"
        except Exception as e: # Catches errors during image extraction.
            print(f"Error extracting image: {e}") # Prints the error.
            image_url = "N/A" # Sets image_url to "N/A" on error.
        
        return price, image_url # Returns the extracted price and image URL.

    except Exception as e: # Catches any general exception during product details fetching.
        print(f"Error fetching product details: {e}") # Prints the error.
        return "N/A", "N/A" # Returns 'N/A' for both on general error.

# -------------------- PREPROCESSING --------------------

def clean_text(text):
    """Clean the review text."""
    text = re.sub(r'<[^>]+>', '', text)  # Removes HTML tags from the text.
    text = re.sub(r'READ MORE', '', text, flags=re.IGNORECASE)  # Removes "READ MORE" (case-insensitive).
    text = re.sub(r'[^a-zA-Z0-9\s.,!?]', '', text)  # Removes special characters, keeping letters, numbers, spaces, and basic punctuation.
    text = ' '.join(text.split())  # Normalizes whitespace (replaces multiple spaces with single, removes leading/trailing).
    return text.strip() # Returns the cleaned text.

def remove_stopwords(text):
    """Remove stopwords from text."""
    stop_words = set(stopwords.words('english')) # Loads a set of English stopwords for efficient lookup.
    # Splits the text into words and reconstructs it, excluding any words found in the stop_words set.
    return ' '.join(word for word in text.split() if word.lower() not in stop_words)

def lemmatize_text(text):
    """Lemmatize words in text."""
    lemmatizer = WordNetLemmatizer() # Initializes the WordNetLemmatizer.
    # Splits the text into words, lemmatizes each word (reduces to base form), and joins them back.
    return ' '.join(lemmatizer.lemmatize(word) for word in text.split())

def preprocess_reviews(reviews):
    """Apply preprocessing pipeline to reviews."""
    processed_reviews = [] # Initializes an empty list for processed reviews.
    for review in reviews: # Iterates through each raw review description.
        # Clean text
        cleaned = clean_text(review) # Applies the clean_text function.
        # Remove stopwords & lemmatize
        processed_review = lemmatize_text(remove_stopwords(cleaned)) # Applies stopword removal and lemmatization.
        if len(processed_review.split()) >= 3:  # Keep only meaningful reviews
            # Only adds the processed review if it has at least 3 words, filtering out very short or empty reviews.
            processed_reviews.append(processed_review)
    
    return processed_reviews # Returns the list of processed reviews.

# -------------------- MAIN FUNCTION --------------------

def extractReviews(name, max_pages=15):
    """Extract Flipkart reviews and product price."""
    links = get_product_links(name) # Calls linkExtractor to get Flipkart product links for the given name.
    
    if not links: # Checks if no product links were found.
        print("No product links found!") # Prints a message.
        return [], "N/A", "N/A" # Returns empty lists/N/A if no links.

    all_reviews = [] # Initializes a list to accumulate all reviews.
    
    # Iterate through each product link
    # The original comment says "Only process first link to avoid duplicates", but the loop iterates.
    # However, `get_reviews` is called inside the loop. If `get_product_links` returns multiple links
    # for the same product, this might lead to duplicate reviews.
    for link in links:
        url = modify_reviews_url(link) # Converts the product link to its reviews URL.
        print(f"\nExtracting reviews from: {url}") # Prints the URL being scraped.
    
        # Get reviews
        product_reviews = get_reviews(url, max_pages) # Calls get_reviews to scrape reviews from the current URL.
        if product_reviews: # If reviews are found for this URL.
            all_reviews.extend(product_reviews) # Adds them to the overall list.

    if not all_reviews: # Checks if no reviews were collected after processing all links.
        print("No reviews found!") # Prints a message.
        return [], "N/A", "N/A" # Returns empty lists/N/A.
    
    # Save raw reviews
    save_dir = "C:/Users/eapen/OneDrive/Desktop/automated-review-rating-system/data/reviews"
    os.makedirs(save_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    raw_filename = os.path.join(save_dir, f"{name}_flipkart_reviews{timestamp}.csv")
    df_reviews = pd.DataFrame(all_reviews)
    df_reviews = df_reviews.replace("N/A", pd.NA)
    df_reviews=df_reviews.dropna() # Drops any rows with NaN values in the DataFrame.
    df_reviews.to_csv(raw_filename, index=False) # Saves the collected reviews to a CSV file.
    print(f"\nSaved {len(all_reviews)} raw reviews to {raw_filename}") # Confirms saving.

    # Preprocess review descriptions
    # Extracts the 'Description' column from the DataFrame and preprocesses it.
    processed_reviews = preprocess_reviews(df_reviews['Description'].tolist())

    # Fetch product details from the first valid product link
    # Gets price and image URL from the first link found by linkExtractor.
    price, image_url = get_product_details(links[0])

    # Returns a dictionary containing raw reviews, processed reviews, price, and image URL.
    return {
        'raw_reviews': all_reviews,
        'processed_reviews': processed_reviews,
        'price': price,
        'image_url': image_url
    }

def sanitize_filename(filename):
    # Replaces characters that are not alphanumeric, hyphens, or underscores with underscores.
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', filename)
    return sanitized[:100]  # Truncates the filename to 100 characters to avoid path issues.

def extractReviewsFromLink(link, max_pages=15):
    # This function is similar to extractReviews but takes a direct product link
    # instead of a product name that needs to be searched via Google.
    sanitized_link = sanitize_filename(link) # Sanitizes the full link for use in filename.

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") # Generates a timestamp.
    
    # Constructs a raw filename using the sanitized link and timestamp.
    raw_filename = f'reviews/{sanitized_link}_flipkart_reviews{timestamp}.csv'
    all_reviews = [] # Initializes list for all reviews.
    
    url = modify_reviews_url(link) # Converts the product link to its reviews URL.
    print(f"\nExtracting reviews from: {url}") # Prints the URL being scraped.
    
    # Get reviews
    product_reviews = get_reviews(url, max_pages) # Scrapes reviews from the URL.
    if product_reviews: # If reviews are found.
        all_reviews.extend(product_reviews) # Adds them to the list.

    if not all_reviews: # Checks if no reviews were found.
        print("No reviews found!") # Prints a message.
        return [], "N/A", "N/A" # Returns empty lists/N/A.
    
    # Save raw reviews
    save_dir = "C:/Users/eapen/OneDrive/Desktop/automated-review-rating-system/data/reviews" # Directory to save reviews.
    os.makedirs(save_dir, exist_ok=True) # Creates the 'reviews' directory if it doesn't exist.  

    sanitized_link = sanitize_filename(link.split("/")[-1])
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    raw_filename = os.path.join(save_dir, f"{sanitized_link}_flipkart_reviews{timestamp}.csv")
    df_reviews = pd.DataFrame(all_reviews)
    df_reviews = df_reviews.replace("N/A", pd.NA) # Replaces "N/A" strings with pandas' NA.
    df_reviews=df_reviews.dropna() # Drops any rows with NaN values in the DataFrame.
    df_reviews.to_csv(raw_filename, index=False)
    print(f"\nSaved {len(all_reviews)} raw reviews to {raw_filename}") # Confirms saving.

    # Preprocess review descriptions
    processed_reviews = preprocess_reviews(df_reviews['Description'].tolist()) # Preprocesses review descriptions.

    # Fetch product details from the link
    price, image_url = get_product_details(link) # Gets price and image URL directly from the provided link.

    # Returns a dictionary with raw reviews, processed reviews, price, and image URL.
    return {
        'raw_reviews': all_reviews,
        'processed_reviews': processed_reviews,
        'price': price,
        'image_url': image_url
    }

if __name__ == "__main__":
    # Top-level function call to begin the review extraction process
    product_name = input("Enter the product name to search on Flipkart: ")
    
    # Step-by-step call hierarchy:
    # extractReviews → get_product_links → modify_reviews_url → get_reviews → get_reviews_from_page
    # extractReviews → preprocess_reviews → clean_text → remove_stopwords → lemmatize_text
    # extractReviews → get_product_details
    
    result = extractReviews(product_name, max_pages=10)

    print("\n--- Summary ---")
    print(f"Total Raw Reviews: {len(result['raw_reviews'])}")
    print(f"Total Processed Reviews: {len(result['processed_reviews'])}")
    print(f"Product Price: {result['price']}")
    print(f"Product Image URL: {result['image_url']}")

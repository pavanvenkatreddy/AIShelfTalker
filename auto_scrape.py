from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fuzzywuzzy import fuzz  # Import fuzzywuzzy for fuzzy matching
import time
import re  # Import regex for extracting left value

def handle_popup(driver):
    try:
        # Wait for the popup close button to appear
        close_button = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ab-close-button"))
        )
        print("Popup detected. Attempting to close.")
        
        # Click the close button
        close_button.click()
        
        # Optional: Wait for the popup to disappear
        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element((By.CLASS_NAME, "ab-close-button"))
        )
        print("Popup closed successfully.")
    except Exception as e:
        print(f"No popup detected or error while closing popup: {e}")


def search_product(product_name, threshold=60):
    # Set up the web driver (Ensure ChromeDriver matches your Chrome version)
    driver = webdriver.Chrome()  # Or specify the path if needed

    website_url = "https://www.vivino.com/US/en/"  # Change this to the website you want to search

    # Open the specified website
    driver.get(website_url)

    # Initialize variables to hold data
    rating = "Not available"
    profile_info = "Not available"
    left_value = "Not available"
    bold_label_left_value = "Not available"

    try:
        # Wait for the search bar to be visible (adjust selector as needed)
        search_bar = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.NAME, "q"))
        )
        # Perform the search
        search_bar.send_keys(product_name)
        search_bar.send_keys(Keys.RETURN)

        # Wait for search results to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".search-results-list"))
        )

        # Locate the container with all search results
        container = driver.find_element(By.CSS_SELECTOR, ".search-results-list")
        results = container.find_elements(By.CSS_SELECTOR, ".card.card-lg.fixed")
        print(f"Found {len(results)} results.")

        highest_score = 0
        most_relevant_result = None

        # Check all results for the best match
        for result in results:
            try:
                result_name = result.find_element(By.CSS_SELECTOR, ".header-smaller.text-block.wine-card__name").text.lower()
                similarity_score = fuzz.partial_ratio(product_name.lower(), result_name)
                print(f"Result: {result_name}, Similarity Score: {similarity_score}%")
                if similarity_score >= threshold and similarity_score > highest_score:
                    highest_score = similarity_score
                    most_relevant_result = result
            except Exception as e:
                print(f"Error extracting result name: {e}")

        # Click the most relevant result if found
        if most_relevant_result:
            relevant_item = most_relevant_result.find_element(By.CSS_SELECTOR, ".wine-card__image-wrapper")
            driver.execute_script("arguments[0].scrollIntoView();", relevant_item)
            time.sleep(1)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(relevant_item)).click()
        else:
            print("No relevant result found.")
            driver.quit()
            return {"rating": rating, "profile_info": profile_info, "left_value": left_value}

        # Wait for the product page to load and extract details
        # Handle popup if it appears
        handle_popup(driver)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1")))
        product_title = driver.find_element(By.CSS_SELECTOR, "h1").text
        print("Product Title:", product_title)

        # Extract rating
        try:
            rating = driver.find_element(By.CSS_SELECTOR, ".wineFacts__wineFacts--2Ih8B").text
        except:
            print("Rating: Not available")

        # Extract profile info
        try:
            full_text = driver.find_element(By.CSS_SELECTOR, ".tasteCharacteristics__tasteCharacteristics--2y2ix").text
            if "WINE LOVERS TASTE SUMMARY" in full_text:
                profile_info = full_text.split("WINE LOVERS TASTE SUMMARY", 1)[1].strip()
        except:
            print("Profile info: Not available")

        try:
            bold_label = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'tasteStructure__property--CLNl_') and text()='Light']"))
            )
            bold_label_value_span = bold_label.find_element(By.XPATH, "../following-sibling::td//span[contains(@class, 'indicatorBar__progress--3aXLX')]")
            bold_label_style_attribute = bold_label_value_span.get_attribute("style")
            bold_label_left_match = re.search(r"left:\s*([0-9.]+%);", bold_label_style_attribute)
            if bold_label_left_match:
                bold_label_left_value = bold_label_left_match.group(1)
        except Exception as e:
            print(f"Bold component left value extraction error: {e}")

        # Extract left value for "Dry"
        try:
            dry_label = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'tasteStructure__property--CLNl_') and text()='Dry']"))
            )
            dry_left_value_span = dry_label.find_element(By.XPATH, "../following-sibling::td//span[contains(@class, 'indicatorBar__progress--3aXLX')]")
            style_attribute = dry_left_value_span.get_attribute("style")
            left_match = re.search(r"left:\s*([0-9.]+%);", style_attribute)
            if left_match:
                left_value = left_match.group(1)
        except:
            print("Dry component left value: Not available")

        # Extract left value for "Dry"
        # Extract left value for "Bold"
        



    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the browser
        driver.quit()

    return {"rating": rating, "profile_info": profile_info, "left_value": left_value, "bold_label_left_value":bold_label_left_value}
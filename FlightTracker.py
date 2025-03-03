import aiohttp
import asyncio
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def get_user_input():
    while True:
        trip_type = input("Enter 'one-way' or 'round-trip': ").strip().lower()
        if trip_type in ["one-way", "round-trip"]:
            break
        print("Invalid input. Please enter 'one-way' or 'round-trip'.")
    
    from_city = input("Enter departure city (IATA Code): ").strip().upper()
    to_city = input("Enter destination city (IATA Code): ").strip().upper()
    
    while True:
        try:
            dep_date = input("Enter departure date (YYYY-MM-DD): ").strip()
            dep_date = datetime.datetime.strptime(dep_date, "%Y-%m-%d")
            break
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
    
    ret_date = None
    if trip_type == "round-trip":
        while True:
            try:
                ret_date = input("Enter return date (YYYY-MM-DD): ").strip()
                ret_date = datetime.datetime.strptime(ret_date, "%Y-%m-%d")
                break
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD.")
    
    return trip_type, from_city, to_city, dep_date, ret_date

def scrape_google_flights(from_city, to_city, dep_date):
    url = f"https://www.google.com/travel/flights?q=flights%20from%20{from_city}%20to%20{to_city}%20on%20{dep_date.strftime('%Y-%m-%d')}"

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)
        flights = driver.find_elements(By.CLASS_NAME, "pIav2d")  
        prices = [f.text for f in flights if "$" in f.text]
        driver.quit()
        return prices
    except Exception as e:
        print(f"Error scraping Google Flights: {e}")
        return []

async def main():
    # Get user input for the flight search
    trip_type, from_city, to_city, dep_date, ret_date = get_user_input()

    # Print out the parameters
    print("\nFlight Search Parameters:")
    print(f"Trip Type: {trip_type.capitalize()}")
    print(f"Departure City (IATA): {from_city}")
    print(f"Destination City (IATA): {to_city}")
    print(f"Departure Date: {dep_date.strftime('%Y-%m-%d')}")
    if ret_date:
        print(f"Return Date: {ret_date.strftime('%Y-%m-%d')}")
    
    # Scrape Google Flights for prices
    print("\nScraping Google Flights for the cheapest options...")
    google_prices = scrape_google_flights(from_city, to_city, dep_date)
    
    # Output results
    print("\nGoogle Flights Prices Found:")
    if google_prices:
        for price in google_prices:
            print(price)
    else:
        print("No prices found.")

if __name__ == "__main__":
    asyncio.run(main())

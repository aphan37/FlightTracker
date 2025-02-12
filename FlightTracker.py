import aiohttp
import asyncio
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

API_KEY = "d3ac1c080eeccd82da463057f5f0318e"
BASE_URL = "http://api.aviationstack.com/v1/flights"

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

async def fetch_flights(from_city, to_city, dep_date, ret_date=None):
    params = {
        "access_key": API_KEY,
        "dep_iata": from_city,
        "arr_iata": to_city,
        "flight_date": dep_date.strftime("%Y-%m-%d"),
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(BASE_URL, params=params) as response:
                if response.status != 200:
                    print(f"API request failed with status {response.status}")
                    return {}
                return await response.json()
    except aiohttp.ClientError as e:
        print(f"Network error fetching flights: {e}")
        return {}
    except Exception as e:
        print(f"Unexpected error fetching flights: {e}")
        return {}

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
    trip_type, from_city, to_city, dep_date, ret_date = get_user_input()
    
    print("Fetching flights from AviationStack API...")
    flights = await fetch_flights(from_city, to_city, dep_date, ret_date)
    
    print("Scraping Google Flights...")
    google_prices = scrape_google_flights(from_city, to_city, dep_date)
    
    print("\nCheapest Flights Found:")
    for flight in flights.get("data", []):
        print(f"{flight.get('airline', 'Unknown Airline')} - ${flight.get('price', 'N/A')} - {flight.get('flight_number', 'No flight number')}")
    
    print("\nGoogle Flights Prices:")
    if google_prices:
        for price in google_prices:
            print(price)
    else:
        print("No prices found.")

if __name__ == "__main__":
    asyncio.run(main())

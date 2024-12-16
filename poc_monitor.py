import os
import time
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Environment variables
API_KEY = os.getenv("GOOGLE_API_KEY")
CX = os.getenv("SEARCH_ENGINE_ID")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
SEARCH_TERM = os.getenv("SEARCH_TERM")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 14400))  # Default to 4 hours

CACHE_FILE = "poc_cache.json"

def load_cache():
    """Load seen links from the cache file."""
    try:
        with open(CACHE_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"seen_links": []}

def save_cache(cache_data):
    """Save seen links to the cache file."""
    with open(CACHE_FILE, "w") as file:
        json.dump(cache_data, file)

def google_search(search_term, num_results=10):
    """Search Google using Custom Search JSON API."""
    endpoint = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": CX,
        "q": search_term,
        "num": num_results,
    }
    
    response = requests.get(endpoint, params=params)
    if response.status_code != 200:
        print("Error occurred while searching Google:", response.json())
        return []
    
    search_results = response.json()
    results = []

    for item in search_results.get("items", []):
        results.append({
            "title": item.get("title"),
            "link": item.get("link"),
            "description": item.get("snippet"),
        })

    return results

def send_discord_alert(results):
    """Send new results to Discord via webhook."""
    content = f"**New results found for search term: {SEARCH_TERM}**\n\n"
    for idx, result in enumerate(results, start=1):
        # Truncate the description if it exceeds 200 characters
        description = result['description'][:200] + "..." if len(result['description']) > 200 else result['description']
        
        # Format the result entry
        result_entry = f"**{idx}. [{result['title']}]({result['link']})**\n{description}\n\n"
        
        # Check if adding this entry will exceed Discord's limit
        if len(content) + len(result_entry) > 2000:
            print("[INFO] Content exceeds 2000 characters, truncating alert.")
            break  # Stop adding more results
        
        content += result_entry

    # Send the message to Discord
    data = {"content": content}
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)

    if response.status_code == 204:
        print("[INFO] Alert sent to Discord successfully.")
    else:
        print("[ERROR] Failed to send alert to Discord:", response.status_code, response.text)


def log_results(results):
    """Log new results to a file and print to the console."""
    filename = "poc_monitor_log.md"
    with open(filename, "a", encoding="utf-8") as file:
        file.write(f"\n# Updates on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        for idx, result in enumerate(results, start=1):
            file.write(f"### Result {idx}\n")
            file.write(f"**Title:** [{result['title']}]({result['link']})\n\n")
            file.write(f"**Description:** {result['description']}\n\n")
    
    print(f"[INFO] Logged {len(results)} new results to {filename}.")

def monitor_poc():
    """Monitor for new POC content."""
    cache_data = load_cache()
    seen_links = set(cache_data.get("seen_links", []))

    while True:
        print(f"\n[INFO] Checking for updates on: {SEARCH_TERM}")
        results = google_search(SEARCH_TERM)
        
        new_results = []
        for result in results:
            if result['link'] not in seen_links:
                seen_links.add(result['link'])
                new_results.append(result)
        
        if new_results:
            print("[ALERT] New content found!")
            log_results(new_results)
            send_discord_alert(new_results)
            # Update cache with new links
            cache_data["seen_links"] = list(seen_links)
            save_cache(cache_data)
        else:
            print("[INFO] No new content.")
        
        print(f"[INFO] Sleeping for {CHECK_INTERVAL} seconds...\n")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        monitor_poc()
    except KeyboardInterrupt:
        print("\n[INFO] Monitoring stopped by user.")

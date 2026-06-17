import os
import json
import urllib.request

# --- CONFIGURATION ---
CLAN_TAG = "#YOUR_CLAN_TAG_HERE"  # IMPORTANT: Change this back to your clan tag!
API_TOKEN = os.environ.get("COC_TOKEN")
PROXY_URL = "https://cocproxy.royaleapi.dev/v1/clans/"

def check_war_status():
    if not API_TOKEN:
        print("Error: API Token not found in the vault!")
        return
        
    # Format the clan tag for the web URL (replace # with %23)
    formatted_tag = CLAN_TAG.replace("#", "%23")
    url = f"{PROXY_URL}{formatted_tag}/currentwar"
    
    # NEW: User-Agent added here to bypass the Cloudflare 403 Forbidden error!
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            
            state = data.get("state")
            print(f"Current war state: {state}")
            
            # If the war has ended, we save it immediately!
            if state == "warEnded":
                save_war_data(data)
            else:
                print("War is still active or clan is not in war. Doing nothing.")
                
    except Exception as e:
        print(f"Error fetching data: {e}")

def save_war_data(data):
    # Create a unique filename based on the exact time the war ended
    end_time = data.get("endTime", "unknown_time").replace(":", "")
    filename = f"warEnded_{end_time}.json"
    
    # Save the file into the GitHub folder
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
        
    print(f"Successfully saved war data to {filename}")

if __name__ == "__main__":
    check_war_status()

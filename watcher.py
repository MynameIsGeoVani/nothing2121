import os
import json
import urllib.request
import urllib.error

# --- CONFIGURATION ---
CLAN_TAG = "#2Q2YLVCVV"  # Your clan tag is now automatically loaded!
API_TOKEN = os.environ.get("COC_TOKEN")
PROXY_URL = "https://cocproxy.royaleapi.dev/v1/clans/"

def check_war_status():
    if not API_TOKEN:
        print("Error: API Token not found in the vault!")
        return
        
    # AUTO-CLEANER: Fixes common copy/paste mistakes in the GitHub Secret Vault
    clean_token = API_TOKEN.replace('"', '').replace("'", "").strip()
    if clean_token.startswith("COC_TOKEN="):
        clean_token = clean_token.replace("COC_TOKEN=", "")

    formatted_tag = CLAN_TAG.replace("#", "%23")
    url = f"{PROXY_URL}{formatted_tag}/currentwar"
    
    headers = {
        "Authorization": f"Bearer {clean_token}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    req = urllib.request.Request(url, headers=headers)
    
    try:
        print("Connecting to Clash of Clans API...")
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            
            state = data.get("state")
            print(f"Current war state: {state}")
            
            if state == "warEnded":
                save_war_data(data)
            else:
                print("War is still active or clan is not in war. Doing nothing.")
                
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}")
        try:
            error_body = e.read().decode('utf-8', errors='ignore')
            print(f"\n--- THE REAL REASON ---")
            print(error_body)
            print(f"-----------------------\n")
        except Exception:
            print("Could not read hidden error body.")
    except Exception as e:
        print(f"Error fetching data: {e}")

def save_war_data(data):
    end_time = data.get("endTime", "unknown_time").replace(":", "")
    filename = f"warEnded_{end_time}.json"
    
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
        
    print(f"Successfully saved war data to {filename}")

if __name__ == "__main__":
    check_war_status()

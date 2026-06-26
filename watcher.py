import os
import json
import urllib.request
import urllib.error

# --- CONFIGURATION ---
CLAN_TAG = "#2Q2YLVCVV"
API_TOKEN = os.environ.get("COC_TOKEN")
PROXY_URL = "https://cocproxy.royaleapi.dev/v1/clans/"
CWL_WAR_URL = "https://cocproxy.royaleapi.dev/v1/clanwarleagues/wars/"

def get_headers():
    clean_token = API_TOKEN.replace('"', '').replace("'", "").strip()
    if clean_token.startswith("COC_TOKEN="):
        clean_token = clean_token.replace("COC_TOKEN=", "")
    return {
        "Authorization": f"Bearer {clean_token}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

def fetch_api(url):
    req = urllib.request.Request(url, headers=get_headers())
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code} for URL {url}")
        return None
    except Exception as e:
        print(f"Connection Error: {e}")
        return None

def save_war_data(data, prefix="warEnded"):
    end_time = data.get("endTime", "unknown_time").replace(":", "")
    filename = f"{prefix}_{end_time}.json"
    
    # Prevents saving the exact same war twice if the file already exists
    if os.path.exists(filename):
        print(f"Data for {filename} already exists. Skipping.")
        return

    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Successfully saved war data to {filename}")

def check_cwl_status(formatted_tag):
    print("Checking Clan War League status...")
    group_url = f"{PROXY_URL}{formatted_tag}/currentwar/leaguegroup"
    group_data = fetch_api(group_url)
    
    if not group_data or group_data.get("state") not in ["inWar", "ended"]:
        print("Not currently in a CWL.")
        return

    # Loop through the rounds to find active/ended war tags
    for round_info in group_data.get("rounds", []):
        war_tags = round_info.get("warTags", [])
        if not war_tags or war_tags[0] == "#0":
            continue # Round hasn't started yet
            
        for tag in war_tags:
            war_url = f"{CWL_WAR_URL}{tag.replace('#', '%23')}"
            war_data = fetch_api(war_url)
            
            if not war_data:
                continue
                
            # Check if our clan is in this specific CWL war
            clan1 = war_data.get("clan", {}).get("tag")
            clan2 = war_data.get("opponent", {}).get("tag")
            
            if CLAN_TAG in [clan1, clan2]:
                state = war_data.get("state")
                print(f"CWL Round State: {state}")
                if state == "warEnded":
                    save_war_data(war_data, prefix="cwlEnded")
                break # Found our clan's war for this round, move to the next round!

def check_war_status():
    if not API_TOKEN:
        print("Error: API Token not found in the vault!")
        return
        
    formatted_tag = CLAN_TAG.replace("#", "%23")
    print("Connecting to Clash of Clans API...")
    
    # 1. Check Regular War
    regular_war_url = f"{PROXY_URL}{formatted_tag}/currentwar"
    regular_data = fetch_api(regular_war_url)
    
    if regular_data:
        state = regular_data.get("state")
        print(f"Regular war state: {state}")
        
        if state == "warEnded":
            save_war_data(regular_data, prefix="warEnded")
        elif state == "notInWar":
            # 2. If no regular war, check CWL
            check_cwl_status(formatted_tag)
        else:
            print("Regular war is currently active. Doing nothing.")

if __name__ == "__main__":
    check_war_status()

#MIT License
#Copyright (c) 2024 Jose Diaz Ayala

import sqlite3
import os
import json
import base64
import platform

def base64_encode_value(value):
    """Encode the given byte value using Base64 and return as a string."""
    try:
        encoded_value = base64.b64encode(value).decode('utf-8')
        return encoded_value.replace("=", "").replace("+", "_").replace("/", "-")
    except Exception as e:
        print(f"Error encoding value: {e}")
        return ""

def fetch_cookies_from_network_directory(profile_path):
    network_path = os.path.join(profile_path, 'Network')
    cookie_db_path = os.path.join(network_path, 'Cookies')

    cookies_list = []

    if os.path.exists(cookie_db_path):
        try:
            conn = sqlite3.connect(cookie_db_path)
            cursor = conn.cursor()

            cursor.execute("PRAGMA table_info(cookies)")
            columns = [column[1] for column in cursor.fetchall()]

            cursor.execute("SELECT * FROM cookies")
            cookies_data = cursor.fetchall()

            for cookie in cookies_data:
                cookie_dict = {}
                for index, column_name in enumerate(columns):
                    value = cookie[index]
                    if isinstance(value, bytes) and column_name == "encrypted_value":
                        value = base64_encode_value(value)
                    elif isinstance(value, bytes):
                        value = value.decode('utf-8', 'ignore')
                    cookie_dict[column_name] = value
                
                cookies_list.append(cookie_dict)
            
            conn.close()

            return cookies_list

        except sqlite3.Error as e:
            print(f"SQLite error while fetching cookies from {profile_path}: {e}")
    else:
        print(f"No Cookies database found in {network_path}")

    return []


def main():
    main_drive = os.environ.get('SystemDrive', 'C:')  # Default to C: if SystemDrive is not available
    current_user = os.environ.get('USERNAME', 'Admin')  # Default to Admin if USERNAME is not available

    base_path = os.path.join(main_drive + '\\', f'Users\\{current_user}\\AppData\\Local\\Google\\Chrome\\User Data')


    print(f"Base Path: {base_path}")  # Debugging line

    for profile_num in range(1, 5):
        profile_path = os.path.join(base_path, f'Profile {profile_num}')
        
        print(f"Checking Profile Path for Profile {profile_num}: {profile_path}")  # Debugging line

        if os.path.exists(profile_path):
            print(f"Fetching cookies from Profile {profile_num}...")
            profile_cookies = fetch_cookies_from_network_directory(profile_path)

            if profile_cookies:
                json_file_path = f"profile_{profile_num}_cookies.json"
                with open(json_file_path, "w", encoding="utf-8") as outfile:
                    json.dump(profile_cookies, outfile, ensure_ascii=False, indent=4)
                
                print(f"Cookies from Profile {profile_num} exported to {json_file_path}")
            else:
                print(f"No cookies fetched for Profile {profile_num}")
        else:
            print(f"Profile {profile_num} does not exist.")

if __name__ == "__main__":
    main()

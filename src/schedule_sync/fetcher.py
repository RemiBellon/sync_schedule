import requests
from requests.auth import HTTPBasicAuth
import os

def download_schedule():
    # --- Link ---
    base_url = "https://ao.lpp.polytechnique.fr"
    share_token = "m3XzfANgmBjktpF"
    password = os.environ.get("NEXTCLOUD_PASSWORD", "cloud_password")

    # File name on the server
    file_name = "Schedule_PPF_2026_Core.ods"

    # Construction URL WebDAV
    webdav_url = f"{base_url}/public.php/webdav/{file_name}"

    print(f"Connection to server : {base_url}...")

    # Authentification WebDAV (Token = Username)
    auth = HTTPBasicAuth(share_token, password)
    headers = {'X-Requested-With': 'XMLHttpRequest'}

    # Download request
    response = requests.get(webdav_url, auth=auth, headers=headers, stream=True)

    if response.status_code == 200:
        # data file creation
        os.makedirs("data", exist_ok=True)
        output_path = os.path.join("data", "current_schedule.ods")

        # saving file
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"File downloaded and saved in : {output_path}")

    elif response.status_code == 404:
        print("No file")
    else:
        print(f"File not downloaded. Code HTTP: {response.status_code}")
        print(f"Details : {response.text}")

if __name__ == "__main__":
    download_schedule()
import requests
from requests.auth import HTTPBasicAuth
import os

def download_schedule() -> str:
    """
    Download the .ods schedule from the Nextcloud public share.

    Returns
    -------
    str
        Path of the downloaded file.

    Raises
    ------
    RuntimeError
        If the server does not return the file (HTTP code other than 200).
    """
    # --- Link ---
    base_url = "https://ao.lpp.polytechnique.fr"
    share_token = "m3XzfANgmBjktpF"
    password = os.environ.get("NEXTCLOUD_PASSWORD", "cloud_password")

    # File path on the server (relative to the share root)
    file_path = "Schedule/Schedule_PPF_2026_Core.ods"

    # Construction URL WebDAV
    webdav_url = f"{base_url}/public.php/webdav/{file_path}"

    print(f"Connection to server : {base_url}...")

    # Authentification WebDAV (Token = Username)
    auth = HTTPBasicAuth(share_token, password)
    headers = {'X-Requested-With': 'XMLHttpRequest'}

    # Download request
    response = requests.get(webdav_url, auth=auth, headers=headers, stream=True, timeout=60)

    if response.status_code != 200:
        # Stop here: the previous calendar stays online and the workflow fails
        raise RuntimeError(
            f"File not downloaded ({webdav_url}). Code HTTP: {response.status_code}"
        )

    # data file creation
    os.makedirs("data", exist_ok=True)
    output_path = os.path.join("data", "current_schedule.ods")

    # saving file
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"File downloaded and saved in : {output_path}")
    return output_path

if __name__ == "__main__":
    download_schedule()

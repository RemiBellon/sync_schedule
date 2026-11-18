import os

import requests
from requests.auth import HTTPBasicAuth

# --- Link ---
BASE_URL = "https://ao.lpp.polytechnique.fr"
SHARE_TOKEN = "m3XzfANgmBjktpF"

# Files to download: path on the server (relative to the share root) -> local file name.
# Each file covers a different period of the year; all of them end up in the same calendar.
SCHEDULE_FILES: dict[str, str] = {
    "Schedule/Schedule_PPF_2026_Core.ods": "current_schedule.ods",
    "Schedule/Schedule_PPF_2026_Electives.ods": "current_schedule_electives.ods",
}


def download_file(remote_path: str, local_name: str, output_dir: str = "data") -> str:
    """
    Download one .ods file from the Nextcloud public share.

    Parameters
    ----------
    remote_path : str
        Path of the file on the server, relative to the share root.
    local_name : str
        Name of the file saved in ``output_dir``.
    output_dir : str, optional
        Directory where the file is saved, by default ``"data"``.

    Returns
    -------
    str
        Path of the downloaded file.

    Raises
    ------
    RuntimeError
        If the server does not return the file (HTTP code other than 200).
    """
    password = os.environ.get("NEXTCLOUD_PASSWORD", "cloud_password")

    # Construction URL WebDAV
    webdav_url = f"{BASE_URL}/public.php/webdav/{remote_path}"

    print(f"Connection to server : {BASE_URL} ({remote_path})...")

    # Authentification WebDAV (Token = Username)
    auth = HTTPBasicAuth(SHARE_TOKEN, password)
    headers = {"X-Requested-With": "XMLHttpRequest"}

    # Download request
    response = requests.get(webdav_url, auth=auth, headers=headers, stream=True, timeout=60)

    if response.status_code != 200:
        # Stop here: the previous calendar stays online and the workflow fails
        raise RuntimeError(
            f"File not downloaded ({webdav_url}). Code HTTP: {response.status_code}"
        )

    # data file creation
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, local_name)

    # saving file
    with open(output_path, "wb") as f:
        f.writelines(response.iter_content(chunk_size=8192))
    print(f"File downloaded and saved in : {output_path}")
    return output_path


def download_schedule(output_dir: str = "data") -> list[str]:
    """
    Download every .ods schedule listed in ``SCHEDULE_FILES``.

    Parameters
    ----------
    output_dir : str, optional
        Directory where the files are saved, by default ``"data"``.

    Returns
    -------
    list of str
        Paths of the downloaded files, in the order of ``SCHEDULE_FILES``.

    Raises
    ------
    RuntimeError
        If any of the files cannot be downloaded.
    """
    return [
        download_file(remote_path, local_name, output_dir)
        for remote_path, local_name in SCHEDULE_FILES.items()
    ]


if __name__ == "__main__":
    download_schedule()

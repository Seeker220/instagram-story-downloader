from mailersend import emails
from datetime import datetime, timezone
import requests
import os
import subprocess
from urllib.parse import urlparse
import shutil
import random
import shutil
import zipfile
from zoneinfo import ZoneInfo
def current_datetime():
    """
    Returns the current date and time in the format YYYY-MM-DD HH:MM:SS.
    """
    # Get the current date and time
    now = datetime.now(timezone.utc)
    # Format the date and time
    formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_now
def log(text,logfile):
    with open(logfile, "a") as file:
        file.write(text + "\n")

def email(id,message):
    mailer = emails.NewEmail("mlsn.1b3ff5dbbb9dc288e184a9c18de317e1597b65d59295bd347de352066c52bb43")
    mail_body = {}
    recipients = [
        {
            "email": id,
        }
    ]
    mail_from = {
        "name": "Instagram Story Downloader Logs",
        "email": "instalogs@trial-z3m5jgr6nqogdpyo.mlsender.net",
    }
    sub="Instagram Story Downloader Errored on "+str(current_datetime())+" UTC"
    mailer.set_mail_from(mail_from, mail_body)
    mailer.set_mail_to(recipients, mail_body)
    mailer.set_subject(sub, mail_body)
    mailer.set_plaintext_content(message, mail_body)
    sent = mailer.send(mail_body)
    return sent

def sendlogs(id, templogs_file,logfile):
    # Check if the templogs file exists and is not empty
    if os.path.exists(templogs_file) and os.path.getsize(templogs_file) > 0:
        # Read the content of the templogs file
        with open(templogs_file, 'r') as file:
            log_content = file.read()

        try:
            email(id, log_content)
        except Exception as e:
            log(f"Error sending logs : {e}",logfile)
def get_username(user_id):
    # Set the URL with the specified user ID
    url = f"https://i.instagram.com/api/v1/users/{user_id}/info/"

    # Set the custom user agent for the request
    headers = {
        "User-Agent": "Instagram 85.0.0.21.100 Android (23/6.0.1; 538dpi; 1440x2560; LGE; LG-E425f; vee3e; en_US)"
    }

    # Make the GET request to the API
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        # Extract the username from the response data
        username = data.get('user', {}).get('username', None)
        return username
    else:
        return None


def download_story(story_data, story_folder,logfile):
    """
    Downloads the story to the specified folder using curl and saves them with the ID as the filename and the correct extension.

    Args:
    story_data (dict): The data containing the user and media information.
    story_folder (str): The folder where the story should be downloaded.
    """
    username = story_data["user"]["username"]
    user_folder = os.path.join(story_folder, username)

    # Create the directory if it doesn't exist
    os.makedirs(user_folder, exist_ok=True)

    for media in story_data["medias"]:
        url = media["url"]
        media_id = media["id"]

        # Extract the file extension from the URL path
        parsed_url = urlparse(url)
        extension = os.path.splitext(parsed_url.path)[1]

        # Construct the file name using the media ID and the extracted extension
        file_name = f"{media_id}{extension}"
        file_path = os.path.join(user_folder, file_name)

        # Download the file using curl
        curl_command = f'curl -L -o "{file_path}" "{url}"'
        subprocess.run(curl_command, shell=True)
        log(f"Downloaded {file_name} to {user_folder}",logfile)


def upload_story(story_folder, config_file, logfile, templogfile):
    try:
        # Ensure the story_folder exists
        if not os.path.exists(story_folder):
            log(f"Error: The folder '{story_folder}' does not exist.",logfile)
            return

        # Dynamically get the path to rclone.conf
        current_dir = os.getcwd()
        rclone_config_path = os.path.join(current_dir, config_file)

        # Remote path on Google Drive
        remote_path = "Drive:/Instagram Stories/Stories"

        log(f"Using rclone.conf from: {rclone_config_path}",logfile)
        log(f"Uploading from: {story_folder} to {remote_path}",logfile)

        # Construct the rclone command to upload the folder
        command = [
            "rclone",
            "copy",  # Copy files
            story_folder,  # Local folder
            remote_path,  # Remote destination
            f"--config={rclone_config_path}",  # Use specific rclone config
            "--ignore-existing",  # Skip files that already exist
            "--checksum",  # Compare file checksums (hash) instead of modification time
            "--create-empty-src-dirs"  # Create empty directories if needed
        ]

        # Execute the command and capture output
        result = subprocess.run(command, capture_output=True, text=True)

        # Check if the command was successful
        if result.returncode == 0:
            log("Upload completed successfully.",logfile)
            log(str(result.stdout),logfile)
        else:
            log("Error occurred during upload:",logfile)
            log(str(result.stderr),logfile)
    except Exception as e:
        log(f"Unexpected error: {e}",logfile)
        log(f"Unexpected error: {e}", templogfile)

def extract_username_from_url(url):
    parsed_url = urlparse(url)
    path_segments = parsed_url.path.strip('/').split('/')
    if len(path_segments) > 1 and path_segments[0] == 'stories':
        return path_segments[1]
    return path_segments[0]


def get_username(user_id):
    # Set the URL with the specified user ID
    url = f"https://i.instagram.com/api/v1/users/{user_id}/info/"

    # Set the custom user agent for the request
    headers = {
        "User-Agent": "Instagram 85.0.0.21.100 Android (23/6.0.1; 538dpi; 1440x2560; LGE; LG-E425f; vee3e; en_US)"
    }

    # Make the GET request to the API
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        # Extract the username from the response data
        username = data.get('user', {}).get('username', None)
        return username
    else:
        return None


def update_subs(subnum, logfile, subfile):
    try:
        # Read the subscriptions file and store lines in a list
        with open(subfile, "r") as file:
            lines = file.readlines()

        # Get the current subscription line (subnum is 0-based, so use it directly)
        subscription_line = lines[subnum].strip()  # subnum is 0-based, so no need to subtract 1

        # Split the subscription line into username and user ID
        username, user_id = subscription_line.split()

        # Get the current username from Instagram API using the user ID
        current_username = get_username(user_id)

        # If the username has changed, update the subscriptions file
        if current_username and current_username != username:
            # Log the change
            log(f"Username for user ID {user_id} changed from {username} to {current_username}.", logfile)

            # Update the line with the new username
            lines[subnum] = f"{current_username} {user_id}\n"

            # Write the updated lines back to the subscriptions file
            with open(subfile, "w") as file:
                file.writelines(lines)
            log(f"Updated {subfile} with new username for {user_id}.", logfile)
            return current_username
        else:
            log(f"No change in username for user ID {user_id}.", logfile)

    except Exception as e:
        log(f"Error updating subscriptions: {e}", logfile)

def delete_user_data_dir(user_dir, logfile):
    """Deletes the user directory and all its contents."""
    try:
        if os.path.exists(user_dir):
            shutil.rmtree(user_dir)
            log(f"Successfully deleted {user_dir}", logfile)
        else:
            log(f"Directory {user_dir} does not exist.", logfile)
    except Exception as e:
        log(f"Error deleting {user_dir}: {e}", logfile)





def randomsubs(subfile,logfile):
    subs = []
    try:
        # Open the subscriptions file
        with open(subfile, 'r') as file:
            # Read each line and parse it
            for idx, line in enumerate(file):
                # Strip any leading/trailing whitespace
                line = line.strip()

                # Skip empty lines
                if not line:
                    continue

                # Split the line into username and user_id
                username, user_id = line.split()

                # Append the tuple (line number, username, user_id) to the list
                subs.append((idx, username, user_id))

        # Shuffle the list to randomize the order
        random.shuffle(subs)

    except Exception as e:
        log(f"Error reading {subfile}: {e}",logfile)

    return subs


def reset_folder(folder_path):
    # Delete the folder if it exists
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)

    # Recreate the folder
    os.makedirs(folder_path)


def initlogs(logfile):
    """Initializes the logfile with newlines and the current date and time."""
    with open(logfile, "a") as file:
        file.write("\n" * 10)  # Add two newlines for separation
        file.write(f"Log Initialized: {current_datetime()}\n")
        file.write("=" * 50 + "\n")  # Add a separator line
    print(f"Logfile '{logfile}' initialized.")




def zip_default(user_dir, templogfile, logfile):
    try:
        default_folder_path = os.path.join(user_dir, "Default")
        zip_file_path = os.path.join(user_dir, "Default.zip")

        # Remove Cache and Code Cache folders if they exist
        for folder in ["Cache", "Code Cache"]:
            folder_path = os.path.join(default_folder_path, folder)
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
                log(f"Deleted {folder} folder from Default.", logfile)

        # Zip the Default folder
        with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(default_folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, user_dir)  # Maintain relative structure
                    zipf.write(file_path, arcname)

        log("Successfully zipped Default folder as Default.zip.", logfile)

    except Exception as e:
        log(f"Error occurred during zipping: {e}", templogfile)
        log(f"Error occurred during zipping: {e}", logfile)


def unzip_default(user_dir, templogfile, logfile):
    try:
        zip_file_path = os.path.join(user_dir, "Default.zip")
        default_folder_path = os.path.join(user_dir, "Default")

        # Delete existing Default folder if it exists
        if os.path.exists(default_folder_path):
            shutil.rmtree(default_folder_path)
            log("Deleted existing Default folder.", logfile)
        else:
            log(f"Default Folder not found : {default_folder_path}", logfile)
        # Extract Default.zip
        if os.path.exists(zip_file_path):
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(user_dir)
            log("Extracted Default.zip successfully.", logfile)

            # Delete Default.zip after extraction
            os.remove(zip_file_path)
            log("Deleted Default.zip after extraction.", logfile)
        else:
            log("Default.zip not found in user_dir.", logfile)

    except Exception as e:
        log(f"Error occurred during unzipping: {e}", templogfile)
        log(f"Error occurred during unzipping: {e}", logfile)



def get_persistent_files(cwd, logfile, user_dir, templogfile, config_file, user_email):
    try:
        remote_path = "Drive:/Instagram Stories/Persistent Data"

        command_logs = [
            "rclone",
            "copy",  # Copy files
            f"{remote_path}/logs.txt",  # Remote logs file
            cwd,  # Local path to overwrite
            "--config", config_file,  # Use specific rclone config
            "--checksum"  # Compare file checksums instead of modification time
        ]

        command_sub = [
            "rclone",
            "copy",  # Copy files
            f"{remote_path}/subscriptions.txt",  # Remote subscriptions file
            cwd,  # Local path to overwrite
            "--config", config_file,  # Use specific rclone config
            "--checksum"  # Compare file checksums instead of modification time
        ]

        # Execute command to fetch logs.txt
        result_logs = subprocess.run(command_logs, capture_output=True, text=True)
        if result_logs.returncode != 0:
            log("Error occurred while fetching logs.txt:", templogfile)
            log(str(result_logs.stderr), templogfile)
        initlogs(logfile)
        # Execute command to fetch subscriptions.txt
        result_sub = subprocess.run(command_sub, capture_output=True, text=True)
        if result_sub.returncode != 0:
            log("Error occurred while fetching subscriptions.txt:", templogfile)
            log(str(result_sub.stderr), templogfile)


        command_playwright = [
            "rclone",
            "copy",  # Copy files
            f"{remote_path}/playwright-data/",  # Remote playwright data folder
            user_dir,  # Local path to overwrite
            "--config", config_file,  # Use specific rclone config
        ]

        # Execute command to fetch playwright-data
        result_playwright = subprocess.run(command_playwright, capture_output=True, text=True)
        if result_playwright.returncode != 0:
            log("Error occurred while fetching playwright-data:", templogfile)
            log(str(result_playwright.stderr), templogfile)

        unzip_default(user_dir, templogfile, logfile)
        # Log success
        log("Persistent files fetched and overwritten successfully.", logfile)

    except Exception as e:
        log(f"Unexpected error: {e}", templogfile)
        log(f"Unexpected error: {e}", logfile)
        sendlogs(user_email, templogfile, logfile)
        exit()

def upload_ss(ssname, cwd, config_file, logfile, templogfile):
    try:
        remote_path = "Drive:/Instagram Stories/Persistent Data"
        ss_path = os.path.join(cwd, ssname)
        if os.path.exists(ss_path):
            command_ss_upload = [
                "rclone",
                "copy",
                ss_path,
                f"{remote_path}",
                "--config", config_file,
            ]
            result_ss_upload = subprocess.run(command_ss_upload, capture_output=True, text=True)
            if result_ss_upload.returncode != 0:
                log(f"Error occurred while uploading {ssname}:", templogfile)
                log(str(result_ss_upload.stderr), templogfile)
                log(str(result_ss_upload.stderr), logfile)
        else:
            log(f"Screenshot not found {ssname}",logfile)
            log(f"Screenshot not found {ssname}",templogfile)
    except Exception as e:
        log(f"Unexpected error: {e}", templogfile)
        log(f"Unexpected error: {e}", logfile)
def upload_persistent_files(logfile, subfile, user_dir, templogfile, config_file):
    try:
        remote_path = "Drive:/Instagram Stories/Persistent Data"

        # Log action
        log(f"Uploading persistent files to {remote_path}", logfile)

        # Command to upload logs.txt
        command_logs = [
            "rclone",
            "copy",
            logfile,
            f"{remote_path}",
            "--config", config_file,
        ]

        # Command to upload subscriptions.txt
        command_sub = [
            "rclone",
            "copy",
            subfile,
            f"{remote_path}",
            "--config", config_file,
        ]
        # Execute upload commands for logs and subscriptions
        result_logs = subprocess.run(command_logs, capture_output=True, text=True)
        if result_logs.returncode != 0:
            log("Error occurred while uploading logs.txt:", templogfile)
            log(str(result_logs.stderr), templogfile)

        result_sub = subprocess.run(command_sub, capture_output=True, text=True)
        if result_sub.returncode != 0:
            log("Error occurred while uploading subscriptions.txt:", templogfile)
            log(str(result_sub.stderr), templogfile)

        zip_default(user_dir, templogfile, logfile)
        # Paths to overwrite in drive
        remote_playwright_dir = f"{remote_path}/playwright-data/"
        # Overwrite Last Browser, Last Version, Local State, Variations
        important_files = ["Last Version", "Local State", "Variations", "Default.zip"]
        for file_name in important_files:
            local_file_path = os.path.join(user_dir, file_name)
            remote_file_path = f"{remote_playwright_dir}"
            command_file_upload = [
                "rclone",
                "copy",
                local_file_path,
                remote_file_path,
                "--config", config_file,
            ]
            result_file_upload = subprocess.run(command_file_upload, capture_output=True, text=True)
            if result_file_upload.returncode != 0:
                log(f"Error occurred while uploading {file_name}:", templogfile)
                log(str(result_file_upload.stderr), templogfile)
        log("Persistent files uploaded successfully.", logfile)

    except Exception as e:
        log(f"Unexpected error: {e}", templogfile)
        log(f"Unexpected error: {e}", logfile)
        exit()

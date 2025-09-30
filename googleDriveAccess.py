
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import shutil
# # Authenticate
gauth = GoogleAuth()
# gauth.LocalWebserverAuth()  # Opens browser for authentication

# drive = GoogleDrive(gauth)

# # Upload a file
# file_to_upload = drive.CreateFile({'title': 'example.txt'})
# file_to_upload.SetContentFile('example.txt')
# file_to_upload.Upload()

# print("File uploaded successfully!")

# gauth.LoadCredentialsFile("mycreds.txt")
# if gauth.credentials is None:
#     gauth.LocalWebserverAuth()
# elif gauth.access_token_expired:
#     gauth.Refresh()
# else:
#     gauth.Authorize()
# gauth.SaveCredentialsFile("mycreds.txt")

# try:
#     file_to_upload.Upload()
#     print("File uploaded successfully!")
# except Exception as e:
#     print(f"Upload failed: {e}")
# import os
# filename = 'example.txt'
# file_to_upload = drive.CreateFile({'title': os.path.basename(filename)})
# file_to_upload.SetContentFile(filename)
# Batch Upload with Metadata
# for filename in os.listdir('upload_folder'):
#     if filename.endswith('.txt'):
#         file = drive.CreateFile({'title': filename, 'description': 'Partner data - Bihar'})
#         file.SetContentFile(os.path.join('upload_folder', filename))
#         file.Upload()
# Folder Creation and Organization
# folder = drive.CreateFile({'title': 'Bihar Partners', 'mimeType': 'application/vnd.google-apps.folder'})
# folder.Upload()

# file = drive.CreateFile({'title': 'data.txt', 'parents': [{'id': folder['id']}]})
# file.SetContentFile('data.txt')
# file.Upload()

# Automated Sharing with Permissions
# file.Upload()
# file.InsertPermission({
#     'type': 'user',
#     'value': 'partner@example.com',
#     'role': 'reader'
# })
# Logging and Audit Trail
# import csv
# with open('upload_log.csv', 'a', newline='') as log:
#     writer = csv.writer(log)
#     writer.writerow([filename, folder['title'], file['id'], datetime.now()])

# Scheduled Uploads or Sync
# import schedule, time

# def upload_task():
#     # your upload logic here

# schedule.every().day.at("10:00").do(upload_task)

# while True:
#     schedule.run_pending()
#     time.sleep(60)

# from pydrive2.auth import GoogleAuth
# from pydrive2.drive import GoogleDrive
# from oauth2client.service_account import ServiceAccountCredentials

# # Path to the JSON key file you downloaded
# key_file_path = 'gen-lang-client-0992694401-e442ae76834f_ServiceAccount.json'

# # Define the scopes (the permissions the service account will have)
# scope = ['https://www.googleapis.com/auth/drive']

# # Authenticate using the service account credentials
# gauth = GoogleAuth()
# gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(key_file_path, scope)

# drive = GoogleDrive(gauth)

# # Now you can interact with Google Drive
# print("Authentication successful!")
# file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
# for file1 in file_list:
#     print(f'title: {file1["title"]}, id: {file1["id"]}')

# # Get and print the user ID
# about_me = drive.GetAbout()
# user_email = about_me['user']['emailAddress']
# user_id = about_me['user']['permissionId']
# print(f"User ID: {user_id}")
# print(f"User Email: {user_email}")

# print("\nListing files:")
# # List and print files from the user's root folder
# file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
# for file1 in file_list:
#     print(f'title: {file1["title"]}, id: {file1["id"]}')



import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive"]


# def main():
  # """Shows basic usage of the People API.
  # Prints the name of the first 10 connections.
  # """
creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            "client_secrets.json", SCOPES
        )
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
        token.write(creds.to_json())

try:
    pass
    service = build("drive", "v3", credentials=creds)
# Call the Drive v3 API to get about information (including storage)
    about = service.about().get(fields='storageQuota').execute()
    storage_quota = about.get('storageQuota')
    if storage_quota:
        limit_bytes = int(storage_quota.get('limit', 0))
        usage_bytes = int(storage_quota.get('usage', 0))
        available_bytes = limit_bytes - usage_bytes

        # Convert to more readable units (e.g., GB)
        limit_gb = limit_bytes / (1024**3)
        usage_gb = usage_bytes / (1024**3)
        available_gb = available_bytes / (1024**3)

        print(f"Total Storage Limit: {limit_gb:.2f} GB")
        print(f"Storage Used: {usage_gb:.2f} GB")
        print(f"Storage Available: {available_gb:.2f} GB")
    else:
        print("Could not retrieve storage quota information.")
# Call the People API
    print("Backup Started")
    results = service.files().list(
        q="name='TallyBackup' and mimeType='application/vnd.google-apps.folder'",
        spaces='drive'
    ).execute()
    if not results['files']:
        file_metaData = {
            "name": "TallyBackup",
            "mimeType": "application/vnd.google-apps.folder"
        }
        file = service.files().create(body=file_metaData, fields="id").execute()
        folder_id = file.get('id')
    else:
        folder_id = results['files'][0]['id']

    # connections = results.get("connections", [])

    for files in os.listdir('backupfiles'):
        file_metaData = {
            "name": files,
            "parents": [folder_id]
        }
        from googleapiclient.http import MediaFileUpload
        media = MediaFileUpload(f"backupfiles/{files}")
        upload_files = service.files().create(
            body=file_metaData,
            media_body=media,
            fields="id"
        ).execute()
        print("backed up files: " + files)
        # Get and print the user ID
        drive = GoogleDrive(gauth)
        about_me = drive.GetAbout()
        user_email = about_me['user']['emailAddress']
        user_id = about_me['user']['permissionId']
        print(f"User ID: {user_id}")
        print(f"User Email: {user_email}")
        # if names:
        #   name = names[0].get("displayName")
        #   print(name)
except HttpError as err:
    print(err)
# Calculate folder size and count files 
#import os

def get_folder_info(folder_path):
    """
    Calculates the total size of a folder and the number of files within it.

    Args:
        folder_path (str): The path to the folder.

    Returns:
        tuple: A tuple containing (total_size_bytes, file_count).
               Returns (0, 0) if the folder_path is invalid or empty.
    """
    total_size_bytes = 0
    file_count = 0

    if not os.path.isdir(folder_path):
        print(f"Error: '{folder_path}' is not a valid directory.")
        return 0, 0

    for dirpath, dirnames, filenames in os.walk(folder_path):
        for f in filenames:
            file_path = os.path.join(dirpath, f)
            if os.path.isfile(file_path):  # Ensure it's a file and not a broken link
                total_size_bytes += os.path.getsize(file_path)
                file_count += 1
    
    return total_size_bytes, file_count

def format_bytes(size_bytes):
    """
    Formats a size in bytes into a human-readable string (KB, MB, GB, etc.).
    """
    if size_bytes == 0:
        return "0 Bytes"
    
    sizes = ("Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = 0
    while size_bytes >= 1024 and i < len(sizes) - 1:
        size_bytes /= 1024
        i += 1
    return f"{size_bytes:.2f} {sizes[i]}"

# Example usage:
folder_to_check = "backupfiles"  # Replace with the actual folder path

total_size, num_files = get_folder_info(folder_to_check)

if total_size > 0 or num_files > 0:
    print(f"Folder: '{folder_to_check}'")
    print(f"Total Size: {format_bytes(total_size)}")
    print(f"Number of Files: {num_files}")
# if __name__ == "__main__":
#   main()
# Google Sheets API Setup Guide

To allow this automation to read and write to your Google Sheets, you need to set up a **Service Account** in Google Cloud.

## Step 1: Create a Google Cloud Project
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Click on the project dropdown at the top left.
3. Click **"New Project"**.
4. Give it a name (e.g., `MF-Automation`) and click **"Create"**.

## Step 2: Enable APIs
1. In the sidebar, go to **"APIs & Services" > "Library"**.
2. Search for **"Google Sheets API"** and click **"Enable"**.
3. Go back to the Library, search for **"Google Drive API"**, and click **"Enable"**.
   * *Note: Drive API is needed to access sheets shared with the service account.*

## Step 3: Create a Service Account
1. In the sidebar, go to **"APIs & Services" > "Credentials"**.
2. Click **"+ CREATE CREDENTIALS"** and select **"Service account"**.
3. **Service account details**:
   * Name: `sheet-bot` (or anything you like).
   * Click **"Create and Continue"**.
4. **Grant this service account access to project**:
   * Role: Select **"Editor"** (Basic > Editor).
   * Click **"Continue"**, then **"Done"**.

## Step 4: Download the Key (JSON)
1. You should now see your service account in the list (e.g., `sheet-bot@your-project.iam.gserviceaccount.com`).
2. Click on the **pencil icon** (Edit) or the email address to open details.
3. Go to the **"Keys"** tab.
4. Click **"Add Key" > "Create new key"**.
5. Select **"JSON"** and click **"Create"**.
6. A file will automatically download to your computer.

## Step 5: Configure the Project
1. Rename the downloaded file to `service_account.json`.
2. Move this file to the root folder of this project:
   `/Users/niteshnandan/workspace/2026/mf-automation/service_account.json`

## Step 6: Share Your Sheet (CRITICAL)
The service account is like a separate user with its own email address. It cannot see your sheets unless you share them.

1. Open your `service_account.json` file and find the `"client_email"` field.
   * It looks like: `sheet-bot@your-project.iam.gserviceaccount.com`
2. Copy this email address.
3. Open the Google Sheet you want to automate.
4. Click the **"Share"** button (top right).
5. Paste the service account email and ensure it has **"Editor"** permission.
6. Click **"Send"** (uncheck "Notify people" if you want, it doesn't matter).

## Step 7: Verify
Run the example script to test the connection:
```bash
python sheet_io_example.py
```

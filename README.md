# MyTNB Energy Data Downloader

An automated Python script using Playwright to securely log into the MyTNB portal and download daily and monthly electricity usage data into organized CSV files.

## 🌟 Features

* **Dual Download:** Automatically retrieves both monthly summary data and detailed daily breakdown data.
* **Secure Configuration:** Uses the external `config.ini` file to keep credentials and sensitive tokens out of the script and Git history.
* **Custom Filenames:** Saves files with dynamic date stamps (e.g., `monthly_usage_YYYYMMDD.csv`).
* **Headless Operation:** Runs silently in the background (headless mode) for efficiency.

---

## ⚠️ Security Note (Crucial!)

The `config.ini` file contains your password and account token. **NEVER** commit this file to GitHub or any public repository. Please ensure your sensitive data is kept private.

---

## 🛠️ Setup Guide

### 1. Prerequisites

You must have the following installed on your system:

* **Python:** Version 3.8 or newer.
* **Git:** To clone this repository.

### 2. Initial Setup

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/ixanza/MYTnBSmartMeterUsageDownloader
    cd MYTnBSmartMeterUsageDownloader
    ```

2.  **Install Python Dependencies:**
    The project uses `playwright` for automation and `configparser` for reading settings.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Install Playwright Browser Binaries:**
    Playwright needs its own browser engine to run.
    ```bash
    playwright install chromium
    ```

### 3. Configure Settings (`config.ini`)

The `config.ini` file is already present in the repository, but you must edit it with your credentials.

1.  **Open the `config.ini` file.**
2.  **Update the `[Credentials]` section** with your actual MyTNB login email and password.
3.  **Update the `[Navigation]` section** with your unique `caNo` token (see instructions below).

**Structure of `config.ini`:**
```ini
[Credentials]
USERNAME = your.email@example.com
PASSWORD = your_mytnb_password

[Navigation]
ENERGY_DASHBOARD_CA_NO = XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
DOWNLOAD_DIR_PATH = tnb_data
```
## 🔑 How to Get Your `ENERGY_DASHBOARD_CA_NO` Token

The `caNo` is a secure, unique token tied to your specific MyTNB account and is required for direct navigation to the energy dashboard.

1.  **Log in Manually:** Log into the MyTNB portal in your regular web browser.
2.  **Navigate to Usage:** Right click on the **"View Energy Usage"** button and copy link URL.
3.  **Inspect the URL:** It will follow this structure:

    `https://myaccount.mytnb.com.my/AccountManagement/SmartMeter/Index/TRIL?caNo=`**`[YOUR_UNIQUE_TOKEN]`**

4.  **Copy the Token:** Copy **only the value after `caNo=`**. This is the token you need, including any percent-encoded characters (e.g., `%2B`).

    *Example Token:* `&vc!ry1xjQ8y0w&D&e4^sGq!k8@1eOW7jKL3C#`

5.  **Paste into `config.ini`:** Paste this entire token into the `ENERGY_DASHBOARD_CA_NO` field in your `config.ini` file.

---

## 🚀 Execution

Once all dependencies are installed and `config.ini` is properly configured, run the script from your terminal:

```bash
python tnb_downloader.py
```

### Output Files

The script will save two files to the directory specified in your `config.ini` (e.g., `tnb_data/` by default):

* `monthly_usage_YYYYMMDD.csv`
* `daily_usage_YYYYMMDD.csv`

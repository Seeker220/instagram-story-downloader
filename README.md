# Instagram Story Downloader

A Python-based Instagram Story Downloader using Playwright, Rclone, Docker, and GitHub Actions to upload stories to Google Drive or OneDrive.

---

## Disclaimer

- This repo is in no way affiliated with Instagram.
- This is just for research purposes.
- **INSTAGRAM MIGHT BAN YOUR ACCOUNT. I WILL NOT BE RESPONSIBLE.** Please use a spare account if possible.

---

## Features

- Downloads Instagram stories for specified accounts.
- Supports both Google Drive and OneDrive as upload destinations.
- Avoids additional network requests to Instagram for enhanced privacy and reduced detection risk.
- Runs twice (at randomized times) daily.
- Sends error logs to user email. Also saves logs in a logfile.

---

## Setup Guide

### 🚀 **Getting Started**

Follow these steps to set up the Instagram Story Downloader on your own GitHub repository and configure it to run automatically.

---

### **📂 Step 1: Download the Repository**  

#### **Option 1: Clone Using Git (Recommended)**  
This keeps files updated easily.  

1. Open a terminal (**Command Prompt, PowerShell, Terminal, or Bash**).
2. Run the following commands:  
   ```sh
   git clone https://github.com/Seeker220/instagram-story-downloader.git
   cd instagram-story-downloader
   ```
3. Open the folder in **File Explorer**:  
   - **Windows:**  
     ```sh
     explorer .
     ```
   - **macOS:**  
     ```sh
     open .
     ```
   - **Linux (Ubuntu, GNOME-based):**  
     ```sh
     nautilus . &
     ```
     *(Use `xdg-open .` if you're on a different file manager.)*


#### **Option 2: Download as ZIP (For Non-Git Users)**  
1. Click **"Code"** (🔽) on the GitHub repo page and select **"Download ZIP"**.  
2. Extract the ZIP file to a folder on your computer.  
3. Open the folder and proceed with setup.  



---

### **📂 Step 2: Set Up Storage Drive and Subscriptions**

1. Open the cloud storage service where you want to save the downloaded Instagram stories (**Google Drive or OneDrive**).
2. **Ensure that there is no existing folder named **`Instagram Stories`** in the root directory** of your Drive.
3. **Edit the subscriptions file before uploading it to Drive**:
   - Open `repo-folder/Upload to Drive/Instagram Stories/Persistent Data/subscriptions.txt`.
   - Add the usernames of the Instagram accounts you want to download stories from.
   - The format should be:
     ```
     bbcnews 16278726
     twicetagram 2107411892
     ```
   - The number beside the username (after a space) is the **Instagram user ID**.
   - Write each subscription on a **new line**.
   - To find the Instagram user ID, follow this guide: [Find Instagram User ID](https://www.codeofaninja.com/tools/find-instagram-user-id/).
4. Navigate to `repo-folder/Upload to Drive/` and upload the `Instagram Stories` folder to your Drive root directory.

---

### **⚙️ Step 3: Get Rclone Configuration**

1. Open the `Get_Config.ipynb` file from GitHub and **open it in Google Colab**.
2. Run the notebook cell and authenticate with your Drive.
3. It will generate an `rclone.conf` file. **Copy the generated config** and paste it into:
   ```
   repo-folder/Docker Files/rclone.conf
   ```

---

### **🔑 Step 4: Generate a New Classic Token**  

1. Go to **GitHub → Account Settings → Developer Settings → Personal Access Tokens → Tokens (Classic)**.  
2. Click **"Generate new token (classic)"**.  
3. Select the following permissions:  
   - `write:packages`  
   - `read:packages`  
   - `repo`  
   - `workflow`  
4. Click **Generate token** and copy the token immediately. You won’t be able to see it again.  

---

### **📌 Step 5: Set Up GitHub Repository and Secrets**

1. Create a **new private GitHub repository** where you will configure the downloader. **MAKE SURE IT IS PRIVATE**.
2. Go to your **GitHub repository → Settings → Secrets and variables → Actions**.  
3. Click **"New repository secret"**.  
4. Add the following secrets one by one:  

   - **Name:** `GH_CLASSIC_TOKEN`  
     - **Value:** *(Paste the Classic PAT you copied in Step 4)*  

   - **Name:** `INSTA_USERNAME`  
     - **Value:** *(Your Instagram username)*  

   - **Name:** `INSTA_PASSWORD`  
     - **Value:** *(Your Instagram password)*  

   - **Name:** `USER_EMAIL`  
     - **Value:** *(Your email to receive logs)*  

5. **Ensure that GitHub Actions workflows have the required permissions**:  
   - Go to **Repository Settings → Actions → General**.  
   - Under **Workflow permissions**, select **Read and write permissions**.

---

### **🐫 Step 6: Install Docker and Build Image**  

#### **Windows & macOS:**  
- Install **Docker Desktop** and open its CLI.  

#### **Linux:**  
- Install **Docker CLI** using the appropriate package manager.  

#### **Build the Docker Image:**  

1. Open a terminal or command prompt.  
2. Navigate to the Docker Files directory:  
   ```sh
   cd "repo-folder/Docker Files"
   ```  
3. Build the Docker image:  
   ```sh
   docker build -t instagram-story-downloader .
   ```  
4. Run the following command sequentially in the terminal (replacing placeholders with your actual credentials):  
   ```sh
   docker run --rm \
     -e INSTA_USERNAME="your_username" \
     -e INSTA_PASSWORD="your_password" \
     -e USER_EMAIL="your_email@example.com" \
     instagram-story-downloader
   ```



---

### **📤 Step 7: Push Docker Image to GitHub Container Registry (GHCR)**

1. Authenticate with GitHub Container Registry using the **PAT created in Step 5**:
   ```sh
   echo {GH_CLASSIC_TOKEN} | docker login ghcr.io -u {YOUR_GITHUB_USERNAME} --password-stdin
   ```
2. Tag the Docker image:
   ```sh
   docker tag instagram-story-downloader ghcr.io/YOUR_GITHUB_USERNAME/instagram-story-downloader:latest
   ```
3. Push the Docker image to GHCR:
   ```sh
   docker push ghcr.io/YOUR_GITHUB_USERNAME/instagram-story-downloader:latest
   ```

---

### **📝 Step 8: Configure GitHub Actions**

1. Open the file:
   ```
   repo-folder/Github Actions Repo Files/.github/workflows/main-runner.yaml
   ```
2. Modify the **image link** in **lines 16 and 19** to match your **GitHub username**:
   ```yaml
   image: ghcr.io/YOUR_GITHUB_USERNAME/instagram-story-downloader:latest
   ```
3. Save the file.

---

### **📤 Step 9: Upload GitHub Actions Workflow**

1. Go to your new GitHub repository.
2. Upload the `.github` folder from `repo-folder/Github Actions Repo Files/` to your repo.

---

### **🚀 Step 10: Run the Workflow**

1. Navigate to the **Actions tab** in your GitHub repository.
2. Select `main-runner` workflow.
3. Click **Run workflow**.

🎉 **You're all set!** The downloader will now automatically run as per the scheduled cron job. 🚀

---

## Background and Inspiration:

I was in high school when I used to download Instagram stories of some of my celeb crushes. Then I found [AutoFetcher-IG-Stories-to-GDrive](https://github.com/chriskyfung/AutoFetcher-IG-Stories-to-GDrive) by **Chris K.Y. Fung**. It worked wonderfully and helped me so much. But with Instagram's increasing security and robot detection, my account used to get restricted for using it.

At last, I made my own downloader. **Chris is the single biggest inspiration for this project** 😊 (He also helped me a lot in making this) 😃.

Also I am bound to credit someone who went along me through this struggle, frustrated me, and un-frustrated me 😊 (they even wrote this README). Kudos ChatGPT! ❤️

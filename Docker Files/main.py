import asyncio
import os
import shutil
import random
import json
from mailersend import emails
from datetime import datetime, timezone
import requests
import subprocess
from urllib.parse import urlparse
import shutil
from playwright.async_api import async_playwright
from scripts.insta import *
from scripts.utils import *
ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
subfile = os.path.join(os.getcwd(), "subscriptions.txt")
user_dir = os.path.join(os.getcwd(), "playwright_data")
logfile = os.path.join(os.getcwd(), "logs.txt")
templogfile = os.path.join(os.getcwd(), "templogs.txt")
insta_username = "username" #Replace with your username
insta_password = "password" #Replace with your password
user_email = "mail@email.com" #Replace with your email
story_folder = os.path.join(os.getcwd(), "Stories")
config_file = os.path.join(os.getcwd(), "rclone.conf")
user_data_list = []
cwd = os.getcwd()
async def main_runner():
    reset_folder(story_folder)
    open(templogfile, 'w').close()
    get_persistent_files(cwd, logfile, user_dir, templogfile, config_file, user_email)
    async with async_playwright() as p:
        # Launch Chrome browser with persistent context and extension
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=user_dir,  # explicitly specify this as a keyword argument
            channel="chrome",
            user_agent=ua,
        )
        context = browser
        page = context.pages[0] if context.pages else await context.new_page(user_agent=ua)
        # Navigate to a website or perform any action
        await page.goto("https://www.instagram.com/" , timeout=60000)
        await random_wait(8,16)
        await page.screenshot(path="screenshot.png")
        upload_ss("screenshot.png",cwd,config_file,logfile,templogfile)
        await random_wait()
        notloggedin = await isnotloggedin(page)
        if notloggedin:
            print("Not Logged In")
            log("Not logged in. Trying to log in.",logfile)
            await browser.close()
            delete_user_data_dir(user_dir,logfile)
            browser = await p.chromium.launch_persistent_context(
                user_data_dir=user_dir,  # explicitly specify this as a keyword argument
                channel="chrome",
                user_agent=ua,
            )
            context = browser
            page = context.pages[0] if context.pages else await context.new_page(user_agent=ua)
            await login_handler(page,logfile,templogfile,insta_username,insta_password)
            # Navigate to a website or perform any action
            await page.goto("https://www.instagram.com/" , timeout=60000)
            await random_wait()
            await page.screenshot(path="screenshot1.png")
            upload_ss("screenshot1.png", cwd, config_file, logfile, templogfile)
        else:
            log("Already logged in.", logfile)
        log("Scrolling Randomly",logfile)
        await scroll_randomly(page)
        log("Stopped Scrolling",logfile)
        subs = randomsubs(subfile,logfile)
        for i in range(len(subs)):
            username = subs[i][1]
            subnum = subs[i][0]
            gtprfl = await gotoprofile(subnum,page,username,logfile,subfile,templogfile)
            if gtprfl=="No Searchbox":
                pdb = press_dismiss_button(page,logfile,templogfile)
                gtprfl2 = ""
                if pdb=="Pressed":
                    random_wait(1,10)
                    gtprfl2 = await gotoprofile(subnum,page,username,logfile,subfile,templogfile)
                    if gtprfl2=="Failed":
                        continue
                if pdb=="Not Found" or gtprfl2=="No Searchbox":
                    print("Dismiss button not found or Searchbox not found after pressing Dismiss. Trying to re-login.")
                    log("Dismiss button not found or Searchbox not found after pressing Dismiss. Trying to re-login.",logfile)
                    await browser.close()
                    delete_user_data_dir(user_dir, logfile)
                    browser = await p.chromium.launch_persistent_context(
                        user_data_dir=user_dir,  # explicitly specify this as a keyword argument
                        channel="chrome",
                        user_agent=ua,
                    )
                    context = browser
                    page = context.pages[0] if context.pages else await context.new_page(user_agent=ua)
                    await login_handler(page, logfile, templogfile, insta_username, insta_password)
                    # Navigate to a website or perform any action
                    await page.goto("https://www.instagram.com/", timeout=60000)
                    await random_wait()
                    await page.screenshot(path="screenshot2.png")
                    upload_ss("screenshot2.png", cwd, config_file, logfile, templogfile)
                    gtprfl3 = await gotoprofile(subnum, page, username, logfile, subfile, templogfile)
                    if gtprfl3=="No Searchbox":
                        print("No searchbox found on re-login.")
                        log("No searchbox found on re-login.",logfile)
                        log("No searchbox found on re-login.",templogfile)
                        upload_story(story_folder, config_file, logfile, templogfile)
                        upload_persistent_files(logfile,subfile,user_dir,templogfile,config_file)
                        sendlogs(user_email, templogfile, logfile)
                        exit()
            elif gtprfl=="Failed":
                await random_wait()
                continue
            nostories = False
            failed = False
            for t in range(3):
                stories = await getstories(page,username,logfile,templogfile)
                if stories == "No Stories":
                    failed = False
                    nostories = True
                    await random_wait()
                    break
                elif stories == "Failed":
                    log(f"Trying x{str(t)}",logfile)
                    failed = True
                    await random_wait()
                    continue
                else:
                    failed = False
                    await random_wait()
                    break
            if nostories:
                log("No stories found. Proceeding to next.",logfile)
                await random_wait()
                continue
            elif failed:
                log(f"3 tries failed. Couldn't download {username}. Proceeding to next.",logfile)
                log(f"3 tries failed. Couldn't download {username}. Proceeding to next.",templogfile)
                await random_wait()
                continue
            download_story(stories,story_folder,logfile)
        await browser.close()
        upload_story(story_folder,config_file,logfile,templogfile)
        upload_persistent_files(logfile,subfile,user_dir,templogfile,config_file)
        sendlogs(user_email,templogfile,logfile)
if __name__ == "__main__":
    asyncio.run(main_runner())
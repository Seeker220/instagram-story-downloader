import asyncio
import os
import shutil
import random
import json
from playwright.async_api import async_playwright
from .utils import *
user_data_list = []
# Async function for random wait
async def random_wait(min_time=2, max_time=5):
    """Waits for a random time between min_time and max_time seconds."""
    await asyncio.sleep(random.uniform(min_time, max_time))



# Async login handler
async def login_handler(page, logfile, templogfile, insta_username, insta_password):
    try:
            await page.goto("https://www.instagram.com/accounts/login/")
            await page.wait_for_load_state("networkidle", timeout=60000)
            await random_wait()
            log("Logging in...", logfile)
            usernamefield = page.locator("input[name='username']")
            await usernamefield.click()
            await random_wait()
            await usernamefield.fill(insta_username)
            await random_wait()
            passwordfield  = page.locator("input[name='password']")
            await random_wait()
            await passwordfield.click()
            await passwordfield.fill(insta_password)
            await random_wait()

            submitbutton = page.locator("button[type='submit']")
            await submitbutton.click()
            await page.wait_for_load_state("networkidle")
            await random_wait()

            try:
                save_info_button = page.locator('button', has_text="Save info")
                log("Clicking 'Save info' button...", logfile)
                await save_info_button.click()
                log("Successfully clicked 'Save info' button.", logfile)
            except Exception as e:
                log(f"Error clicking 'Save info' button: {e}", logfile)

    except Exception as e:
        log(f"Error during login: {e}", logfile)
        log(f"Error during login: {e}", templogfile)



async def closecurrent(page):
    current_url = await page.evaluate("window.location.href")
    if current_url in ["https://www.instagram.com/","https://www.instagram.com"]:
        return
    try:
        closebutton = await page.wait_for_selector('svg[aria-label="Close"]', state='visible', timeout=30000)
        await closebutton.click()
    except:
        pass

async def isnotloggedin(page):
    usernamefield = page.locator("input[name='username']")

    # Return True if the login button is visible, meaning the user is not logged in
    return await usernamefield.is_visible()

async def scroll_randomly(page):
    # Randomly choose a duration between 1 and 10 seconds
    duration = random.uniform(1, 10)
    # Randomly choose a scroll interval between 0.1 and 0.5 seconds
    scroll_interval = random.uniform(0.1, 0.5)
    # Randomly choose a scroll distance between 50 and 100 pixels per interval
    scroll_distance = random.uniform(50, 100)

    end_time = asyncio.get_event_loop().time() + duration
    while asyncio.get_event_loop().time() < end_time:
        # Scroll down by the chosen scroll distance
        await page.evaluate(f'window.scrollBy(0, {scroll_distance})')
        # Wait for the chosen interval before scrolling again
        await asyncio.sleep(scroll_interval)



# Log function
def log(text, logfile):
    with open(logfile, "a") as file:
        file.write(text + "\n")


async def gotoprofile(subnum, page, username, logfile, subfile, templogfile):
    try:
        await closecurrent(page)
        await random_wait(10,30)
        await page.wait_for_selector('svg[aria-label="Search"]', state='visible', timeout=30000)
        log("Search button is visible, clicking search.", logfile)
        # Click on the search button
        await page.click('svg[aria-label="Search"]')
        await random_wait(1, 3)
        # Wait for the search box to be visible and fill it with the username
        try:
            searchbox = await page.wait_for_selector("//input[@placeholder='Search']", state='visible', timeout=30000)
        except:
            return "No Searchbox"
        await searchbox.fill('')
        log(f"Searching for username: {username}", logfile)

        keyword = username
        await random_wait(1, 3)
        await searchbox.type(keyword)
        # Wait for the first result and click it
        await random_wait(5,10)
        await random_wait()
        first_result = page.locator(f'//span[text()="{keyword}"]').first
        await first_result.click()

        await random_wait(10,30)
        await random_wait()
        # After navigating, get the current URL and check the username
        current_url = await page.evaluate("window.location.href")
        log(f"Current URL after navigation: {current_url}", logfile)

        current_username = extract_username_from_url(current_url)

        if current_username == username:
            log("Username Reached!", logfile)
        else:
            log(f"Username Not Reached! Current: {current_username}, Expected: {username}", logfile)
            log(f"Username Not Reached! Current: {current_username}, Expected: {username}", templogfile)
            update_subs(subnum,logfile,subfile)
    except Exception as e:
        log(f"Error occurred while navigating to profile: {e}. Proceeding to next sub.", logfile)
        log(f"Error occurred while navigating to profile of {username} : {e}. Proceeding to next sub.", templogfile)
        return "Failed"



async def log_response(response, current_username, logfile):
    if "www.instagram.com/graphql/query" in response.url:
        body = await response.text()
        try:
            json_body = json.loads(body)
            # Check if the response contains the specific JSON structure
            if "data" in json_body and "xdt_api__v1__feed__reels_media" in json_body["data"]:
                reels_media = json_body["data"]["xdt_api__v1__feed__reels_media"]["reels_media"]
                for reel in reels_media:
                    if reel["user"]["username"] == current_username:
                        # Format the output as specified
                        reels_data = {
                            "user": {
                                "username": reel["user"]["username"],
                            },
                            "medias": []
                        }
                        for item in reel["items"]:
                            media = {
                                "url": item["image_versions2"]["candidates"][0]["url"] if item["media_type"] == 1 else item["video_versions"][0]["url"],
                                "isVideo": item["media_type"] != 1,
                                "id": item["pk"]
                            }
                            reels_data["medias"].append(media)

                        # Log the formatted result instead of printing
                        log(f"const data = {json.dumps(reels_data, indent=4)};", logfile)
                        return reels_data
        except Exception as e:
            log(str(e),logfile)


async def getstories(page, username, logfile,templogfile):
    global user_data_list
    user_data_list = []
    current_url = await page.evaluate("window.location.href")
    log(f"Current URL: {current_url}", logfile)

    current_username = extract_username_from_url(current_url)

    if current_username != username:
        log(f"Username Not Reached! Current: {current_username}, Expected: {username}", logfile)
        log(f"Username Not Reached! Current: {current_username}, Expected: {username}", templogfile)
        return "Failed"
    async def response_handler(response):
        global user_data_list
        ud = await log_response(response, current_username, logfile)
        if ud is not None:
            user_data_list.append(ud)
    await random_wait(10,30)
    # Add random wait here for async operation before interacting
    await random_wait(5,10)
    storycircle = page.locator("canvas.x1upo8f9.xpdipgo.x87ps6o")
    hasstory = await storycircle.is_visible()
    if not hasstory:
        log("No Stories. Proceeding to next.",logfile)
        return "No Stories"
    else:
        log("Has Story Circle.",logfile)

    log(f"Recording network traffic for 10 seconds for username: {current_username}", logfile)
    page.on("response", response_handler)

    await storycircle.click()

    await asyncio.sleep(10)
    page.remove_listener("response", response_handler)

    log("Stopped recording network traffic.", logfile)

    log(f"User data list: {user_data_list}", logfile)

    if len(user_data_list) == 0:
        log("Story Circle visible but couldn't open page.", logfile)
        log(f"Story Circle of {username} visible but couldn't open page.", templogfile)
        return "Failed"
    else:
        return user_data_list[0]

async def press_dismiss_button(page, logfile, templogfile):
    try:
        dismiss_button = page.locator('div[role="button"][aria-label="Dismiss"]')
        if await dismiss_button.is_visible():
            await dismiss_button.click()
            log("Successfully clicked the 'Dismiss' button.", logfile)
            return "Pressed"
        else:
            log("Dismiss button not found.", logfile)
            return "Not Found"
    except Exception as e:
        log(f"Error pressing 'Dismiss' button: {e}", logfile)
        log(f"Error pressing 'Dismiss' button: {e}", templogfile)

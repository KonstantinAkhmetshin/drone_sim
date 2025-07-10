"""
Browser crawler
"""

from camoufox.sync_api import Camoufox
import requests
import time
import json


# POST
#https://www.recreation.gov/api/camps/reservations/campgrounds/232296/multi

def get_payload():
    return {
        "reservations": [
            {
                "account_id": "cpsf3sa35g14bh43o3ag",
                "campsite_id": "232296",
                "check_in": "2025-06-18T00:00:00.000Z",
                "check_out": "2025-06-19T00:00:00.000Z",
                "reservation_options": {
                    "night_map": {
                        "2025-06-18T00:00:00.000Z": {
                            "campsite_id": "63635",
                            "campsite_loop": "COUN",
                            "campsite_name": "1"
                        }
                    },
                    "recommendation_referrer": "campground-v1:campgroundPage"
                }
            }
        ],
        "gate_a": {
            "value": "03AFcWeA6dpacH0XAfW1SNUecWBi9OpVIVvb9dwNhqTUGirVAPHfmCxkp_3ArvjHpEq3raX_sVgwxYBoPIn0CJsikEPFBRor69eMNE_VTlNtVt4HY0Y-wDzjlTUbSVSrK1rSlMSLk-dtQGHzm4-e4_lWofHub_5hyvhBPJCds7ECZ5VrdHGSwW7Rz-V68D69NUMV6pPk-B5THy4uHWTtPrQ17yKH4iXUFYgOy1wNnauU6NB7UgDp6mOyhpHIB7icQTHif276KL5kPHKJ8hWY7lmfTMhNbaftDg8xZLzNleYMLQ3n2g-x8OHJyujhYLaBhE1NcIvC75T-rKqaIoUZeqybLpwQxd2wH6xefoFHnqxgM0lIfp4yXzsV4S7UCye3QWanTVpUBnt9NZBxXNE40VLPvapr0K8rWiE-JeCH8cckL5jNDeEOqPdme5fk8rvSR-PHqU14Dk3vu6J_Kyf2-vAfq8S-2XAAr-",
            "description": "campsiteListBooking",
            "success": True,
            "terminal": "east"
        }
    }



def get_cook(page, recaccount):
    cookies = page.context.cookies()
    cookie_jar = {cookie['name']: cookie['value'] for cookie in cookies}

    # Extract headers from Playwright
    headers = {
        "User-Agent": page.evaluate("navigator.userAgent"),
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Referer": page.url,
        "Origin": "https://www.recreation.gov",
        "Authorization": f"Bearer {recaccount.get('access_token')}"
    }   
    return cookie_jar, headers, cookies

with Camoufox() as browser:
    page = browser.new_page()
    page.goto("https://www.recreation.gov/")
    page.screenshot(path="screenshot-1.png")
    #login page    
    page.click("button#ga-global-nav-log-in-link")

    page.screenshot(path="screenshot-2.png")
    # user name and pass
    page.fill("input#email", "konstantin.akhmetshin@gmail.com")
    page.fill("input#rec-acct-sign-in-password", "ko11AH06@89!")
    page.screenshot(path="screenshot-3.png")
    # click login
    page.click("button.rec-acct-sign-in-btn")
    time.sleep(3)
    page.screenshot(path="screenshot-4.png")
    # open camp site
    page.goto("https://www.recreation.gov/camping/campgrounds/232296")
    time.sleep(3)
    page.screenshot(path="screenshot-5.png")
    # get acount ID from local storage
    recaccount = json.loads(page.evaluate("localStorage.getItem('recaccount')"))


    [cookie_jar, headers, cookies] = get_cook(page, recaccount)


    url = "https://www.recreation.gov/api/camps/reservations/campgrounds/232296/multi"

    response = requests.post(url, json=get_payload(), cookies=cookie_jar, headers=headers)

    if response.status_code == 200:
        print("Reservation successful!")
        print(response.text)
    else:
        print(f"Failed to reserve: {response.status_code}")
        print(response.text)

    time.sleep(3)
    # open cart
    page.click("#ga-global-nav-account-cart-link")
    time.sleep(3)

    page.screenshot(path="screenshot-6.png")
    
    browser.close()






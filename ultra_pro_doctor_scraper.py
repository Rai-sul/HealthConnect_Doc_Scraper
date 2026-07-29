import os
import re
import time
import random
import shutil
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# Only real doctor data + local images

# ---------------- CONFIG ----------------
BASE_URL = "https://www.doctorbangladesh.com"
PAGE_URL = "https://www.doctorbangladesh.com/anesthesiologist-dhaka/"

CSV_NAME = "anesthesiologist.csv"
IMAGE_FOLDER = "anesthesiologist"

MAX_WORKERS = 10
TIMEOUT = 20
RETRY = 3

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

os.makedirs(IMAGE_FOLDER, exist_ok=True)

# =====================================================
# HELPERS
# =====================================================

def clean_text(text):
    if not text:
        return None
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def safe_filename(text):
    text = clean_text(text)
    text = re.sub(r'[^a-zA-Z0-9\s-]', '', text)
    text = text.replace(" ", "-").lower()
    return text[:120]


def request_html(url):
    for _ in range(RETRY):
        try:
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            r.raise_for_status()
            return r.text
        except:
            time.sleep(random.uniform(1, 2))
    return None


def extract_text(tag):
    if not tag:
        return None
    return clean_text(tag.get_text(" ", strip=True))


def get_image_url(img):
    if not img:
        return None

    for attr in ["src", "data-src", "data-lazy-src", "srcset"]:
        val = img.get(attr)

        if val:
            if attr == "srcset":
                val = val.split(",")[0].split()[0]

            return urljoin(BASE_URL, val.strip())

    return None


def file_ext(url):
    ext = os.path.splitext(urlparse(url).path)[1].lower()
    if ext in [".jpg", ".jpeg", ".png", ".webp"]:
        return ext
    return ".jpg"


def download_image(url, doctor_name):
    if not url:
        return None

    try:
        filename = safe_filename(doctor_name) + file_ext(url)
        filepath = os.path.join(IMAGE_FOLDER, filename)

        if os.path.exists(filepath):
            return filepath

        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()

        with open(filepath, "wb") as f:
            f.write(r.content)

        return filepath

    except:
        return None


# PROFILE PAGE SCRAPER

def scrape_profile(profile_url):

    result = {
        "extra_chambers": None,
        "extra_addresses": None,
        "extra_visiting_hours": None,
        "appointments": None,
        "about": None
    }

    html = request_html(profile_url)

    if not html:
        return result

    soup = BeautifulSoup(html, "lxml")
    entry = soup.find("div", class_="entry-content")

    if not entry:
        return result

    chambers = []
    addresses = []
    hours = []
    phones = []

    for h2 in entry.find_all("h2"):

        heading = extract_text(h2)

        if not heading:
            continue

        # ABOUT SECTION
        if "About" in heading:
            p = h2.find_next_sibling("p")
            if p:
                result["about"] = extract_text(p)
            break

        p = h2.find_next_sibling("p")
        if not p:
            continue

        txt = extract_text(p)

        # -------------------------------------------------
        # HOSPITAL / PLACE NAME
        # usually inside <strong><a>Hospital Name</a></strong>
        # -------------------------------------------------
        place_name = None

        strong_tag = p.find("strong")
        if strong_tag:
            place_name = extract_text(strong_tag)

        if not place_name:
            place_name = heading

        chambers.append(place_name)

        # -------------------------------------------------
        # ADDRESS
        # -------------------------------------------------
        m1 = re.search(r'Address:\s*(.*?)\s*Visiting Hour:', txt)

        if m1:
            pure_address = clean_text(m1.group(1))
            full_address = f"[{place_name}] {pure_address}"
            addresses.append(full_address)

        # -------------------------------------------------
        # VISITING HOUR
        # -------------------------------------------------
        m2 = re.search(r'Visiting Hour:\s*(.*?)\s*Appointment:', txt)

        if m2:
            hours.append(clean_text(m2.group(1)))

        # -------------------------------------------------
        # PHONE
        # -------------------------------------------------
        m3 = re.search(r'Appointment:\s*([+0-9]+)', txt)

        if m3:
            phones.append(clean_text(m3.group(1)))

    result["extra_chambers"] = " | ".join(chambers) if chambers else None
    result["extra_addresses"] = " | ".join(addresses) if addresses else None
    result["extra_visiting_hours"] = " | ".join(hours) if hours else None
    result["appointments"] = " | ".join(phones) if phones else None

    return result


# =====================================================
# SCRAPE MAIN LISTING PAGE
# =====================================================

html = request_html(PAGE_URL)

if not html:
    print("Page failed to load")
    exit()

soup = BeautifulSoup(html, "lxml")
doctors = soup.find_all("li", class_="doctor")

print("Doctors Found:", len(doctors))

rows = []

for doctor in doctors:

    title = extract_text(doctor.find("h3", class_="title"))

    img = doctor.find("img")
    image_url = get_image_url(img)

    call = doctor.find("a", class_="call-now")
    profile_url = call["href"] if call else None

    degree = speciality = experience = designation = workplace = None
    chamber = address = visiting_hour = None

    doctor_info = doctor.find("ul", class_="doctor-info")

    if doctor_info:
        for li in doctor_info.find_all("li"):

            li_title = li.get("title", "").strip()
            txt = extract_text(li)

            if li_title == "Degree":
                degree = txt
            elif li_title == "Experiences":
                experience = txt
            elif li_title == "Specialty":
                speciality = txt
            elif li_title == "Designation":
                designation = txt
            elif li_title == "Workplace":
                workplace = txt

    chamber_info = doctor.find("ul", class_="chamber-info")

    if chamber_info:
        for li in chamber_info.find_all("li"):

            li_title = li.get("title", "").strip()
            txt = extract_text(li)

            if li_title == "Chamber":
                chamber = txt
            elif li_title == "Address":
                address = txt.replace("Address:", "").strip()
            elif li_title == "Visiting Hour":
                visiting_hour = txt.replace("Visiting Hour:", "").strip()

    rows.append({
        "image_url": image_url,          # temp only
        "profile_url": profile_url,     # temp only

        "title": title,
        "degree": degree,
        "speciality": speciality,
        "experience": experience,
        "designation": designation,
        "workplace": workplace,

        "chamber": chamber,
        "address": address,
        "visiting_hour": visiting_hour
    })


# =====================================================
# THREAD PROCESSING
# =====================================================

def process_row(row):

    # profile scrape
    extra = scrape_profile(row["profile_url"])
    row.update(extra)

    # download image locally
    row["photo"] = download_image(row["image_url"], row["title"])

    # remove urls completely
    row.pop("image_url", None)
    row.pop("profile_url", None)

    return row


final_rows = []

with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:

    futures = [executor.submit(process_row, row) for row in rows]

    for future in as_completed(futures):
        final_rows.append(future.result())


# =====================================================
# DATAFRAME
# =====================================================

df = pd.DataFrame(final_rows)

df = df.drop_duplicates(subset=["title"])
df = df.fillna("null")

df = df[
    [
        "photo",
        "title",
        "degree",
        "speciality",
        "experience",
        "designation",
        "workplace",
        "chamber",
        "address",
        "visiting_hour",
        "extra_chambers",
        "extra_addresses",
        "extra_visiting_hours",
        "appointments",
        "about"
    ]
]

# save
df.to_csv(CSV_NAME, index=False, encoding="utf-8-sig")

# zip images
shutil.make_archive(IMAGE_FOLDER, "zip", IMAGE_FOLDER)

print(df.head())
print("Total Doctors:", len(df))
print("CSV Saved:", CSV_NAME)
print("ZIP Saved:", IMAGE_FOLDER + ".zip")

import shutil
import os

# Specify the path to the folder you want to delete
folder_to_delete = 'diabetologist' # Replace with your folder path

if os.path.exists(folder_to_delete):
    try:
        shutil.rmtree(folder_to_delete)
        print(f"Folder '{folder_to_delete}' and its contents deleted successfully.")
    except OSError as e:
        print(f"Error: {e.filename} - {e.strerror}.")
else:
    print(f"Folder '{folder_to_delete}' does not exist.")
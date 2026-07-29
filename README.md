Scraper

A Python web scraper that collects anesthesiologist information from theDoctor Bangladesh website, downloads doctor profile images, and exports theresult as a clean CSV dataset.

What the Script Does

The script:

Requests the Dhaka anesthesiologist listing page.

Extracts the available doctor information from each listing.

Visits individual profile pages concurrently to collect additional chamber,appointment, and biography information.

Downloads doctor profile images to a local folder.

Removes temporary source URL fields from the final dataset.

Removes duplicate records based on the doctor's title/name.

Exports the cleaned data to a UTF-8 CSV file.

Creates a ZIP archive containing the downloaded images.

Data Collected

The generated CSV contains the following columns:

Column

Description

photo

Local path of the downloaded profile image

title

Doctor's name and title

degree

Academic and professional qualifications

speciality

Medical specialty

experience

Experience information shown on the source page

designation

Current professional designation

workplace

Hospital or organization where the doctor works

chamber

Primary chamber name

address

Primary chamber address

visiting_hour

Primary visiting schedule

extra_chambers

Additional chamber names, separated by |

extra_addresses

Additional chamber addresses, separated by |

extra_visiting_hours

Additional visiting schedules, separated by |

appointments

Public appointment phone numbers, separated by |

about

Profile description from the doctor's page

Missing values are saved as the string null.

Requirements

Python 3

Internet access

The following Python packages:

requests

beautifulsoup4

pandas

lxml

Installation

1. Clone the repository

git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY

Replace the placeholder URL with your actual GitHub repository URL.

2. Create a virtual environment

python -m venv .venv

Activate it on Linux or macOS:

source .venv/bin/activate

Activate it on Windows PowerShell:

.\.venv\Scripts\Activate.ps1

3. Install the dependencies

python -m pip install requests beautifulsoup4 pandas lxml

Configuration

The scraper is configured through constants near the beginning ofultra_pro_doctor_scraper.py:

Setting

Default value

Purpose

BASE_URL

https://www.doctorbangladesh.com

Base URL used to resolve relative links

PAGE_URL

Anesthesiologist listing for Dhaka

Listing page to scrape

CSV_NAME

anesthesiologist.csv

Name of the generated CSV file

IMAGE_FOLDER

anesthesiologist

Directory used for downloaded images

MAX_WORKERS

10

Maximum concurrent profile-processing threads

TIMEOUT

20

HTTP timeout in seconds

RETRY

3

Maximum number of listing/profile request attempts

To scrape another category, update PAGE_URL, CSV_NAME, and IMAGE_FOLDERbefore running the program. The target page must use an HTML structurecompatible with the selectors in this script.

Important Safety Warning

The current script ends with code that recursively deletes a local directorynamed diabetologist if that directory exists:

folder_to_delete = "diabetologist"
shutil.rmtree(folder_to_delete)

Review or remove that cleanup block before running the scraper. Do not changethe value to a directory containing files you want to keep.

Usage

Run the script from the repository directory:

python ultra_pro_doctor_scraper.py

The script prints:

The number of doctor listings found

A preview of the generated DataFrame

The total number of exported doctors

The generated CSV and ZIP filenames

Generated Files

With the default configuration, a successful run creates:

.
├── anesthesiologist.csv
├── anesthesiologist/
│   ├── doctor-name-1.jpg
│   ├── doctor-name-2.webp
│   └── ...
└── anesthesiologist.zip

The CSV uses utf-8-sig encoding, which helps preserve text when the file isopened in spreadsheet software.

How It Works

Listing-page extraction

The scraper finds list items with the doctor class and extracts fields fromthe doctor-info and chamber-info sections.

Profile-page extraction

For each available profile URL, the scraper looks inside the entry-contentsection and collects additional chambers, addresses, visiting hours,appointment numbers, and the profile's About text.

Concurrent processing

ThreadPoolExecutor processes up to MAX_WORKERS doctor profiles at the sametime. Because completed futures are collected as they finish, output row orderis not guaranteed to match the website's listing order.

Image handling

Images are downloaded into IMAGE_FOLDER. Filenames are produced from asanitized lowercase version of the doctor's name. Existing files with the samegenerated path are reused rather than downloaded again.

Known Limitations

The scraper depends on the website's current HTML classes, headings, and textlabels. Website layout changes can cause missing or incorrect values.

Broad exception handlers suppress detailed network and image-download errors.

Failed values are generally exported as null, so a completed run does notguarantee that every field was collected.

Records are deduplicated only by title; two different doctors with the samedisplayed name could be treated as duplicates.

Image filenames are also derived from the displayed name, so identical namescan produce filename collisions.

Appointment parsing accepts only a limited phone-number format.

Concurrent completion order makes CSV row order nondeterministic.

The script has no command-line arguments, automated tests, structuredlogging, or resumable checkpoint system.

Responsible Use

Before scraping any website:

Review its terms of service and robots.txt.

Confirm that your collection and reuse of data is permitted by applicablerules and laws.

Use a conservative request rate and avoid disrupting the website.

Treat phone numbers, biographies, schedules, and images responsibly, evenwhen they are publicly displayed.

Recheck important medical-directory information against an authoritativesource before relying on it.

You are responsible for how you run the script and use the collected data.

Troubleshooting

Page failed to load

Check your internet connection, confirm that PAGE_URL is reachable, andverify that the website has not blocked or rate-limited the requests.

ModuleNotFoundError

Activate the project's virtual environment and reinstall the dependencies:

python -m pip install requests beautifulsoup4 pandas lxml

Zero doctors found

The source page may have changed its HTML structure. Inspect the page and checkwhether doctor entries still use:

<li class="doctor">

Empty profile fields

Profile extraction expects an entry-content container, h2 section headings,and text labels such as Address:, Visiting Hour:, and Appointment:.Changes to those elements require corresponding selector or regular-expressionupdates.

Suggested Repository Structure

doctor-scraper/
├── ultra_pro_doctor_scraper.py
├── README.md
├── requirements.txt
└── .gitignore

A suitable requirements.txt would contain:

beautifulsoup4
lxml
pandas
requests

Generated datasets and images can be excluded from Git when they should not becommitted:

.venv/
__pycache__/
*.py[cod]
anesthesiologist/
anesthesiologist.csv
anesthesiologist.zip

License

No license is declared by the provided project files. Add a license only afterchoosing terms that match how you want others to use your code. The sourcewebsite's content may have separate rights and usage conditions that are notgranted by a code license.
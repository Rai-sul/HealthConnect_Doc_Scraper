# HealthConnect Doc Scraper

A small Python scraper that extracts doctor listings and profile information from doctorbangladesh.com and exports a cleaned CSV and downloaded profile images.

This repository contains a practical example script for gathering publicly-available directory data. Use responsibly — see the Responsible Use section below.

---

## Quick summary

- Scrapes listing pages and individual profile pages.
- Downloads profile images to a local folder and creates a ZIP archive.
- Exports a cleaned UTF-8 CSV with columns such as title, degree, speciality, workplace, chamber, address, visiting hours, appointments, and about text.


## Files

- `healthconnect_doc_scraper.py` — main scraper script (run from the repository root).
- `HealthConnect_doc_Scraper.ipynb` — Jupyter notebook version / analysis (if present).
- `README.md` — this file.


## Installation

1. Clone the repository

   git clone https://github.com/Rai-sul/HealthConnect_Doc_Scraper.git
   cd HealthConnect_Doc_Scraper

2. (Recommended) Create a virtual environment

   python -m venv .venv

   On Linux/macOS:

   source .venv/bin/activate

   On Windows PowerShell:

   .\.venv\Scripts\Activate.ps1

3. Install dependencies

   python -m pip install -r requirements.txt

If you don't have a `requirements.txt`, install the packages used by the script:

   python -m pip install requests beautifulsoup4 pandas lxml


## Usage

Run the scraper from the repository directory:

   python healthconnect_doc_scraper.py

By default the script prints progress information and creates the following files in the repository root (names depend on configuration):

- `<CSV_NAME>` (default: `anesthesiologist.csv`)
- `<IMAGE_FOLDER>/` (folder with downloaded images)
- `<IMAGE_FOLDER>.zip` (zip archive with images)


## Configuration

The main configuration constants are defined near the top of `healthconnect_doc_scraper.py`:

- `BASE_URL` — base site URL used to resolve relative links
- `PAGE_URL` — target listing page to scrape
- `CSV_NAME` — output CSV filename
- `IMAGE_FOLDER` — local directory for downloaded images
- `MAX_WORKERS` — number of concurrent profile workers
- `TIMEOUT`, `RETRY` — network settings

Update these values when you want to change category, output filenames, or concurrency.


## About images not showing in README

If the original README referenced images that are not visible on GitHub, it is usually because the image files are not present in the repository or the image path is incorrect. To add images that render correctly in this README:

1. Add the image files into the repository, for example `docs/` or `assets/` (create the folder if it doesn't exist).
2. Reference them with a relative path in Markdown, for example:

   ![Screenshot of output](docs/screenshot.png)

3. Commit and push the images to the same branch where README.md lives. GitHub will render them once present.

If you want, I can add an `assets/` or `docs/` folder and upload images you provide, or remove broken image links from the README — tell me which you prefer.


## Important safety note

The repository previously contained a cleanup snippet that deletes a local directory named `diabetologist` without confirmation. Review the script for any unconditional deletions before running it. Do not change such values to point at directories that contain important data.


## Responsible use

- Check robots.txt and the target site's terms of service before scraping.
- Use a conservative request rate, exponential backoff, and retries.
- Do not attempt to access private or protected data.
- Treat phone numbers, biographies, images and other personal data with care and follow applicable law.


## Troubleshooting

- ModuleNotFoundError: Activate your virtualenv and reinstall dependencies.

- Zero results: The site's HTML may have changed. Inspect the target page for class names or structure used by the scraper (for example `li.doctor`).

- Network errors / rate limiting: slow down requests and add retries / backoff.


## Contributing

Contributions are welcome. If you submit pull requests that modify the scraping behavior, include tests (where practical) and justify selectors or parsing logic that are fragile.


## License

No license is declared in this repository. Add a LICENSE file if you want to grant reuse rights.


---

If you'd like, I can also:

- Restore or add images into a `docs/` or `assets/` folder and update the README to reference them, or
- Keep the README image-free and add badges / examples of output CSV rows.

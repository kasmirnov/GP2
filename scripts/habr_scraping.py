from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import datetime as dt
import logging.config
import logging.handlers
import json
from pathlib import Path

logger = logging.getLogger("my_app")

BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = BASE_DIR / "configs" / "config.json"
OUTPUT_PATH = BASE_DIR / "data" / "raw" / "habr.jsonl"
FIRST_PAGE_URL = "https://career.habr.com/vacancies?page=1&type=all"


def setup_logging():
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
    if not config.get("enabled", True):
        logging.disable(logging.CRITICAL)
        return
    logging.config.dictConfig(config)


def parse_each_vacancy_from_list(vacancies_urls, page, driver):
    for url in vacancies_urls:
        driver.execute_script(f"window.open('{url}');")
        driver.switch_to.window(driver.window_handles[-1])

        header_html = driver.find_element(By.CSS_SELECTOR, ".basic-section").get_attribute("outerHTML")
        description_html = driver.find_element(By.CSS_SELECTOR,
                                               ".basic-section--appearance-vacancy-description").get_attribute(
            "outerHTML")
        company_html = driver.find_element(By.CSS_SELECTOR,
                                           ".section.company_info.section--rounded").get_attribute("outerHTML")

        record = {
            "page": page,
            "url": url,
            "title": driver.title,
            "timestamp": dt.datetime.fromtimestamp(
                time.time(), tz=dt.timezone.utc
            ).isoformat(),
            "blocks": {
                "header_html": header_html,
                "description_html": description_html,
                "company_html": company_html
            }

        }
        with open(OUTPUT_PATH, "a", encoding="utf-8") as f:
            json_line = json.dumps(record, ensure_ascii=False)
            f.write(json_line + '\n')

        driver.close()
        driver.switch_to.window(driver.window_handles[0])


def make_driver():
    logger.info("making driver...")
    opts = Options()
    opts.page_load_strategy = "eager"
    opts.add_argument("--window-size=1920,1200")
    opts.add_argument("--headless=new")
    driver = webdriver.Chrome(options=opts)
    return driver


def try_click_next(driver, wait):
    logger.info("starting try_click_next func")
    NEXT_LOC = (By.CSS_SELECTOR, "div.with-pagination__side-button a[rel='next']")
    for attempt in range(1, 4):
        try:
            wait.until(EC.element_to_be_clickable(NEXT_LOC))
            buttons = driver.find_elements(*NEXT_LOC)
            if not buttons:
                logger.info(f"button was not found, attempt: {attempt}")
                return False
            button = buttons[0]
            old_url = driver.current_url
            button.click()
            wait.until(EC.url_changes(old_url))
            return True
        except:
            time.sleep(1)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    driver.save_screenshot("page.png")
    logger.info(f"screenshot saved, button isn't avaible for click")
    return False


def main():
    setup_logging()
    logger.info("script starting...")
    driver = make_driver()
    logger.info("driver created successfully, opening url")
    driver.get(FIRST_PAGE_URL)

    page = 1

    while True:
        vacancies_urls = []
        wait = WebDriverWait(driver, 10)
        logger.info("waiting until presense of all vacancy links")
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".vacancy-card__title-link")))
        elements_vacancies = driver.find_elements(By.CSS_SELECTOR, ".vacancy-card__title-link")
        logger.info(f"successfully found {len(elements_vacancies)} vacancy links")
        for vacancy in elements_vacancies:
            vacancies_urls.append(vacancy.get_attribute("href"))

        parse_each_vacancy_from_list(vacancies_urls, page, driver)

        ok = try_click_next(driver, wait)
        if not ok:
            break
        page += 1
        logging.info(f"successfully moved to the next page number: {page}")

    logging.info("all vacancies have been parsed, ending parser")
    driver.quit()


if __name__ == "__main__":
    main()

from selectolax.parser import HTMLParser
import json
from pathlib import Path
import pandas as pd
import logging.config
import logging.handlers

logger = logging.getLogger("my_app")

BASE_DIR = Path(__file__).resolve().parents[1]
READ_PATH = BASE_DIR / "data" / "raw" / "habr.jsonl"
OUTPUT_PATH = BASE_DIR / "data" / "clean" / "habr_clean.jsonl"
READ_CLEAN_PATH = BASE_DIR / "data" / "clean" / "habr_clean.jsonl"
OUTPUT_CSV_PATH = BASE_DIR / "data" / "clean" / "habr.csv"
CONFIG_PATH = BASE_DIR / "configs" / "config.json"


def setup_logging():
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
    if not config.get("enabled", True):
        logging.disable(logging.CRITICAL)
        return
    logging.config.dictConfig(config)


def get_salary(tree):
    salary = tree.css_first(".basic-salary.basic-salary--appearance-vacancy-header")
    if salary:
        salary = salary.text()
    return salary


def get_skills_and_levels(tree):
    req_block = None

    for sec in tree.css("div.content-section"):
        title_node = sec.css_first("h2.content-section__title")
        if title_node and title_node.text(strip=True) == "Требования":
            req_block = sec
            break

    skills = []
    levels = []
    raw = None

    if req_block:
        raw = req_block.css_first(".inline-list")

    for a in raw.css("a"):
        href = a.attributes.get('href', '')
        text = a.text(strip=True)
        if 'skills' in href:
            skills.append(text)
        else:
            levels.append(text)

    return skills, levels


def get_geo_and_working_requirements(tree):
    geo_block = None

    for sec in tree.css("div.content-section"):
        title_node = sec.css_first("h2.content-section__title")
        if title_node and title_node.text(strip=True) == "Местоположение и тип занятости":
            geo_block = sec
            break

    geo = set()
    raw_geo = None

    if geo_block:
        raw_geo = geo_block.css_first(".inline-list")

    for a in raw_geo.css("a"):
        geo.add(a.text())
    geo = list(geo)

    working_requirements = [x.strip() for x in raw_geo.text().split("•") if x.strip()]

    if geo:
        working_requirements = working_requirements[1:]

    return geo, working_requirements


def get_company_name(record):
    company_html = HTMLParser(record["blocks"]["company_html"])
    company_name = company_html.css_first(".company_name")
    if company_name:
        company_name = company_name.text()

    return company_name


def get_title(tree):
    title = tree.css_first("h1").text()
    return title


def make_csv():
    df = pd.read_json(READ_CLEAN_PATH, lines=True)
    df.to_csv(OUTPUT_CSV_PATH, index=False)


def main():
    setup_logging()
    logger.info("starting habr_make_csv")

    vacancy_n = 0
    is_successfull = True
    with open(READ_PATH, "r", encoding="utf-8") as f:
        for line in f:
            vacancy_n += 1
            logger.info(f"parsing vacancy number: {vacancy_n}")

            try:
                record = json.loads(line)
                header_html = record["blocks"]["header_html"]
                tree = HTMLParser(header_html)

                title = get_title(tree)

                salary = get_salary(tree)

                skills, levels = get_skills_and_levels(tree)

                geo, working_requirements = get_geo_and_working_requirements(tree)

                company_name = get_company_name(record)

            except Exception as e:
                logger.exception(f"exception: {e}")
                logger.info("ending program with error")
                is_successfull = False
                break

            vacancy_dict = {
                "vacancy_name": title,
                "company_name": company_name,
                "salary": salary,
                "levels": levels,
                "skills": skills,
                "geo": geo,
                "working_requirements": working_requirements,
            }

            with open(OUTPUT_PATH, "a", encoding="utf-8") as file:
                json_line = json.dumps(vacancy_dict, ensure_ascii=False)
                file.write(json_line + '\n')

            logger.info(f"successfully parsed and wrote into file vacancy number: {vacancy_n}")

        logger.info("starting formatting file into .csv")
        make_csv()
        logger.info(f"successfully formatted file into .csv, path:{OUTPUT_CSV_PATH}. ending program")


if __name__ == "__main__":
    main()

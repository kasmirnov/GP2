from datetime import datetime, timedelta
import requests
from dateutil import parser
import json
import time
import logging.config
import logging.handlers
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = BASE_DIR / "configs" / "config.json"
OUTPUT_PATH = BASE_DIR / "data" / "raw" / "hh.jsonl"
API_URL = "https://api.hh.ru/vacancies"
DATE_UPPER_BOUND = None

PROFESSIONAL_ROLES_IDS = [156, 160, 10, 150, 25, 165, 34, 36, 73, 155, 96, 164, 104, 157, 107, 112, 113, 148, 114, 116,
                          124, 125, 126]

ITEM_FIELDS = ['id', 'premium', 'name', 'department', 'has_test', 'response_letter_required', 'area', 'salary',
               'salary_range', 'type', 'address', 'response_url', 'sort_point_distance', 'published_at', 'created_at',
               'archived', 'apply_alternate_url', 'show_logo_in_search', 'show_contacts', 'insider_interview', 'url',
               'alternate_url', 'relations', 'employer', 'snippet', 'contacts', 'schedule', 'working_days',
               'working_time_intervals', 'working_time_modes', 'accept_temporary', 'fly_in_fly_out_duration',
               'work_format', 'working_hours', 'work_schedule_by_days', 'night_shifts', 'professional_roles',
               'accept_incomplete_resumes', 'experience', 'employment', 'employment_form', 'internship',
               'adv_response_url', 'is_adv_vacancy', 'adv_context']

logger = logging.getLogger("my_app")


def setup_logging():
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
    if not config.get("enabled", True):
        logging.disable(logging.CRITICAL)
        return
    logging.config.dictConfig(config)


def fetch_block(date_to: datetime | None):
    params = {
        "professional_role": PROFESSIONAL_ROLES_IDS,
        "host": "hh.ru",
        "order_by": "publication_time",
        "date_from": "2020-11-10T16:10:15+0300",
        "per_page": 100,
    }

    if date_to is not None:
        params["date_to"] = date_to

    min_published = None

    for page in range(20):
        time.sleep(0.8)
        logger.debug(f"parsing page number {page}")
        params["page"] = page
        r = requests.get(API_URL, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        items = data.get("items", [])

        if not items:
            logger.info("no items were found")
            return date_to, True

        for item in items:
            try:
                line = {}
                for name in ITEM_FIELDS:
                    if name in item.keys():
                        line[name] = item[name]
            except Exception as e:
                logger.exception(f"error: {e}")
                break

            with open(OUTPUT_PATH, "a", encoding="utf-8") as f:
                json.dump(line, f, ensure_ascii=False)
                f.write("\n")

            published_at = None
            try:
                published_at = parser.isoparse(line["published_at"])
                if (min_published is None) or (published_at < min_published):
                    min_published = published_at
            except Exception as e:
                logger.exception(f"error: {e}, published_at= {published_at}")

    return min_published, False


def crawl():
    date_to = DATE_UPPER_BOUND
    total_requests = 0
    logger.info(f"date_to: {date_to}, total requests: {total_requests}")

    while True:
        min_published, is_end = fetch_block(date_to)
        total_requests += 20
        logger.info(f"current first published date: {min_published}, total requests: {total_requests}")

        if is_end:
            logger.info("ending program")
            break

        try:
            epsilon = timedelta(seconds=1)
            logger.debug(f"date_to: {date_to}, min_published: {min_published}")
            date_to = min_published - epsilon
            if date_to < parser.isoparse("2024-11-10T14:33:42+0300"):
                break
            date_to = date_to.strftime("%Y-%m-%dT%H:%M:%S%z")

        except Exception as e:
            logger.exception(f"error: {e}")


def main():
    setup_logging()
    logger.info("starting program...")
    crawl()


if __name__ == "__main__":
    main()

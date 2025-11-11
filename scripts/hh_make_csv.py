import json
import pandas as pd
import logging.config
import logging.handlers
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = BASE_DIR / "configs" / "config.json"
INPUT_PATH = BASE_DIR / "data" / "raw" / "hh.jsonl"
OUTPUT_PATH = BASE_DIR / "data" / "clean" / "hh.csv"

logger = logging.getLogger("my_app")


def setup_logging():
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
    if not config.get("enabled", True):
        logging.disable(logging.CRITICAL)
        return
    logging.config.dictConfig(config)


def main():
    logger.info("starting program")
    all_data = []
    with open(INPUT_PATH, "r", encoding="utf-8", errors="strict") as f:
        for line in f:
            logger.info("got line, starting to collect items")
            item = json.loads(line)

            # main fields
            vacancy_id = item.get("id")
            name = item.get("name")
            employer = item.get("employer", {}).get("name", "")
            published_at = item.get("published_at")
            url_link = item.get("alternate_url")

            # требования и обязанности
            snippet = item.get("snippet", {})
            requirement = snippet.get("requirement", "") or ""
            responsibility = snippet.get("responsibility", "") or ""
            description = (requirement + " " + responsibility).strip()

            # зп
            salary_info = item.get("salary")
            salary_from = None
            salary_to = None
            currency = None

            if salary_info:
                salary_from = salary_info.get("from")
                salary_to = salary_info.get("to")
                currency = salary_info.get("currency")

            # employment
            employment_info = item.get("employment")
            if employment_info:
                employment = employment_info.get("name")

            # city
            if "name" in item.get("area").keys():
                city = item["area"]["name"]

            # experience
            experience_code = None
            experience_name = None
            experience = item.get("experience")
            if experience:
                experience_code = experience.get("id")
                experience_name = experience.get("name")

            # wotking_hours
            working_hours_code = None
            working_hours_name = None
            working_hours = item.get("working_hours")
            if working_hours:
                working_hours = working_hours[0]
                working_hours_code = working_hours.get("id")
                working_hours_name = working_hours.get("name")

            # work_format
            work_format_id = None
            work_format_name = None
            work_format = item.get("work_format")
            if work_format:
                work_format = work_format[0]
                work_format_id = work_format.get("id")
                work_format_name = work_format.get("name")

            # schedule
            schedule_code = None
            schedule_name = None
            schedule = item.get("schedule")
            if schedule:
                schedule_code = schedule.get("id")
                schedule_name = schedule.get("name")

            # address
            address_city = None
            address_lat = None
            address_lng = None
            address = item.get("address")
            if address:
                address_city = address.get("city")
                address_lat = address.get("lat")
                address_lng = address.get("lng")

            # night_shifts
            night_shifts = item.get("night_shifts")

            # internship
            internship = item.get("internship")

            line_dict = {
                "id": vacancy_id,
                "title": name,
                "description": description,
                "salary_from": salary_from,
                "salary_to": salary_to,
                "currency": currency,
                "employer": employer,
                "city": city,
                "night_shifts": night_shifts,
                "internship": internship,
                "address_city": address_city,
                "address_lat": address_lat,
                "address_lng": address_lng,
                "schedule_id": schedule_code,
                "schedule_name": schedule_name,
                "work_format_id": work_format_id,
                "work_format_name": work_format_name,
                "working_hours_code": working_hours_code,
                "working_hours_name": working_hours_name,
                "experience_code": experience_code,
                "experience_name": experience_name,
                "employment": employment,
                "published_at": published_at,
                "url": url_link
            }

            all_data.append(line_dict)

    df = pd.DataFrame(all_data)
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    main()

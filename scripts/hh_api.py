from datetime import datetime, timedelta, timezone
import requests
from dateutil import parser
import json
import time

url = "https://api.hh.ru/vacancies"

HEADERS = {
    "User-Agent": "YourApp/1.0 (dev@example.com)",
    "HH-User-Agent": "YourApp/1.0 (dev@example.com)",
    "Authorization": "Bearer <OAUTH_TOKEN>",
}

professional_roles_ids = [156, 160, 10, 150, 25, 165, 34, 36, 73, 155, 96, 164, 104, 157, 107, 112, 113, 148, 114, 116,
                          124, 125, 126]

item_fields = ['id', 'premium', 'name', 'department', 'has_test', 'response_letter_required', 'area', 'salary',
               'salary_range', 'type', 'address', 'response_url', 'sort_point_distance', 'published_at', 'created_at',
               'archived', 'apply_alternate_url', 'show_logo_in_search', 'show_contacts', 'insider_interview', 'url',
               'alternate_url', 'relations', 'employer', 'snippet', 'contacts', 'schedule', 'working_days',
               'working_time_intervals', 'working_time_modes', 'accept_temporary', 'fly_in_fly_out_duration',
               'work_format', 'working_hours', 'work_schedule_by_days', 'night_shifts', 'professional_roles',
               'accept_incomplete_resumes', 'experience', 'employment', 'employment_form', 'internship',
               'adv_response_url', 'is_adv_vacancy', 'adv_context']


def fetch_block(date_to: datetime | None):
    params = {
        "professional_role": professional_roles_ids,
        "host": "hh.ru",
        "order_by": "publication_time",
        "date_from": "2020-11-10T16:10:15+0300",
        "per_page": 100,
    }
    if date_to is not None:
        params["date_to"] = date_to
        print(date_to)

    min_published = None

    for page in range(20):
        time.sleep(0.8)
        # print("парсится страница")
        params["page"] = page
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        items = data.get("items", [])

        if not items:
            print("no items")
            return date_to, True

        for item in items:
            # print("парсятся айтемы")
            line = {}
            for name in item_fields:
                if name in item.keys():
                    line[name] = item[name]

            # print("открывается файл")
            with open("../data/raw/hh.jsonl", "a", encoding="utf-8") as f:
                json.dump(line, f, ensure_ascii=False)
                f.write("\n")
                # print("записано в файл")

            published_at = parser.isoparse(line["published_at"])
            if (min_published is None) or (published_at < min_published):
                min_published = published_at
                # print("время обновилось")
    print(min_published)
    return min_published, False


def crawl():
    date_to = None
    total_requests = 0
    while True:
        print("запуск crawl")
        min_published, is_end = fetch_block(date_to)
        total_requests += 20
        if is_end:
            print("конец")
            break
        epsilon = timedelta(seconds=1)
        date_to = min_published - epsilon
        if date_to < parser.isoparse("2024-11-10T14:33:42+0300"):
            break
        date_to = date_to.strftime("%Y-%m-%dT%H:%M:%S%z")

        print(date_to)
        print(total_requests)


crawl()

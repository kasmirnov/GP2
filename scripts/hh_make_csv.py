import json
import pandas as pd

k=0
all_data = []
with open("../data/raw/hh.jsonl", "r", encoding="utf-8", errors="strict") as f:
    for line in f:
        item = json.loads(line)

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
        avg_salary = None

        if salary_info:
            salary_from = salary_info.get("from")
            salary_to = salary_info.get("to")
            currency = salary_info.get("currency")

        employment_info = item.get("employment")
        employment = employment_info.get("name") if employment_info else None

        work_format_info = item.get("work_format", [])
        remote_type = "Очная"



        if work_format_info:
            work_format_id = work_format_info[0].get("id", "")
            if work_format_id == "REMOTE":
                remote_type = "Удалённая"
            elif work_format_id == "HYBRID":
                remote_type = "Гибрид"
            elif work_format_id == "ON_SITE":
                remote_type = "Очная"
        else:

            employment_name = (item.get("employment") or {}).get("name", "")
            schedule_name = (item.get("schedule") or {}).get("name", "")

            if employment_name == "Удалённая работа":
                remote_type = "Удалённая"
            elif schedule_name == "Гибрид":
                remote_type = "Гибрид"
            elif description:
                desc_lower = description.lower()
                if any(w in desc_lower for w in ["гибрид", "гибридный", "офис и удалён"]):
                    remote_type = "Гибрид"
                elif any(w in desc_lower for w in ["удалён", "remote"]):
                    remote_type = "Удалённая"

        if "name" in item.get("area").keys():
            city = item["area"]["name"]

        experience_code = None
        experience_name = None
        experience = item.get("experience")
        if experience:
            experience_code = experience.get("id")
            experience_name = experience.get("name")

        working_hours = None
        working_hours_code = None
        working_hours_name = None
        working_hours = item.get("working_hours")
        if working_hours:
            working_hours = working_hours[0]
            working_hours_code = working_hours.get("id")
            working_hours_name = working_hours.get("name")

        work_format = None
        work_format_id = None
        work_format_name = None
        work_format = item.get("work_format")
        if work_format:
            work_format = work_format[0]
            work_format_id = work_format.get("id")
            work_format_name = work_format.get("name")

        schedule_code = None
        schedule_name = None
        schedule = item.get("schedule")
        if schedule:
            schedule_code = schedule.get("id")
            schedule_name = schedule.get("name")

        address_city = None
        address_lat = None
        address_lng = None
        address = item.get("address")
        if address:
            address_city = address.get("city")
            address_lat = address.get("lat")
            address_lng = address.get("lng")


        night_shifts = item.get("night_shifts")

        internship = item.get("internship")


        dd = {
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
                        "remote": remote_type,
                        "published_at": published_at,
                        "url": url_link
                    }

        all_data.append(dd)
        # print(dd.keys())
        # print()
        # print(dd)
        # print(line)
        # k+=1
        # if k==2:
        #     break
        # # if avg_salary:
        # #     print(dd)
        # #     break
df = pd.DataFrame(all_data)
df.to_csv("hh.csv", index=False, encoding="utf-8-sig")

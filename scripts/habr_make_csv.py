from selectolax.parser import HTMLParser
import json


with open("vacancies1.ndjson") as f:
    for line in f:
        record = json.loads(line)

        header_html = record["blocks"]["header_html"]
        tree = HTMLParser(header_html)

        title = tree.css_first("h1").text()

        salary = tree.css_first(".basic-salary.basic-salary--appearance-vacancy-header")
        if salary:
            salary = salary.text()

        req_block = None

        for sec in tree.css("div.content-section"):
            title_node = sec.css_first("h2.content-section__title")
            if title_node and title_node.text(strip=True) == "Требования":
                req_block = sec
                break

        skills = []
        levels=[]

        if req_block:
            raw = req_block.css_first(".inline-list")

        for a in raw.css("a"):
            href = a.attributes.get('href', '')
            text = a.text(strip=True)
            if 'skills' in href:
                skills.append(text)
            else:
                levels.append(text)

        # if req_block:
        #     raw = req_block.css_first(".inline-list").text(separator=" ", strip=True)
        #     requirements = [s.strip() for s in raw.split("•")]
        #
        # if ',' in requirements[0]:
        #     levels = [s.strip() for s in requirements[0].split(',')]
        #     skills = requirements[1:]
        # else:
        #     skills = requirements

        geo_block = None

        for sec in tree.css("div.content-section"):
            title_node = sec.css_first("h2.content-section__title")
            if title_node and title_node.text(strip=True) == "Местоположение и тип занятости":
                geo_block = sec
                break

        geo = set()

        if geo_block:
            raw_geo = geo_block.css_first(".inline-list")

        for a in raw_geo.css("a"):
            geo.add(a.text())
        geo = list(geo)

        working_requirements = [x.strip() for x in raw_geo.text().split("•") if x.strip()]

        if geo:
            working_requirements = working_requirements[1:]


        company_html = HTMLParser(record["blocks"]["company_html"])
        company_name = company_html.css_first(".company_name")
        if company_name:
            company_name = company_name.text()

        dict = {
            "vacancy_name": title,
            "company_name": company_name,
            "salary": salary,
            "levels": levels,
            "skills": skills,
            "geo": geo,
            "working_requirements": working_requirements,
        }

        with open("parsed.ndjson", "a") as file:
            json_line = json.dumps(dict, ensure_ascii=False)
            file.write(json_line + '\n')

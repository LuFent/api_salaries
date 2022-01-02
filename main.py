import requests
import os

from dotenv import load_dotenv
from terminaltables import DoubleTable


def predict_rub_salary(sal_from, sal_to):
    if not sal_from and not sal_to:
        return None

    if not sal_from:
        return sal_to*0.8

    elif not sal_to:
        return sal_from*1.2

    else:
        return (sal_from + sal_to)/2


def get_hh_job_page_salary(area_id, period, language, page_number):
    url = "https://api.hh.ru/vacancies"
    response = requests.get(url, params={"area": area_id,
                                         "period": period,
                                         "text": language,
                                         "page": page_number})

    response.raise_for_status()
    response = response.json()
    pages_amount = response["pages"]
    vacs_count = response["found"]
    response = response["items"]
    vacs_processed = 0
    summary = 0

    for vac in response:
        raw_salary = vac["salary"]
        if raw_salary and raw_salary["currency"] == "RUR":
            salary = predict_rub_salary(raw_salary["from"], raw_salary["to"])
            if salary:
                summary += int(salary)
                vacs_processed += 1

    return vacs_count, vacs_processed, summary, pages_amount


def get_hh_language_salary(language, area_id, period):
    params = {"area": area_id,
              "period": period,
              "text": language,
              "page": -1}

    language_salary = {"vacancies_found": 0,
                       "vacancies_processed": 0,
                       "average_salary": 0}
    while True:

        params["page"] += 1
        vacancies_found, vac_processed, summary, pages_amount = \
            get_hh_job_page_salary(*params.values())
        language_salary["vacancies_found"] = vacancies_found
        language_salary["vacancies_processed"] += vac_processed
        language_salary["average_salary"] += summary

        if pages_amount - 1 == params["page"]:
            if language_salary["vacancies_processed"] != 0:
                language_salary["average_salary"] /= \
                    language_salary["vacancies_processed"]

                language_salary["average_salary"] =\
                    int(language_salary["average_salary"])
                return language_salary
            else:
                language_salary["vacancies_found"] = 0
                language_salary["vacancies_processed"] = 0
                language_salary["average_salary"] = 0
                return language_salary


def get_sj_page_salary(language, town, period,
                       vacs_per_page, page_number, headers):
    url = "https://api.superjob.ru/2.0/vacancies/"
    response = requests.get(url, headers=headers,
                            params={"keyword": f"Програмист {language}",
                                               "town": town,
                                               "period": period,
                                               "count": vacs_per_page,
                                               "page": page_number})
    response.raise_for_status()
    response = response.json()
    vacs_count = response["total"]
    vacs_processed = 0
    summary = 0

    for job in response["objects"]:
        salary = predict_rub_salary(job['payment_from'], job['payment_to'])
        if salary:
            summary += int(salary)
            vacs_processed += 1

    return vacs_count, vacs_processed, summary, response["more"]


def get_sj_language_salary(language, api_key, town, period, vacs_per_page):

    params = {"keyword": f"Програмист {language}", "town": town,
              "period": period, "count": vacs_per_page, "page": 0}

    headers = {"X-Api-App-Id": api_key}

    language_salary = {"vacancies_found": 0,
                       "vacancies_processed": 0,
                       "average_salary": 0}

    while True:
        vacs_count, vacs_processed, summary, has_next_page = \
            get_sj_page_salary(*params.values(), headers)
        language_salary["vacancies_found"] = vacs_count
        language_salary["vacancies_processed"] += vacs_processed
        language_salary["average_salary"] += summary
        params["page"] += 1

        if not has_next_page:
            break

    if language_salary["vacancies_processed"] != 0:
        language_salary["average_salary"] /= language_salary["vacancies_processed"]
        language_salary["average_salary"] = int(language_salary["average_salary"])
        return language_salary
    else:
        language_salary["vacancies_found"] = 0
        language_salary["vacancies_processed"] = 0
        language_salary["average_salary"] = 0
        return language_salary


def draw_table(table_filling, title):
    table_lines = [["Язык програмирования", "Вакансий найдено",
                    "Вакансий обработано", "Средняя з.п."]]

    for lang, lang_lines in table_filling.items():
        table_line = [lang]
        table_line.extend(lang_lines.values())
        table_lines.append(table_line)

    table = DoubleTable(table_lines, title=title)
    return table.table


def main():
    load_dotenv()
    super_job_api_token = os.getenv("SUPER_JOB_KEY")
    languages = ["JavaScript", "Java", "Python",
                 "Ruby", "PHP", "C++", "CSS", "C#", "C", "Go"]
    hh_languages_salary = dict()
    sj_languages_salary = dict()

    city = "Moscow"
    period = 30
    area_id = 1

    for lang in languages:
        hh_languages_salary[lang] = get_hh_language_salary(lang,
                                                           area_id, period)
        sj_languages_salary[lang] = get_sj_language_salary(lang, super_job_api_token,
                                                           city, period, 100)

    print(draw_table(hh_languages_salary, "HeadHunter Moscow"))
    print()
    print()
    print(draw_table(sj_languages_salary, "SuperJob Moscow"))


if __name__ == "__main__":
    main()

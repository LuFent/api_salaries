import requests
import os

from dotenv import load_dotenv
from terminaltables import DoubleTable
from tqdm import tqdm


def predict_rub_salary(sal_from, sal_to):
    if not sal_from and not sal_to:
        return None

    if not sal_from:
        return sal_to*0.8

    elif not sal_to:
        return sal_from*1.2

    else:
        return (sal_from + sal_to)/2


def get_hh_job_page_data(area_id, period, language, page_number):
    params = {"area": area_id,
              "period": period,
              "text": language,
              "page": page_number}
    url = "https://api.hh.ru/vacancies"
    response = requests.get(url, params=params)
    response.raise_for_status()
    response = response.json()
    vacs_count = response["found"]
    response = response["items"]
    vacs_processed = 0
    summary = 0

    for vac in response:
        salary_dict = vac["salary"]
        if salary_dict and salary_dict["currency"] == "RUR":
            salary = predict_rub_salary(salary_dict["from"], salary_dict["to"])
            if salary:
                summary += int(salary)
                vacs_processed += 1

    return vacs_count, vacs_processed, summary


def get_hh_language_data(language, area_id, period):
    params = {"area": area_id,
              "period": period,
              "text": language,
              "page": -1}

    language_data = {"vacancies_found": 0,
                     "vacancies_processed": 0,
                     "average_salary": 0}
    while True:
        try:
            params["page"] += 1
            vacancies_found, vac_processed, summary = get_hh_job_page_data(*params.values())
            language_data["vacancies_found"] = vacancies_found
            language_data["vacancies_processed"] += vac_processed
            language_data["average_salary"] += summary
        except Exception:
            language_data["average_salary"] = int(language_data["average_salary"]/language_data["vacancies_processed"])
            return language_data


def get_sj_page_data(language, town, period, vacs_per_page, page_number, headers):
    params = {"keyword": f"Програмист {language}",
              "town": town,
              "period": period,
              "count": vacs_per_page,
              "page": page_number}

    url = "https://api.superjob.ru/2.0/vacancies/"
    response = requests.get(url, params=params, headers=headers)
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


def get_sj_language_data(language, api_key, town, period, vacs_per_page):

    params = {"keyword": f"Програмист {language}", "town": town, "period": period, "count": vacs_per_page, "page": 0}
    headers = {"X-Api-App-Id": api_key}

    language_data = {"vacancies_found": 0,
                     "vacancies_processed": 0,
                     "average_salary": 0}

    while True:
        vacs_count, vacs_processed, summary, if_next = get_sj_page_data(*params.values(), headers)
        language_data["vacancies_found"] = vacs_count
        language_data["vacancies_processed"] += vacs_processed
        language_data["average_salary"] += summary
        params["page"] += 1

        if not if_next:
            break

    language_data["average_salary"] = int(language_data["average_salary"] / language_data["vacancies_processed"])
    return language_data


def draw_table(lang_dict, title):
    table_lines = [["Язык програмирования", "Вакансий найдено", "Вакансий обработано", "Средняя з.п."]]
    for lang, data in lang_dict.items():
        table_line = list()
        table_line.append(lang)
        for cell in data.values():
            table_line.append(cell)
        table_lines.append(table_line)

    table = DoubleTable(table_lines, title=title)
    print(table.table)
    print()


def main():
    load_dotenv()
    super_job_api_token = os.getenv("SUPER_JOB_KEY")
    languages = ["JavaScript", "Java", "Python", "Ruby", "PHP", "C++", "CSS", "C#", "C", "Go"]
    hh_languages_data = dict()
    sj_languages_data = dict()

    city = "Moscow"
    period = 30
    area_id = 1

    with tqdm(total=len(languages)) as pbar:
        for lang in languages:
            pbar.set_description(f"processing {lang} vacancies")
            hh_languages_data[lang] = get_hh_language_data(lang, area_id, period)
            sj_languages_data[lang] = get_sj_language_data(lang, super_job_api_token, city, period, 100)
            pbar.update(1)

    draw_table(hh_languages_data, "HeadHunter Moscow")
    draw_table(sj_languages_data, "SuperJob Moscow")


if __name__ == "__main__":
    main()

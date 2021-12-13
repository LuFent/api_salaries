import requests
import sys
import os
from dotenv import load_dotenv


def predict_rub_hh_salary(salary):
    if salary["currency"] == "RUR":
        if salary["from"] and salary["to"]:
            return (salary["from"] + salary["to"])/2
        elif not salary["from"]:
            return salary["to"]*0.8
        elif not salary["to"]:
            return salary["from"] * 1.2
    else:
        return 0


def predict_rub_sj_salary(sal_from, sal_to):
    if not sal_from and not sal_to:
        return None

    if not sal_from:
        return sal_to*0.8

    elif not sal_to:
        return sal_from*1.2

    else:
        return (sal_from + sal_to)/2


def get_hh_job_page_data(params):
    url = "https://api.hh.ru/vacancies"
    response = requests.get(url, params=params).json()["items"]
    vacs_count = 0
    vacs_processed = 0
    summary = 0

    for i in response:
        salary_dict = i["salary"]
        if salary_dict:
            salary = int(predict_rub_hh_salary(salary_dict))
            vacs_count += 1
            if salary:
                summary += salary
                vacs_processed += 1

    yield vacs_count
    yield vacs_processed
    yield summary


def get_hh_language_data(language):
    params = {"area": "1",
              "period": "30",
              "text": language,
              "page": -1}
    language_dict = {"vacancies_found": 0,
                     "vacancies_processed": 0,
                     "average_salary": 0}
    while True:
        try:
            params["page"] += 1
            vacancies_found, vac_processed, summary = get_hh_job_page_data(params)
            language_dict["vacancies_found"] += vacancies_found
            language_dict["vacancies_processed"] += vac_processed
            language_dict["average_salary"] += summary
        except Exception:
            language_dict["average_salary"] = int(language_dict["average_salary"]/language_dict["vacancies_processed"])
            return language_dict


def get_sj_page_data(params, headers):
    url = "https://api.superjob.ru/2.0/vacancies/"
    response = requests.get(url, params=params, headers=headers)
    response = response.json()
    vacs_count = 0
    vacs_processed = 0
    summary = 0

    for job in response["objects"]:
        vacs_count += 1
        try:
            summary += predict_rub_sj_salary(job['payment_from'], job['payment_to'])
            vacs_processed += 1
        except Exception:
            pass

    yield vacs_count
    yield vacs_processed
    yield summary
    yield response["more"]


def get_sj_language_data(language, api_key):

    params = {"keyword": f"Програмист {language}", "town": "Moscow", "period": 30, "count": 100, "page": 0}
    headers = {"X-Api-App-Id": api_key}

    language_dict = {"vacancies_found": 0,
                     "vacancies_processed": 0,
                     "average_salary": 0}

    while True:
        vacs_count, vacs_processed, summary, if_next = get_sj_page_data(params, headers)
        language_dict["vacancies_found"] += vacs_count
        language_dict["vacancies_processed"] += vacs_processed
        language_dict["average_salary"] += summary
        params["page"] += 1

        if not if_next:
            break

    language_dict["average_salary"] = int(language_dict["average_salary"] / language_dict["vacancies_processed"])
    return language_dict


def draw_table(lang_dict, service, city):
    seporator = "+-----------------------+------------------+---------------------+------------------+"
    print(f"{service}   {city}")
    print(seporator)
    print("| Язык программирования | Найдено вакансий | Обработано вакансий | Средняя зарплата |")
    print(seporator)
    for lang, data in lang_dict.items():
        print(f"| {lang}", end="")
        print(" "*(22 - len(lang)), end="|")
        print(f"{data['vacancies_found']}", end="")
        print(" " * (18 - len(str(data['vacancies_found']))), end="|")
        print(f"{data['vacancies_processed']}", end="")
        print(" " * (21 - len(str(data['vacancies_processed']))), end="|")
        print(f"{data['average_salary']}", end="")
        print(" " * (18 - len(str(data['average_salary']))), end="|")
        print()
        print(seporator)


def main():
    load_dotenv()
    super_job_api_token = os.getenv("SUPER_JOB_KEY")
    languages = ["JavaScript", "Java", "Python", "Ruby", "PHP", "C++", "CSS", "C#", "C", "Go"]
    hh_languages_dict = dict()
    sj_languages_dict = dict()

    for lang in languages:
        hh_languages_dict[lang] = get_hh_language_data(lang)
        sj_languages_dict[lang] = get_sj_language_data(lang, super_job_api_token)
        sj_languages_dict[lang] = get_sj_language_data(lang, super_job_api_token)

    draw_table(hh_languages_dict, "HeadHunter", "Moscow")
    print()
    draw_table(sj_languages_dict, "SuperJob", "Moscow")


if __name__ == "__main__":
    main()

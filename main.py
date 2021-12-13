import requests
import sys
from pprint import pprint

def predict_rub_salary(salary):
    if salary["currency"] == "RUR":
        if salary["from"] and salary["to"]:
            return  (salary["from"] + salary["to"])/2
        elif not salary["from"]:
            return salary["to"]*0.8
        elif not salary["to"]:
            return salary["from"] * 1.2
    else:
        return 0


def get_hh_job_page_data(params):
    url = "https://api.hh.ru/vacancies"
    response = requests.get(url, params=params).json()["items"]
    vacs_count = 0
    vacs_processed = 0
    summary = 0

    for i in response:
        salary_dict = i["salary"]
        if salary_dict:
            salary = int(predict_rub_salary(salary_dict))
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
                     "vacancies_processed" :0,
                     "average_salary": 0}
    while True:
        try:
            params["page"] += 1
            vacancies_found, vac_processed, summary = get_hh_job_page_data(params)
            language_dict["vacancies_found"] += vacancies_found
            language_dict["vacancies_processed"] += vac_processed
            language_dict["average_salary"] += summary
           # pprint(language_dict)
        except Exception as e:
            print(str(e))
            language_dict["average_salary"] = int(language_dict["average_salary"]/language_dict["vacancies_processed"])
            return language_dict


def draw_table(dict, service, city):
    seporator = "+-----------------------+------------------+---------------------+------------------+"
    print(f"{service}   {city}")
    print(seporator)
    print("| Язык программирования | Найдено вакансий | Обработано вакансий | Средняя зарплата |")
    print(seporator)
    for lang, data in dict.items():
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
    d = {'JavaScript': {'vacancies_found': 970, 'vacancies_processed': 838, 'average_salary': 182139}, 'Java': {'vacancies_found': 583, 'vacancies_processed': 525, 'average_salary': 225567}, 'Python': {'vacancies_found': 674, 'vacancies_processed': 598, 'average_salary': 198884}, 'Ruby': {'vacancies_found': 118, 'vacancies_processed': 97, 'average_salary': 197888}, 'PHP': {'vacancies_found': 940, 'vacancies_processed': 877, 'average_salary': 170551}, 'C++': {'vacancies_found': 594, 'vacancies_processed': 537, 'average_salary': 177757}}
    draw_table(d, "HeadHunter", "Moscow")

    sys.exit()
    languages = ["JavaScript", "Java", "Python", "Ruby", "PHP", "C++"]
    hh_languages_dict = dict()

    for lang in languages:
        language_dict = get_hh_language_data(lang)
        print(language_dict)
        hh_languages_dict[lang] = language_dict

    print(hh_languages_dict)


if __name__ == "__main__":
    main()


import requests
import json
from bs4 import BeautifulSoup
from fake_headers import Headers

HOST = "https://spb.hh.ru/search/vacancy?text=python&area=1&area=2"
# Ключевые слова для поиска по описанию вакансии
KEY_WORDS = ['Django', 'Flask']


def get_headers():
    return Headers(browser="firefox", os="win").generate()


def get_text(url):
    return requests.get(url, headers=get_headers()).text


def save_text(text_data, file_name):
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(text_data)


def parse_vacancy_text(vacancy_text):
    vacancy_title = vacancy_text.find('a', class_='serp-item__title')
    vacancy_href = vacancy_title['href']
    vacancy_title_text = vacancy_title.text
    vacancy_salary_text = vacancy_text.find('span', class_='bloko-header-section-3')

    if vacancy_salary_text:  # В некоторых вакансиях уровень заработной платы не указан
        vacancy_salary = vacancy_salary_text.text
        vacancy_salary = vacancy_salary.replace(u"\u202F", "")  # delete NARROW NO-BREAK SPACE
    else:
        vacancy_salary = ''
    vacancy_company_text = vacancy_text.find('div', class_="vacancy-serp-item-company")

    vacancy_company_blocks = vacancy_company_text.find_all('div', class_="bloko-text")
    vacancy_company_title = vacancy_company_blocks[0].text
    vacancy_company_town = vacancy_company_blocks[1].text.split(',')[0]

    vacancy_responsibility = vacancy_text.find_all(attrs={'data-qa': "vacancy-serp__vacancy_snippet_responsibility"})
    vacancy_requirement = vacancy_text.find_all(attrs={'data-qa': "vacancy-serp__vacancy_snippet_requirement"})

    vacancy_description = [vacancy_responsibility[0].text, vacancy_requirement[0].text]

    # print(vacancy_title_text, vacancy_href)
    # print(vacancy_company_title, vacancy_company_town, vacancy_salary)
    # print(vacancy_description[0])
    # print(vacancy_description[1])

    return {'vacancy': vacancy_title_text,
            'href': vacancy_href,
            'salary': vacancy_salary,
            'company': vacancy_company_title,
            'town': vacancy_company_town,
            'description': vacancy_description}


def sort_vacancies(vacancies, key_words):
    sorted_vacancies_list = []
    for v in vacancies:
        approach_vacancie = False
        for word in key_words:
            if word in v['description'][0] or word in v['description'][1]:
                approach_vacancie = True
                break
        if approach_vacancie:
            v.pop('vacancy')        # Для задания название вакансии не требуется
            v.pop('description')    # Удаляем описание вакансии - в задании оно не требуется
            sorted_vacancies_list.append(v)
    return sorted_vacancies_list


def parse_page(page):
    soup = BeautifulSoup(page, features='lxml')
    vacancies = soup.find_all('div', class_='serp-item')
    page_vacancies = []
    for vacancy in vacancies:
        page_vacancies.append(parse_vacancy_text(vacancy))
    return page_vacancies


if __name__ == "__main__":
    page_text = get_text(HOST)
    # save_text(page_text, 'site.html')
    parsed_vacancies = parse_page(page_text)
    print(f"Получено вакансий: {len(parsed_vacancies)}")
    sorted_vacancies = sort_vacancies(parsed_vacancies, KEY_WORDS)
    print(f"Выбрано вакансий: {len(sorted_vacancies)}")
    with open("python-vacancies.json", "w", encoding='utf-8') as file:
        json.dump(sorted_vacancies, file, ensure_ascii=False, indent=4)
    print('Отобранные вакансии записаны в файл.')

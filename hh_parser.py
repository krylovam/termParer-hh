# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import time
import urllib.request, urllib.error, urllib.parse
import json
import re
def get_data_from_links(links):
    data = []
    for i in range(len(links)):
        print(i, links[i])
        try:
            response = urllib.request.urlopen(links[i])
            webContent = response.read()
            search = BeautifulSoup(webContent, 'lxml')
            title = search.find('h1', attrs={'data-qa':"vacancy-title"})
            salary = search.find('p', attrs={'class':"vacancy-salary"})
            company = search.find('a', attrs={'data-qa':"vacancy-company-name"})
            location = search.find('p', attrs={'data-qa':"vacancy-view-location"})
            work_experience = search.find('span', attrs={'data-qa':'vacancy-experience'})
            employment_mode = search.find('p', attrs={'data-qa':"vacancy-view-employment-mode"})
            description = search.find('div', attrs={'data-qa':"vacancy-description"})
            skills = search.find_all('span', attrs={'data-qa':"bloko-tag__text"})
            creation_time = search.find('p', attrs={'class':'vacancy-creation-time'})
            is_hendicapped = search.find('span', attrs={'class':'vacancy-icon vacancy-icon_accept-handicapped'})
            job_description = {}
            if title:
                job_description['title'] = title.get_text()
            else:
                continue
            if salary:
                job_description['salary'] = salary.get_text()
            else:
                job_description['salary'] =None
            if company:
                job_description['company'] = company['href']
            else:
                job_description['company'] =None
            if location:
                job_description['location'] = location.get_text()
            else:
                job_description['location'] = None
            if work_experience:
                job_description['work_experience'] = work_experience.get_text()
            else:
                job_description['work_experience'] = None
            if employment_mode:
                job_description['employment_mode'] = employment_mode.get_text()
            else:
                job_description['employment_mode'] = None
            if is_hendicapped:
                job_description['hendicapped'] = 1
            else:
                job_description['hendicapped'] = 0
            if description:
                job_description['description'] = description.get_text()
            else:
                job_description['description'] = None
            if skills:
                job_description['skills'] = []
                for skill in skills:
                    job_description['skills'].append(skill.get_text())
            else:
                job_description['skills'] = None
            if creation_time:
                job_description['creation_time'] = creation_time.get_text()
            data.append(job_description)
        except:
            print("Cannot open this link")
        if ((i % 100) == 0) and (i > 0):
            write_data_to_file_(data, 'vacancy_info.txt')
    write_data_to_file_(data, 'vacancy_info.txt')
    return data

def write_data_to_file(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        for job in data:
            f.write(json.dumps(job, ensure_ascii=False) + "\n")

def write_links_to_file(data):
    with open('hh-vacancies-links.txt', 'w', encoding='utf-8') as f:
        for item in data:
            f.write(item + "\n")

def read_from_file(files):
    data = []
    for file in files:
        with open(file, 'r') as f:
            text = f.read().split('\n')

        for i in text:
            data.append(i)
        print(len(data))
    return data

def get_links_by_area(areaId):
    hrefs = set()
    url = 'https://hh.ru/search/vacancy?area=' + str(areaId)
    response = urllib.request.urlopen(url)
    webContent = response.read()
    search = BeautifulSoup(webContent, 'lxml')
    numberOfVacancies = search.find('h1', {'class': 'bloko-header-1'})
    try:
        num = int(numberOfVacancies.get_text().split()[1])
        pages = int(num / 50)
        if num % 50 != 0:
            pages += 1
    except:
        print("Cannot convert to int")
    for i in range(pages):
        url_page = url + '&page=' + str(i)
        try:
            response = urllib.request.urlopen(url_page)
        except:
            continue
        webContent = response.read()
        search = BeautifulSoup(webContent, 'lxml')
        vacancy_titles = search.find_all('a', {'data-qa': "vacancy-serp__vacancy-title"})
        for vacancy in vacancy_titles:
            hrefs.add(vacancy['href'])
    return hrefs

def get_company_links_from_json():
    data = set()
    with open('vacancy_info.txt', 'r', encoding='utf-8') as json_file:
        json_file.seek(0)
        text = json_file.read()
        print(len(text.split('\n')))
        for i in text.split('\n'):
            json_string = json.loads(i)
            if (json_string['company']):
                data.add(json_string['company'])
    return data

def get_set_of_links_from_files(files):
    data = set()
    for file in files:
        with open(file, 'r') as f:
            text = f.read().split('\n')

        for i in text:
            data.add(i)
        print(len(data))
    return data
            
def get_links_by_employers(links):
    data = []
    for k in range(len(links)):
        id = links[k].split('/')[2]
        id = id.split('?')[0]
        href = 'https://hh.ru/search/vacancy?employer_id=' + id
        print(k, href)
        try:
            response = urllib.request.urlopen(href)
        except:
            continue
        webContent = response.read()
        search = BeautifulSoup(webContent, 'lxml')
        numberOfVacancies = search.find('h1', {'class':'bloko-header-1'})
        try:
            num = int(numberOfVacancies.get_text().split()[1])
            pages = int(num / 50)
            if num % 50 != 0:
                pages += 1
        except:
            print("Cannot convert to int")
        if pages == 0:
            continue
        for i in range(pages):
            url = href + '&page=' + str(i)
            try:
                response = urllib.request.urlopen(url)
            except:
                continue
            webContent = response.read()
            search = BeautifulSoup(webContent, 'lxml')
            vacancy_titles = search.find_all('a', {'data-qa': "vacancy-serp__vacancy-title"})
            for vacancy in vacancy_titles:
                data.append(vacancy['href'])
        if k%50 == 0:
            write_links_to_file(data)
    return data

def read_links_from_file(files):
    num = 0
    for file in files:
        with open(file, 'r') as f:
            text = f.read().split('\n')

        for i in text:
            num += 1
        print(num)
    return data
if __name__ == '__main__':
    links = get_links_by_area(1)
    write_links_to_file(links)
    get_data_from_links(links)
    company_links = get_company_links_from_json()
    links_global = get_links_by_employers(company_links)
    get_data_from_links(links_global)
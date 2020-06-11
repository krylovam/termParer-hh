# -*- coding: utf8 -*-
from bs4 import BeautifulSoup
import urllib.request, urllib.error, urllib.parse
import json
import re
import codecs
import collections
import csv
import datetime
import numpy as np
import pandas as pd
from sklearn import preprocessing
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon
from designsQt import (firstMenu, secondMenu)
import sys
def parser(link):
    try:
        response = urllib.request.urlopen(link)
    except:
        print("Cannot open this link")
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
        print('Cannot read this vacancy')
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
    return job_description


months = {'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4, 'мая': 5, 'июня': 6,
              'июля': 7, 'августа': 7, 'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12}
def minSalary(salaryString):
    salaryString = salaryString.replace(u'\xa0', u'')
    words = salaryString.split()
    try:
        numSalary = int(words[1])
        return numSalary
    except:
        return 0

def toLowerCase(text):
    try:
        x = float(text)
        return ""
    except:
        return text.lower()

def search(i, text):
    return (re.search(i, text) != None)
def search_skills(i, skills):
    for idx in skills:
        if idx == i:
            return True
    return False

def getDate(text):
    item = text.split(" ")
    date_strind = item[2:item.index("в")]
    if len(date_strind) == 1:
        date_string = date_strind[0].replace(u'\xa0', u' ')
        words = date_string.split(" ")
    else:
        words = date_strind
    d = datetime.date(int(words[2]), int(months[words[1]]), int(words[0]))
    return d

def preprocessing(data):
    skills = ""
    if data['skills'] != None:
        for i in data['skills']:
            skills += i
            skills += '\n'
    data['skills'] = skills
    columns = ["title", "salary", "company", "location", "work_experience", "employment_mode",
               "hendicapped", "description", "skills", "creation_time"]
    employment_modes=['вахтовый метод','волонтерство','гибкий график','полная занятость','полный день',
                      'проектная/временная работа','сменный график','стажировка','удаленная работа','частичная занятость']
    experience_mode=['не требуется', '1–3 года', '3–6 лет', 'более 6 лет']
    skills=['пользователь пк','работа в команде','грамотная речь','активные продажи',
     'умение работать в команде','ведение переговоров','обучение и развитие','английский язык',
     'навыки продаж','организаторские навыки','поиск и привлечение клиентов','клиентоориентированность',
     'деловое общение','холодные продажи','прямые продажи','управление персоналом',
     'sql', 'ориентация на результат','autocad','телефонные переговоры','деловая переписка',
     'развитие продаж','работа с большим объемом информации','консультирование','заключение договоров',
     'обучение персонала','управление продажами','ms powerpoint','проведение презентаций',
     'управление проектами','деловая коммуникация','b2b продажи','ms outlook','грамотность',
     '1с: предприятие 8','строительство','контроль качества','водительское удостоверение категории b',
     'документальное сопровождение','работа с кассой', 'linux','python','складской учет',
     'английский\\xa0— a1 — начальный','java','умение работать в коллективе','git','ms excel',
     'складская логистика','ms sql','подбор персонала','javascript','управление производством',
     'планирование продаж','проектная документация','мерчандайзинг','охрана труда и техника безопасности',
     '1с: документооборот','розничная торговля', '1с: склад','техническое обслуживание','документооборот',
     'crm','кассовые операции','английский\\xa0— b2 — средне-продвинутый','навыки презентации',
     'руководство коллективом','работа с людьми','навыки переговоров','знание устройства автомобиля',
     'управление командой','ответственность','навыки межличностного общения','работа с базами данных',
     'английский\\xa0— b1 — средний','медицинская документация','управленческая отчетность','управление производственным персоналом',
     'поиск информации в интернет','мобильность','ремонтные работы','postgresql','adobe photoshop',
     'контроль сроков годности','консультативные продажи','аналитическое мышление','работа с возражениями',
     'холодные звонки','бизнес-анализ','кассовые документы','1с: торговля','мотивация персонала',
     'работа с дебиторской задолженностью','ms visio','английский\\xa0— c1 — продвинутый','многозадачность',
     'водительское удостоверение категории bc','ведение отчетности','разработка проектной документации','инвентаризация']
    cities=['Москве','Санкт-Петербурге','Екатеринбурге','Казани','Нижнем Новгороде',
            'Краснодаре','Ростове-на-Дону','Новосибирске','Воронеже','Самаре']
    columns_for_drop = ['title', 'company', 'salary', 'employment_mode', 'description',
                        'skills', 'creation_time','city', 'work_experience', "location"]


    new_df = pd.DataFrame(columns=columns)
    new_df.loc[0] = data
    new_df["is_salary_given"] = (new_df['salary'] != "з/п не указана")
    new_df["min_salary"] = new_df["salary"].apply(minSalary)

    for i in employment_modes:
        new_df["employment_mode"] = new_df['employment_mode'].apply(toLowerCase)
        new_df["emplyment_mode (" + i + ")"] = new_df.apply(lambda x: search(i, x['employment_mode']), axis=1)
    for i in experience_mode:
        new_df["work_experince(" + i + ")"] = new_df.apply(lambda x: x["work_experience"] == i, axis=1)
    new_df["description_length"] = new_df.apply(lambda x: len(x["description"]), axis=1)
    for i in skills:
        new_df["skills"] = new_df['skills'].apply(toLowerCase)
        new_df[i] =new_df.apply(lambda x: search(i, x['skills']), axis =1)
    new_df["city"] = new_df.apply(lambda x: " ".join(x["creation_time"].split(" ")[len(x["creation_time"].split(" ")) - x["creation_time"].split(" ")[::-1].index("в"):]), axis=1)
    for i in cities:
        new_df[i] = new_df.apply(lambda x: x["city"] == i, axis=1)
    new_df["date"] = new_df["creation_time"].apply(getDate)
    new_df = new_df.drop(labels=columns_for_drop, axis=1)
    features = list(new_df.columns)
    rest = [2, -1]
    for i in rest:
        features.pop(i)
    enc = LabelEncoder()

    for f in features:
        new_df[f + "_num"] = enc.fit_transform(new_df[f])
        new_df.drop(f, axis=1, inplace=True)
    base = datetime.date(int('2020'), int(months['июня']), int('4'))
    new_df["date_diff"] = new_df.apply(lambda x: (x["date"] - base).days, axis=1)
    new_df = new_df.drop("date", axis=1)
    df_tmp = new_df["min_salary"]
    new_df.drop(["min_salary"], axis=1, inplace=True)
    new_df['min_salary'] = df_tmp

    return new_df

def import_csv():
    df = pd.read_csv("wow1.csv")
    return df
def train_model():
    data_train = import_csv()
    trainData = data_train.drop('min_salary', axis=1)
    trainDependentVariables = data_train['min_salary']
    randomForest = RandomForestRegressor(random_state=0)
    randomForest.fit(trainData, trainDependentVariables)
    return randomForest
def predict(new_df, randomForest):
    testData = new_df.drop('min_salary', axis=1)
    predictedDependentVariables = randomForest.predict(testData)
    return predictedDependentVariables

class FirstMenu(QMainWindow, firstMenu.Ui_MainWindow):
    def __init__(self, randomForest):
        super().__init__()
        self.setupUi(self)
        self.randomForest = randomForest
        self.pushButton.clicked.connect(self.btnOnClick)
        self.show()

    @pyqtSlot()
    def btnOnClick(self):
        self.hide()
        link = self.lineEdit.text()
        print(link)
        data = parser(link)
        print(data)
        new_df = preprocessing(data)
        salary = predict(new_df, self.randomForest)
        self.secondMenu = SecondMenu(salary)
        self.secondMenu.show()

class SecondMenu(QMainWindow, secondMenu.Ui_MainWindow):
    def __init__(self, salary):
        super().__init__()
        self.setupUi(self)
        self.label_salary.setText(str(int(salary[0])))
        self.backButton.clicked.connect(self.backBtnOnClick)
        self.show()

    @pyqtSlot()
    def backBtnOnClick(self):
        self.hide()
        self.firstMenu = FirstMenu()
        self.firstMenu.show()

def main():
    randomForest = train_model()
    app = QApplication(sys.argv)
    window = FirstMenu(randomForest)
    app.exec_()

if __name__ == '__main__':
    main()

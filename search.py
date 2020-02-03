# !/usr/bin/env python
# coding: utf-8

import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import re

# initializing lists with information about job
jobs_content = []  # list with page content about job
jobs_names = []  # list with names of the jobs
jobs_links = []  # list with links to the job page
all_jobs_links = []  # list of all jobs links

# job we want to take
job = 'Веб-разработчик'

# going through all pages at hh.ru site and collecting links that
# refer to job variable and also get content from them
for page_number in range(2):
    # creating link for our job and current page
    jobs_page = 'https://spb.hh.ru/search/vacancy?area=2&st=searchVacancy&text=' + job.lower() + '&page=' + str(
        page_number)

    # getting current hh.ru page with our job
    page = requests.get(jobs_page, headers={'User-Agent': 'Custom'})

    # clearing jobs links list
    jobs_links.clear()

    # cheking if page is ready to
    # bring us some data, else getting error code
    if page.status_code == 200:
        # parsing page using Beautiful soup
        soup = BeautifulSoup(page.text, 'html.parser')

        # forming vacancies list from link that
        # refer to partucular vacancy
        vacancies_list = soup.find_all('a', {'class': 'bloko-link HH-LinkModifier'})

        # cheking if vacancies list is not empty
        # and if so, getting vacancy name
        # and vacancy link, then retrieve data from vacancy page
        if len(vacancies_list) > 0:
            # collecting links and names of vacancies
            for vacancy in vacancies_list:
                jobs_names.append(vacancy.text)
                if vacancy['href']:
                    jobs_links.append(vacancy['href'])
                    all_jobs_links.append(vacancy['href'])
                else:
                    print('No job link')
                    jobs_links.append(None)

            # getting page content for each vacancy
            for link in jobs_links:
                # getting vacancy page
                job_page = requests.get(link, headers={'User-Agent': 'Custom'})

                # checking if page is ready to
                # bring us some data, else getting error code
                if job_page.status_code == 200:
                    # parsing vacancy page using Beautiful Soup
                    job_soup = BeautifulSoup(job_page.text, 'html.parser')

                    # getting vacancy page content
                    page_content = job_soup.find('div', {'class': 'g-user-content'})

                    # forming jobs content list
                    jobs_content.append(page_content)
                else:
                    print("Something wrong with the page: ", job_page.status_code)
        else:
            print('No items in vacancies_list')
    else:
        print('Something wrong with page: ', page.status_code)

# initializing list with all data about vacancies
data_list = []

# going through jobs contents and splitting it
# by <strong>. So we get all important headings
# and will be able to get requesments, conditions
# and responsibilities
for job_content in jobs_content:
    data_list.append(re.split('<strong>', str(job_content).lower()))

# initializing lists with information about vacancy
jobs_treb = []  # list of vacancy requerments
jobs_usl = []  # list of vancy conditions
jobs_obyaz = []  # list of vacancy responsibilities
jobs_desc = []  # list of vacancy desctiption

# going through splitted data and getting
# requerments, conditions, responsibilities
# and descriptions
for job in data_list:
    # getting descriptiong because
    # it is always first in the split
    jobs_desc.append(job[0])

    # initializing flags witch note if there is
    # one of requesments, conditions and responsibilities
    # in the split
    treb_flag = False
    obyaz_flag = False
    usl_flag = False

    # checking if there is one of three conditions
    # in our split and if so, adding this conditions
    # to corresponding lists
    for job_content in job:
        if job_content.startswith('требования'):
            jobs_treb.append(job_content)
            treb_flag = True

        if job_content.startswith('обязанности'):
            jobs_obyaz.append(job_content)
            obyaz_flag = True

        if job_content.startswith('условия'):
            jobs_usl.append(job_content)
            usl_flag = True

    # if we haven't found any conditions
    # we add None item to corresponding list
    if treb_flag == False:
        jobs_treb.append(None)

    if obyaz_flag == False:
        jobs_obyaz.append(None)

    if usl_flag == False:
        jobs_usl.append(None)

# initializing lists with clean data about requerments, conditions
# and responsibilities
new_jobs_treb = []  # list of vacancy requerments
new_jobs_obyaz = []  # list of vacancy responsibilities
new_jobs_usl = []  # list of vacancy conditions


# Cleaning informations funcition
# Arguments:
#  Data we want to clean and list where we want
# .  to put this data
# . (data, data_list)
#  Returns:
# .  None
def clear_data(data, data_list):
    # going through the data and firstly cleaning
    # out of three possible conditions, then split
    # out data by html tags to form list or conditions
    # and cleanign data out of usless symbols
    for elem in data:
        if elem != None:
            # cleaning of three conditions
            item = re.sub('требования', '', elem)
            item2 = re.sub('к кандидату', '', item)
            item3 = re.sub('к кандидатам', '', item2)
            item4 = re.sub('условия', '', item3)
            item5 = re.sub('обязанности', '', item4)

            # splitting by html tags
            splited_items = re.split(r'<.*?>', item5)

            # initializing list with clean items
            cleared_items = []

            # going through splitted items, cleaning
            # them and adding to cleared items list
            for item in splited_items:
                cleared_items.append(re.sub(r'[^\w\d\s]+', '', re.sub(r'\s+', ' ', re.sub(r'<.*?>', '', item))))

            # deleating all empty items
            while ("" in cleared_items):
                cleared_items.remove("")

            # deleating all space items
            while (" " in cleared_items):
                cleared_items.remove(" ")

            # adding cleaned items to data_list
            data_list.append(cleared_items)
        else:
            # if no element in data, adding None
            data_list.append(None)


# claning information
clear_data(jobs_obyaz, new_jobs_obyaz)
clear_data(jobs_usl, new_jobs_usl)
clear_data(jobs_treb, new_jobs_treb)

# initializing list for cleaned
# description data
new_jobs_desc = []

# going through all descriptions
# and cleaning it
for desc in jobs_desc:
    # if something in descriotion, cleaning
    # it, overwise, adding None
    if desc != None:
        item = re.sub(r'[^\w\d\s]+', '', re.sub(r'\s+', ' ', re.sub(r'<.*?>', '', desc)))
        new_jobs_desc.append(item)
    else:
        new_jobs_desc.append(None)

# forming DataFrame from retrieved data
web_data = pd.DataFrame({'description': new_jobs_desc, 'requerments': new_jobs_treb, 'conditions': new_jobs_usl,
                         'responsibilities': new_jobs_obyaz, 'links': all_jobs_links})

# initializing lists of courses information
courses_links = []  # list of courses links
courses_skills = []  # list of courses skills
page_links = []  # links to cources on current page

# going through all pages of current job we want to take
# and getting information about skilles we want to aquire
for page in range(1, 13):
    # forming link to courcera pages with job courses we want
    courses_link = 'https://www.coursera.org/search?query=web%20development&indices%5Bprod_all_products_term_optimization%5D%5Bpage%5D=' + str(
        page) + '&indices%5Bprod_all_products_term_optimization%5D%5Bconfigure%5D%5BclickAnalytics%5D=true&indices%5Bprod_all_products_term_optimization%5D%5Bconfigure%5D%5BruleContexts%5D%5B0%5D=ru&indices%5Bprod_all_products_term_optimization%5D%5Bconfigure%5D%5BhitsPerPage%5D=10&configure%5BclickAnalytics%5D=true'

    # getting current page
    page = requests.get(courses_link, headers={'User-Agent': 'Custom'})

    # cheking if page is ready to
    # bring us some data, else getting error code
    if page.status_code == 200:
        # parsing page using Beautiful Soup
        soup = BeautifulSoup(page.text, 'html.parser')

        # getting all courses links at current page
        courses_list = soup.find_all('a', {'data-click-key': 'search.search.click.search_card'})

        # checking if there are courses link on
        # the page and if so, adding links to links list
        # getting course page and retrieving skilles
        if len(courses_list) > 0:
            # clearing page links list
            page_links.clear()

            # going through courses and forming links
            for course in courses_list:
                # adding links to links list
                courses_links.append('https://www.coursera.org' + course['href'])
                page_links.append('https://www.coursera.org' + course['href'])

            # going through links and getting pages and skilles
            for link in page_links:
                # getting course page
                course_page = requests.get(link, headers={'User-Agent': 'Custom'})

                # cheking if page is ready to
                # bring us some data, else getting error code
                if course_page.status_code == 200:
                    # parsing page using Beautiful Soup
                    course_soup = BeautifulSoup(course_page.text, 'html.parser')

                    # getting all acquired skilles from course page
                    acquired_skilles = course_soup.find_all('div', {'class': 'Skills border-a p-x-2 p-t-1 p-b-2 m-y-2'})
                    # adding skilles to skilles list
                    courses_skills.append(acquired_skilles)
                else:
                    print("Something wrong with page: ", course_page.status_code)

        else:
            print('No items in courses_list')
    else:
        print('Something wrong with page: ', page.status_code)

# initializing list of cleaned courses skilles
new_courses_skilles = []

# going through all courses skills and
# forming list of skills for each course
for course in courses_skills:
    # checking if something in courses list
    # and if so, getting it
    if len(course) > 0:
        # initializing list with skills
        # for current cource
        temp_skilles = []

        # getting all skilles for current course
        # forming temp_skilles list and adding it
        # to new_courses_skilles
        for skill in range(len(course[0].find_all('span', {'class': 'centerContent_dqfu5r'}))):
            temp_skilles.append(course[0].find_all('span', {'class': 'centerContent_dqfu5r'})[skill].text)
        new_courses_skilles.append(temp_skilles)
    else:
        new_courses_skilles.append(None)

# getting data where requerments are not null
web_data_with_full_req = web_data[web_data['requerments'].notnull()]

# setting to display all records in jupyter notebook
# with a scrollbar
pd.set_option('display.max_columns', 150)
pd.set_option('display.width', 1000)
web_data_with_full_req

# forming cources data with skilles and link to cources
cources_data = pd.DataFrame({'skilles': new_courses_skilles, 'links': courses_links})

# getting data where skills are not null
cources_data_without_nones = cources_data[cources_data['skilles'].notnull()]

# initializing list for new requerments
new_requerments = []

# going through old requerments and extracting
# only valuable information
for req in web_data_with_full_req['requerments']:
    # initializing temproary requerments list
    temp_req = []

    # going through single requerment and cleaning it
    for string in req:
        # cleaning requerments
        new_string = re.sub(r'[1-9]+', '', re.sub('ё', '', re.sub(r'\s+', ' ', re.sub(r'[а-я]+', '', string))))
        new_s = re.sub(r'\s+', ' ', new_string)

        # adding single requerment to temproary lsit
        temp_req.append(new_s)

    # adding temproary requerments list to
    # new requerments list
    new_requerments.append(temp_req)

# deleating all space items
for item in new_requerments:
    while (" " in item):
        item.remove(" ")

# initializing requerments list
# where all key words are splitted
update_requerments = []

# going through all requerments and
# splitting them by space
for req in new_requerments:
    # initializing temproary list for single string
    temp = []

    # going through single string and splitting it
    # by space
    for i in req:
        splited_req = i.split()

        # adding splitted requerments to temp list
        temp.append(splited_req)

    # adding splitted items to updated requerments list
    update_requerments.append(temp)

# updating vacancies list with cleaned requerments
web_data_with_full_req['cleaned requerments'] = update_requerments

# showing DataFrames
web_data_with_full_req

cources_data_without_nones




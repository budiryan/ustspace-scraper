# -*- coding: utf-8 -*-
import json
import scrapy
from scrapy import FormRequest
from scrapy_splash import SplashRequest


class UstspaceCrawlerSpider(scrapy.Spider):
    name = 'ustspace-crawler'
    start_urls = ['https://ust.space/login']
    base_url = 'https://ust.space'
    query_param_department = '/selector/query?page=review&type=default&value='
    query_param_course = '/selector/query?page=review&type=subject&value='
    query_param_review = '/get?single=false&composer=false&' \
                         'preferences%5Bsort%5D=0&preferences%5BfilterInstructor%5D=0' \
                         '&preferences%5BfilterSemester%5D=0&preferences%5BfilterRating%5D=0 '
    departments = []

    def parse(self, response):
        return [FormRequest.from_response(response,
                    formdata={'username': 'bryanaa', 'password': 'bud1ry@n'},
                    callback=self.after_login)]

    def after_login(self, response):
        # check login succeed before going on
        if b'authentication failed' in response.body:
            self.logger.error("Login failed")
            return
        yield SplashRequest(url=self.base_url + self.query_param_department, callback=self.parse_departments)

    def parse_departments(self, response):
        '''
        Parse all the given departments to json and put them into a list
        '''
        jsonresponse = json.loads(response.css('html body pre::text').extract_first())
        with open('data/departments.json', 'w') as outfile:
            json.dump(jsonresponse['list'], outfile)
        jsonresponse = jsonresponse['list']
        for j in jsonresponse:
            if j['type'] == 'subject':
                self.departments.append(j['title'])
        for department in self.departments:
            yield SplashRequest(url=self.base_url + self.query_param_course + department,
                                callback=self.parse_courses, meta={'department': department})

    def parse_courses(self, response):
        '''
        Parse all the courses within one department
        '''
        department = response.meta.get('department')
        jsonresponse = json.loads(response.css('html body pre::text').extract_first().split('<!DOCTYPE html>')[0])
        with open('data/courses/' + department + '.json', 'w') as outfile:
            json.dump(jsonresponse['list'], outfile)
        for course in jsonresponse['list']:
            yield SplashRequest(url=self.base_url + '/review/' + course['value'] +
                                    self.query_param_review, callback=self.parse_course_review)

    def parse_course_review(self, response):
        '''
        Parse all the course review within one course
        '''
        jsonresponse =  json.loads(response.css('html body pre::text').extract_first().split('<!DOCTYPE html>')[0])
        yield jsonresponse





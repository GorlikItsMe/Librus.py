#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
import requests
from urllib.error import HTTPError
from json import loads
import re
import sys


class WrongPasswordError(Exception):
    pass


class SessionExpiredError(Exception):
    pass


cached_objects = {}


class Librus:
    """Klasa odpowiadająca za odbieranie danych z librusa"""
    PATTERN_CSRF = re.compile(
        '<meta name=\\"csrf-token\\" content=\\"(\w+)\\">')

    BASE_URL = "https://api.librus.pl/"
    URL_ROOT = BASE_URL + "2.0/Root"
    URL_SCHOOL_INFO = BASE_URL + "2.0/SchoolInfo"
    URL_SCHOOLS = BASE_URL + "2.0/Schools"
    URL_ME = BASE_URL + "2.0/Me"
    URL_SCHOOL_RECEIVE_MESSAGE = BASE_URL + "2.0/SchoolReceiveMessage"
    URL_SYSTEM_DATA = BASE_URL + "2.0/SystemData"
    URL_HOMEWORK = BASE_URL + "2.0/HomeWorks"
    URL_GRADE = BASE_URL + "2.0/Grades"
    URL_CALENDAR = BASE_URL + "2.0/Calendars"
    URL_TIMTABLE = BASE_URL + "2.0/Timetables"
    URL_USERS = BASE_URL + "2.0/Users"
    URL_SUBJECTS = BASE_URL + "2.0/Subjects"
    URL_GRADES_CATEGORIES = BASE_URL + "2.0/Grades/Categories"
    URL_HOMEWORK_CATEGORIES = BASE_URL + "2.0/HomeWorks/Categories"
    URL_LUCKY_NUMBER = BASE_URL + "2.0/LuckyNumbers"
    URL_COLORS = BASE_URL + "2.0/Colors"
    URL_UNITS = BASE_URL + "2.0/Units"
    URL_PARENTS_MEATING = BASE_URL + "2.0/ParentTeacherConferences"
    URL_CALENDAR_SUBSTITIUSIONS = BASE_URL + "2.0/Calendars/Substitutions"
    URL_UNATTENDANCE = BASE_URL + "2.0/Attendances?showPresences=true"
    URL_ANNOUNCEMENT = BASE_URL + "2.0/SchoolNotices"
    URL_ATTENDACE_TYPE = BASE_URL + "2.0/Attendances/Types"
    URL_LESSONS = BASE_URL + '2.0/Lessons'

    def __init__(self, login, password):
        self.__username = login
        self.__password = password
        self.__client = requests.session()
        self.login()

    def login(self):
        # Cookies i takie tam
        res = self.__client.get(
            'https://portal.librus.pl/oauth2/authorize?'
            'client_id=wmSyUMo8llDAs4y9tJVYY92oyZ6h4lAt7KCuy0Gv&'
            'redirect_uri=http://localhost/bar&response_type=code')
        csrf = self.PATTERN_CSRF.findall(res.content.decode('utf-8'))[0]

        # Należy pamiętać, że to Xml-Http-Request i wysyłany jest JSON,
        # zwykły POST nie działa
        self.__client.post('https://portal.librus.pl/rodzina/login/action',
                           json={'email': self.__username,
                                 'password': self.__password},
                           headers={'X-CSRF-TOKEN': csrf})
        try:
            res = self.__client.get(
                'https://portal.librus.pl/oauth2/authorize?'
                'client_id=wmSyUMo8llDAs4y9tJVYY92oyZ6h4lAt7KCuy0Gv&'
                'redirect_uri=http://localhost/bar&response_type=code')
        except requests.exceptions.ConnectionError as inst:
            code = (str(inst.args).split('code='))[1].split(' ')[0]

        if code not in code:
            raise WrongPasswordError
        #code = res.url.split('=')[1] #
        librus_token = self.__client.post('https://portal.librus.pl/oauth2/access_token',
                           data={
                               'grant_type': 'authorization_code',
                               'code': code,
                               'redirect_uri': 'http://localhost/bar',
                               'client_id': 'wmSyUMo8llDAs4y9tJVYY92oyZ6h4lAt7KCuy0Gv',
                           }).json()['access_token']

        self.__client.headers.update({'Authorization': 'Bearer {}'.format(librus_token)})
        user_token = self.__client.get(
            'https://portal.librus.pl/api/SynergiaAccounts').json()[
            'accounts'][0]['accessToken']
        self.__client.headers.update({'Authorization': 'Bearer {}'.format(user_token)})
        

    def get_api_response(self, url):
        return self.__client.get(url).json()

    def get_api_object(self, url):
        if url in cached_objects:
            return cached_objects[url]
        try:
            res = self.get_api_response(url)
            if '/Lessons/' in url or '/Users/' in url \
                    or '/Attendances/Types' in url or '/Subjects/' in url:
                cached_objects[url] = res
            return res
        except HTTPError:
            cached_objects[url] = None
            return None
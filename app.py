#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import librus

app = librus.Librus('EMAIL@POCZTA','HASLO')
#print (app.get_api_response(app.URL_ME))
me = app.get_api_object(app.URL_ME)
luckynumber = app.get_api_object(app.URL_LUCKY_NUMBER)

print('Zalogowano jako: '+me['Me']['User']['FirstName']+' '+me['Me']['User']['LastName'])
print('Szczęśliwy numerek: '+str(luckynumber['LuckyNumber']['LuckyNumber'])+' Na '+luckynumber['LuckyNumber']['LuckyNumberDay'])

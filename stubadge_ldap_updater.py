#!./stubadge_env/bin/python3
### Student Badge LDAP Updater
### Script to update the LDAP info 
### in the MySQL DB for the Student
### Badge system
### Used by students.redclayschools.com
### Requires time, pandas, ldap3, datetime
### os, csv, zipfile, and rcmailsend(self-created package)
### .env needed to set the username/password for AD
### and the MySQL servers

###Import Modules###
import ldap3 as ld
import pandas as pd
import time
import datetime
import os
from dotenv import load_dotenv
from rcmailsend import mail_send #Self Created Module
from rcadinfoexport import ad_connection #Self Created Module
from rcadinfoexport import ad_info_export #Self Created Module
from sqlalchemy import create_engine #Need pymysql and sqlalchemy 
#######

###Variables###
#Load .ENV File
load_dotenv()
#Date
CurrentDate = datetime.date.today()
Date = CurrentDate.strftime('%m-%d-%Y')
startTime = time.ctime()
#Mail_send Vars
logToEmail = 'philip.smallwood@redclay.k12.de.us'
logSubject = 'Student Badge MySQL Updater'
logFile = "/var/log/stubadge/StuBadgeMySQL" +Date +".log"
#AD Variables
DCServer = os.getenv('DCServer')
BindAccount = os.getenv('BindAccount')
BindPass = os.getenv('BindPass')
SearchBase = ('OU=Kindergarten,OU=Students,OU=Users,OU=RCCSD,DC=redclay,DC=k12,DC=de,DC=us',
    'OU=Elementary,OU=Students,OU=Users,OU=RCCSD,DC=redclay,DC=k12,DC=de,DC=us',
    'OU=Middle,OU=Students,OU=Users,OU=RCCSD,DC=redclay,DC=k12,DC=de,DC=us',
    'OU=High,OU=Students,OU=Users,OU=RCCSD,DC=redclay,DC=k12,DC=de,DC=us',
    'OU=Meadowood,OU=Other,OU=Students,OU=Users,OU=RCCSD,DC=redclay,DC=k12,DC=de,DC=us',
    'OU=ZCalendar,OU=Other,OU=Students,OU=Users,OU=RCCSD,DC=redclay,DC=k12,DC=de,DC=us',
    'OU=First State,OU=Other,OU=Students,OU=Users,OU=RCCSD,DC=redclay,DC=k12,DC=de,DC=us',
    'OU=Charter,OU=Other,OU=Students,OU=Users,OU=RCCSD,DC=redclay,DC=k12,DC=de,DC=us')
SearchScope = ld.SUBTREE
Attributes = ['givenname','sn','distinguishedName',
    'department','departmentNumber','description','title',
    'UserPrincipalName','whenChanged','employeeID']
SearchFilter = '(&(objectCategory=person)(objectClass=user)\
    (!(userAccountControl:1.2.840.113556.1.4.803:=2)))' #Enabled Users
#MySQL Variables
mysqlUser = os.getenv('mysqlUser')
mysqlPass = os.getenv('mysqlPass')
mysqlServer = os.getenv('mysqlServer')
mysqlDB = os.getenv('mysqlDB')
mysqlConnectionUrl = 'mysql+pymysql://' + mysqlUser + ':' + mysqlPass + '@' + mysqlServer + '/' + mysqlDB
########


###Log Begin###
f = open(logFile, "a")
f.write("------------------\n")
f.write("----Student Badge MySQL Updater---- " + startTime + "\n")
f.write("---\n")
f.close()
########

###Get Info from AD###
#Connect
DCConnection = ad_connection(DCServer,BindAccount,BindPass)
#Pull AD Data
df_StudentInfo = ad_info_export(DCConnection,SearchBase,Attributes,SearchScope,SearchFilter)
########

###Update MySQL Table###
mysqlEngine = create_engine(mysqlConnectionUrl, echo=True)
mysqlConnection = mysqlEngine.connect()
df_StudentInfo.to_sql('ldapData', con = mysqlEngine, if_exists = 'replace',index=False)
########


###Logging for cleanup and end 
f = open(logFile, "a")
f.write("---\n")
f.write("MySQL Database was Updated \n")
f.write("------------------\n")
f.close()
########

###Email Results###
mail_send(logToEmail,logSubject,logFile)
########
### Student Badge LDAP Updater
### Script to update the LDAP info 
### in the MySQL DB for the Student
### Badge system
### Used by students.redclayschools.com


###Import Modules###
import ldap3 as ld
import pandas as pd
import time
import datetime
import os
from dotenv import load_dotenv
from rcmailsend import mail_send #Self Created Module
from rc_ad_info_export import ad_connection,ad_info_export
from sqlalchemy import create_engine 
#######

###Variables###
#Load .ENV File
load_dotenv()
#Date
current_date = datetime.date.today()
str_date = current_date.strftime('%m-%d-%Y')
start_time = time.ctime()
#Mail_send Vars
log_to_email_1 = os.getenv('log_to_email_1')
log_subject = 'Student Badge MySQL Updater'
log_file = f"/var/log/stubadge/StuBadgeMySQL{str_date}.log"
#AD Variables
dc_server = os.getenv('dc_server')
bind_account = os.getenv('bind_account')
bind_pass = os.getenv('bind_pass')
search_base_list = os.getenv('Search').split('$')
search_base = tuple(search_base_list)
search_scope = ld.SUBTREE
ad_attributes = ['givenname','sn','distinguishedName',
    'department','departmentNumber','description','title',
    'UserPrincipalName','whenChanged','employeeID']
search_filter = '(&(objectCategory=person)(objectClass=user)\
    (!(userAccountControl:1.2.840.113556.1.4.803:=2)))' #Enabled Users
#MySQL Variables
mysql_user = os.getenv('mysql_user')
mysql_pass = os.getenv('mysql_pass')
mysql_server = os.getenv('mysql_server')
mysql_db = os.getenv('mysql_db')
mysql_connection_url = f"mysql+pymysql://{mysql_user}:{mysql_pass}@{mysql_server}/{mysql_db}"
########


###Log Begin###
f = open(log_file, "a")
f.write("------------------\n")
f.write("----Student Badge MySQL Updater---- " + start_time + "\n")
f.write("---\n")
f.close()
########

###Get Info from AD###
#Connect
dc_connection = ad_connection(dc_server,bind_account,bind_pass)
#Pull AD Data
df_student_info = ad_info_export(dc_connection,\
    search_base,\
    ad_attributes,\
    search_scope,\
    search_filter)
########

###Update MySQL Table###
mysqlEngine = create_engine(mysql_connection_url, echo=True)
mysqlConnection = mysqlEngine.connect()
df_student_info.to_sql('ldapData',\
    con = mysqlEngine,\
    if_exists = 'replace',\
    index=False)
########


###Logging for cleanup and end 
f = open(log_file, "a")
f.write("---\n")
f.write("MySQL Database was Updated \n")
f.write("------------------\n")
f.close()
########

###Email Results###
mail_send(log_to_email_1,log_subject,log_file)
########
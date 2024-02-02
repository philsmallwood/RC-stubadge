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
from os import getenv
from dotenv import load_dotenv
from rc_smtp_send import google_smtp_send
from rc_ad_info_export import ad_connection,ad_info_export
from rc_google_py import write_log_to_google
from sqlalchemy import create_engine 
#######

###Variables###
#Load .ENV File
load_dotenv('../env_file/.env')
# Date
current_date = datetime.date.today()
date_str = current_date.strftime('%m-%d-%Y')
start_time = time.ctime()
# Google Info
google_auth_key = getenv('google_auth_key')
network_team_drive_id = getenv('network_team_drive_id')
stubadge_log_folder_id = getenv('stubadge_log_folder_id')
# Log Vars
log_file = str()
log_file_name = 'StubadgeUpdaterLog-'
# Email Alert Vars
alert_to_email = getenv('log_to_email')
alert_subject = "Stubadge Updater - ERROR ALERT"
smtp_pass = getenv('smtp_pass')
# AD Variables
dc_server = getenv('dc_server')
bind_account = getenv('bind_account')
bind_pass = getenv('bind_pass')
search_base_list = getenv('search_base_list').split('$')
search_base = tuple(search_base_list)
search_scope = ld.SUBTREE
ad_attributes = ['givenname','sn','distinguishedName',
    'department','departmentNumber','description','title',
    'UserPrincipalName','whenChanged','employeeID']
search_filter = '(&(objectCategory=person)(objectClass=user)\
    (!(userAccountControl:1.2.840.113556.1.4.803:=2)))' #Enabled Users
# MySQL Variables
mysql_user = getenv('mysql_user')
mysql_pass = getenv('mysql_pass')
mysql_server = getenv('mysql_server')
mysql_db = getenv('mysql_db')
mysql_connection_url = f"mysql+pymysql://{mysql_user}:{mysql_pass}@{mysql_server}/{mysql_db}"
########


###Log Begin###
log_file += "------------------\n"
log_file += f"The Student Badge App Updater Script was started on {start_time} \n"
log_file += "---\n"
###########

###Get Info from AD###
#Connect
try:
    dc_connection = ad_connection(dc_server,bind_account,bind_pass)
    #Pull AD Data
    df_student_info = ad_info_export(dc_connection,\
        search_base,\
        ad_attributes,\
        search_scope,\
        search_filter)
    #Log Info Download
    log_file += "---\n"
    log_file += "Student Info Successfully Downloaded from AD\n"
    log_file += "---\n"
except:
    #Log Error
    log_file += "---\n"
    log_file += "!! Error !! Student Info Downloaded Failed!\n"
    log_file += "---\n"
###########

###Update MySQL Table###
try:
    mysqlEngine = create_engine(mysql_connection_url, echo=True)
    mysqlConnection = mysqlEngine.connect()
    df_student_info.to_sql('ldapData',\
        con = mysqlEngine,\
        if_exists = 'replace',\
        index=False)
    #Log Database Update
    log_file += "---\n"
    log_file += "Student Data Successfully Updated\n"
    log_file += "---\n"
except:
    #Log Error
    log_file += "---\n"
    log_file += "!! Error !! Student Data Update Failed!\n"
    log_file += "---\n"
########


###Write Log to Google###
try: 
    write_log_to_google(google_auth_key, \
        network_team_drive_id, \
        stubadge_log_folder_id, \
        log_file, \
        log_file_name, \
        date_str)
except:
    #Email if Error Logging
    google_smtp_send(alert_to_email, 
                alert_subject, 
                smtp_pass)
########

###Alert if Error###
if "error" in log_file.lower():
    google_smtp_send(alert_to_email, 
                alert_subject, 
                smtp_pass)
########
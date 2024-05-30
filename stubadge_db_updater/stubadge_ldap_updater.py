### Student Badge LDAP Updater
### Script to update the LDAP info 
### in the MySQL DB for the Student
### Badge system
### Used by students.redclayschools.com


###Import Modules###
import pandas as pd
import time
import datetime
from os import getenv
from dotenv import load_dotenv
from app_logger import AppLogger
from rc_smtp_send import google_smtp_send
from rc_google_py import write_log_to_google
from sqlalchemy import create_engine 
#######

###Variables###
#Load .ENV File
load_dotenv('/app_updater/env_file/.env')
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
# MySQL Variables
adinfo_mysql_username = getenv('adinfo_mysql_username')
adinfo_mysql_pass = getenv('adinfo_mysql_pass')
adinfo_mysql_hostname = getenv('adinfo_mysql_hostname')
adinfo_mydb_name = getenv('adinfo_mydb_name')
student_table_name = 'Students'
stubadge_mysql_user = getenv('stubadge_mysql_user')
stubadge_mysql_server = getenv('stubadge_mysql_server')
stubadge_mysql_pass = getenv('stubadge_mysql_pass')
stubadge_mysql_db = getenv('stubadge_mysql_db')
stubadge_student_table_name = 'ldapData'
########


### Start Logger ###
logger = AppLogger('Stubadge Student LDAP Info Updater App', start_time)
###########

### Get Info from AD MySQL DB ###
# Connect to Database
engine = create_engine(
    f'mysql+pymysql://{adinfo_mysql_username}:{adinfo_mysql_pass}@{adinfo_mysql_hostname}/{adinfo_mydb_name}?charset=utf8mb4')
# Read Student Info to DF
try:
    df_student_info = pd.read_sql(student_table_name, con=engine)
    logger.log_success()
except:
    logger.log_error()
# Disconnect from Database
engine.dispose()
###########

### Format DF ###
df_student_info = df_student_info[['givenName','sn','distinguishedName',
                        'department','departmentNumber','description','title',
                        'userPrincipalName','whenChanged','employeeID']].copy()

###Update MySQL Table###
try:
    engine = create_engine(f"mysql+pymysql://{stubadge_mysql_user}:{stubadge_mysql_pass}@{stubadge_mysql_server}/{stubadge_mysql_db}"
, echo=True)
    df_student_info.to_sql(stubadge_student_table_name,
        con = engine,\
        if_exists = 'replace',\
        index=False)
    #Log Database Update
    logger.log_success()
except:
    logger.log_error()
########


###Write Log to Google###
try: 
    log_file = logger.get_log()
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
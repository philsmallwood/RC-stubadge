# RC-Stubadge

### Student Badge MySQL Updater

#### Repo: RC-stubadge
#### Languages: Python

The Student Badge LDAP Updater script is designed to update the LDAP information in the MySQL database for the Student Badge application used by students.redclayschools.com. The script imports necessary modules, sets variables including authentication keys and server information, establishes a connection to the Active Directory (AD) server to retrieve student information, updates the MySQL database with the retrieved information, logs the process, writes the log to a Google Drive folder, and sends an email alert in case of errors.

Main Steps:
1. Import necessary modules and set variables.
2. Establish a connection to the Active Directory (AD) server and retrieve student information.
3. Update the MySQL database with the retrieved student information.
4. Log the process and indicate whether the student data update was successful or if there was an error.
5. Write the log file to a Google Drive folder using the provided authentication key and folder IDs.
6. If there was an error during the process, send an email alert to the specified recipient.

Notes:
+ Scripts need a configured .env file in the same path.  Envsample file available for settings.
+ Updater Job is run under /etc/crontab as root

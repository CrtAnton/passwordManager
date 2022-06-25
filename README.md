# passwordManager
Password amanager with encrypted database. Before using make sure you change code at lines 71, 73, 78 to add your path where you want the encryption key to be saved.
Do not lose the encryption key as all data will inaccesible without it.

How it works:
1) You will set a master password to login into your passwords database
1 behind the scenes) A new database file will be created in the same directory as the py file. Your master password will be hashed(sha256) and saved into a table of the database.

2) You will login using the master password
2 behind the scenes) Your password will be hashed and checked if it matches the hash in the database. Input is validated to avoid SQL injection and there is also a anti-bruteforce attacks mechanism.

3) You are on the main screen, you can do the following: add some new credentials, update credentials, delete credentials, show all database in the main screen, querry the database, go to settings to change the theme of the program.
3 behind the scenes) Add new credentials - your usename and password will be encrypted and saved into the database.
                     Update credentials - program is checking if credentials in database, if yes you can modify them and it will encrypt and save them.
                     Delete credentials - if credentials in the database they will be deleted.
                     Show all - decrypt database and shows it into the mainscreen. Your choice will be saved to a configuration file for next time you start the program.
                     Querry database - you can search a set of credentials by username or by website
                     Setting - you can change theme(light or dark mode). Your choice will be saved to a configuration file for next time you start the program.

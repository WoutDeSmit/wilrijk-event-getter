# wilrijk-event-getter
## setup:
1. download latest chromium driver at https://googlechromelabs.github.io/chrome-for-testing/
2. extract the downloaded zip and put chromedriver.exe in yout C:\Windows folder.
3. install the requirements in requirements.txt
4. download your credentials for Google calendar. If you don't have these, follow the steps described in https://developers.google.com/calendar/api/quickstart/python. You will need to set up a workspace, enable the calendar api and set up OAuth, then you can get your credentials.
5. Make sure to add yourself as a tester. You can do this in your cloud console by going to Solutions - Google Auth Platform - Audience - Test Users - Add Users.
6. put the credentials json in the folder that this project is in and rename it to credentials.json

The setup should now be complete. You can run main.py. On first time use you will be prompted to log in. Be sure to log in with the account you added as a test user.

## adding or removing clubs
You can add or remove clubs by adding or removing their facebook events page in the "targets" list in main.py. Make sure to follow the structure of the given clubs.

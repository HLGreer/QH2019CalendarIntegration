from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '../credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.now().isoformat() + '-05:00' # 'Z' indicates UTC time
    print(now)
    endOfDay = find_end_of_day(now)
    print(time_diffs(now,endOfDay))

    events_result = service.events().list(calendarId='primary', timeMin=now, timeMax=endOfDay,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    print(events)

    if not events:
        print('No upcoming events found.')
    for event in events:
        #print(event)
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])

# Yes this is a little hacky... its a hackathon!
def find_end_of_day(stamp):
    stampList = list(stamp)
    stampList[11:26] = "23:59:59.999999"
    return ''.join(stampList)

def time_diffs(earlier, later):
    time1 = list(earlier)[11:19]
    time1 = ''.join(time1)
    time2 = list(later)[11:19]
    time2 = ''.join(time2)
    time1ob = datetime.datetime.strptime(time1, '%H:%M:%S')
    time2ob = datetime.datetime.strptime(time2, '%H:%M:%S')
    duration = time2ob - time1ob
    duration_in_s = duration.total_seconds()
    minutes = divmod(duration_in_s, 60)[0]
    return minutes

def find_free_time(events):
    pass

if __name__ == '__main__':
    main()
    #print(find_end_of_day(datetime.datetime.now().isoformat() + '-05:00'))


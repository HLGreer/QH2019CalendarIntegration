from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

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

    events_result = service.events().list(calendarId='primary', timeMin=now, timeMax=endOfDay,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    print(find_free_time(events))

    # if not events:
    #     print('No upcoming events found.')
    # for event in events:
    #     #print(event)
    #     start = event['start'].get('dateTime', event['start'].get('date'))
    #     end = event['end'].get('dateTime', event['end'].get('date'))
    #     print(start, end, event['summary'])

# Yes this is a little hacky... its a hackathon!
def find_end_of_day(stamp):
    stampList = list(stamp)
    stampList[11:26] = "23:59:59.999999"
    return ''.join(stampList)

def find_end_of_day_datetime(stamp):
    endDayStamp = find_end_of_day(stamp)
    return datetime.datetime.strptime(''.join(endDayStamp), '%Y-%m-%dT%H:%M:%S')

def time_diffs(earlier, later):
    duration = later - earlier
    duration_in_s = duration.total_seconds()
    minutes = divmod(duration_in_s, 60)[0]
    return minutes

# Create a datetime object from one of the ugly rcf3339 formatted strings
def create_datetime_from_rcf(rcfstr):
    rcflist = list(rcfstr)[0:19]
    #print (datetime.datetime.strptime(''.join(rcflist), '%Y-%m-%dT%H:%M:%S'))
    return datetime.datetime.strptime(''.join(rcflist), '%Y-%m-%dT%H:%M:%S')

def find_free_time(events):
    if not events:
        print('No upcoming events found.')
    countEvents = 0
    gapTimes = [] # a list of lists where each internal list is [gapstarttime, duration] where duration is in minutes
    for i in range(0,len(events)-1):
        event = events[i]
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        laterEvent = events[i+1]
        startofNextEvent = laterEvent['start'].get('dateTime', laterEvent['start'].get('date'))
        firstEndTime = create_datetime_from_rcf(end)
        secondStartTime = create_datetime_from_rcf(startofNextEvent)
        if (firstEndTime < secondStartTime):
            duration = time_diffs(firstEndTime,secondStartTime)
            gapTimes.append([firstEndTime, duration])
        gapEndDay = find_free_time_at_end_of_day(events[len(events)-1],find_end_of_day(datetime.datetime.now().isoformat()))
        if gapEndDay is not None:
            gapTimes.append(gapEndDay)
    return gapTimes

def find_free_time_at_end_of_day(event, endOfDayTime):
    end = event['end'].get('dateTime', event['end'].get('date'))
    lasteventDatetime = create_datetime_from_rcf(end)
    dayEndDatetime = create_datetime_from_rcf(endOfDayTime)
    if lasteventDatetime < dayEndDatetime:
        duration = time_diffs(lasteventDatetime, dayEndDatetime)
        return [lasteventDatetime, duration]
    return None


if __name__ == '__main__':
    main()


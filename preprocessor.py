import pandas as pd
import re

def preprocess(data):
    pattern = r"\d{2}/\d{2}/\d{2}, \d{1,2}:\d{2}(?:\u202f|\s)(?:am|pm)"
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    df = pd.DataFrame(list(zip(messages, dates)), columns=['user_message', 'message_date'])

    df['message_date'] = pd.to_datetime(df['message_date'], format="%d/%m/%y, %I:%M %p", errors='coerce')

    df['user_message'] = df['user_message'].str.replace('\n', ' ', regex=False)

    users = []
    messages = []

    for msg in df['user_message']:
        entry = re.split('([\w\W]+?):\s', msg)
        if entry[1:]:  # has a user
            users.append(entry[1])
            messages.append(" ".join(entry[2:]))
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)
    df["only_date"] = df["message_date"].dt.date
    df['year'] = df['message_date'].dt.year
    df["month_num"] = df["message_date"].dt.month
    df['month'] = df['message_date'].dt.month_name()
    df['day'] = df['message_date'].dt.day
    df['day_name']=df['message_date'].dt.day_name()
    df['hour'] = df['message_date'].dt.hour
    df['minute'] = df['message_date'].dt.minute

    period = []
    for hour in df[["day_name", "hour"]]["hour"]:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str("00") + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df["period"] = period


    return df



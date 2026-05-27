import pandas as pd
import re

def preprocess(data):
    pattern = r"\d{2}/\d{2}/\d{2}, \d{1,2}:\d{2}(?:\u202f|\s)(?:am|pm)"
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    df = pd.DataFrame(list(zip(messages, dates)), columns=['user_message', 'message_date'])
    df['message_date'] = pd.to_datetime(df['message_date'], format="%d/%m/%y, %I:%M %p", errors='coerce')

    users = []
    msgs = []

    for msg in df['user_message']:
        msg_clean = re.sub(r'^\s*-\s*', '', msg).strip()
        entry = re.split(r'([\w\W]+?):\s', msg_clean)
        if entry[1:]:
            users.append(entry[1].strip())
            msgs.append(" ".join(entry[2:]).replace('\n', ' ').strip())
        else:
            users.append('group_notification')
            msgs.append(entry[0].replace('\n', ' ').strip())

    df['user'] = users
    df['message'] = pd.Series(msgs).astype(str)
    df.drop(columns=['user_message'], inplace=True)
    df["only_date"] = df["message_date"].dt.date
    df['year'] = df['message_date'].dt.year
    df["month_num"] = df["message_date"].dt.month
    df['month'] = df['message_date'].dt.month_name()
    df['day'] = df['message_date'].dt.day
    df['day_name'] = df['message_date'].dt.day_name()
    df['hour'] = df['message_date'].dt.hour
    df['minute'] = df['message_date'].dt.minute

    period = []
    for hour in df['hour']:
        if hour == 23:
            period.append(str(hour) + "-00")
        elif hour == 0:
            period.append("00-1")
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df["period"] = period
    return df
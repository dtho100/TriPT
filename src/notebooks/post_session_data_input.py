import pandas as pd
import numpy as np
import argparse
import datetime

user_input = {
    "morning": {
     "questions": [
        {"name": "date", "prompt": "What date are you entering data for (YYYY-MM-DD)? ", "type": "date"},
        {"name": "body_weight", "prompt": "Enter morning BW: ", "type": "float"},
        {"name": "sleep", "prompt": "Enter number of hours slept: ", "type": "float"},
        {"name": "rhr", "prompt": "Enter RHR from last night: ", "type": "float"},
        {"name": "hrv", "prompt": "Enter HRV from last night: ", "type": "float"}
     ]
     },
    "evening": {
     "questions": [
        {"name": "date", "prompt": "What date are you entering data for (YYYY-MM-DD)? ", "type": "date"},
        {"name": "pain_notes", "prompt": "Enter any pains (out of 10) and where they occur: ", "type": "str"},
        {"name": "session_1_notes", "prompt": "Enter any Session 1 notes: ", "type": "str"},
        {"name": "session_2_notes", "prompt": "Enter any Session 2 notes: ", "type": "str"},
        {"name": "general_notes", "prompt": "Enter any other notes: ", "type": "str"}
     ]
    }
}

csv_schema_mapping = {
    "date": "Date",
    "session_1_notes": "Session 1 Personal Notes",
    "session_2_notes": "Session 2 Personal Notes",
    "general_notes": "General Notes",
    "body_weight": "Body Weight",
    "sleep": "Sleep (h)",
    "rhr": "Resting HR",
    "hrv": "HRV (night)",
    "pain_notes": "Pain Notes",
}

def read_csv(path=None, file_name='post_session_data.csv'):
    if path is None:
        df = pd.read_csv(f"/Users/daleythomsen/Documents/GitHub/TriPT/data/raw/post_workout/{file_name}",         
            dtype=str)
    else:
        df = pd.read_csv(path,         
            dtype=str)
    df["Date"] = pd.to_datetime(df["Date"], format="mixed").dt.date
    #df = df.dropna(how="all").reset_index(drop=True)
    # df["Date"] = pd.to_datetime(df["Date"])
    # df["Body Weight"] = pd.to_float(df["Body Weight"])
    # df["Pain Notes"] = pd.to_string(df["Date"])
    # df["Sleep (h)"] = pd.to_float(df["Date"])
    # df["Resting HR"] = pd.to_float(df["Date"])
    # df["HRV (night)"] = pd.to_float(df["Date"])
    # df["Session 1 Personal Notes"] = pd.to_string(df["Date"])
    # df["Session 2 Personal Notes"] = pd.to_string(df["Date"])
    # df["General Notes"] = pd.to_string(df["Date"])
    return df

def gather_input(questions=user_input):
    for question in questions:
        while True:
            user_answer = input(question["prompt"]).strip()
            if question["name"] == "date":
                if user_answer == '':
                    user_answer = datetime.date.today()
                    question["user_answer"] = user_answer
                    break
                else:
                    try:
                        datetime.datetime.strptime(user_answer, '%Y-%m-%d')
                        question["user_answer"] = datetime.datetime.strptime(user_answer, "%Y-%m-%d").date()
                        break
                    except ValueError:
                        print("Incorrect format. Must be YYYY-MM-DD.")
            elif question["type"] == "float":
                    if user_answer == '':
                        question["user_answer"] = ''
                        break
                    else:
                        try:
                            user_answer = float(user_answer)
                            question["user_answer"] = user_answer
                            break
                        except ValueError:
                            print(f"Incorrect format. Must be {question['type']}.")
            elif question["type"] == "str":
                question["user_answer"] = user_answer
                break      

    return {question["name"]: question["user_answer"] for question in questions}

def write_data(user_answers, df, csv_schema_mapping=csv_schema_mapping, path=None, file_name='post_session_data.csv'):
    mapped_user_answers = pd.DataFrame([dict((csv_schema_mapping[key], value) for (key, value) in user_answers.items())])
    mapped_user_answers = mapped_user_answers.astype(str)#{column: dtype for column, dtype in column_dtypes.items() if column in list(mapped_user_answers.columns)})
    mapped_user_answers["Date"] = pd.to_datetime(mapped_user_answers["Date"], format="mixed").dt.date
    mapped_user_answers.set_index("Date", inplace=True)
    df.set_index("Date", inplace = True)
    if df.empty:
        df = mapped_user_answers
    else:
        if list(df.index.intersection(mapped_user_answers.index)) != []:
            while True:
                user_input = input(f"Data for {mapped_user_answers.index[0]} found. Do you want to overwrite? (yes, no): ")
                if (user_input.lower() == 'yes') | (user_input.lower() == 'y'):
                    df.update(mapped_user_answers)
                    break
                elif (user_input.lower() == 'no') | (user_input.lower() == 'n'):
                    break
                else:
                    print('Type yes or no')
        else:
            df = pd.concat([df, mapped_user_answers], ignore_index=False)
    float_columns = ["Body Weight", "Sleep (h)", "Resting HR", "HRV (night)"]
    df[float_columns] = df[float_columns].replace({'': None})
    df["Body Weight"] = df["Body Weight"].astype(float)
    df["Sleep (h)"] = df["Sleep (h)"].astype(float)
    df["Resting HR"] = df["Resting HR"].astype(float)
    df["HRV (night)"] = df["HRV (night)"].astype(float)
    df = df.sort_index(ascending=True)
    if path is None:
        df.to_csv(f"/Users/daleythomsen/Documents/GitHub/TriPT/data/raw/post_workout/{file_name}")
        print(f"File written to /Users/daleythomsen/Documents/GitHub/TriPT/data/raw/post_workout/{file_name}")
    else:
        df.to_csv(path)
        print(f"File written to {path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Update post-session training log.")
    parser.add_argument("-p", "--path", default=None)
    parser.add_argument("-f", "--file", default='post_session_data.csv')
    parser.add_argument("-t", "--time", default='both')
    args = parser.parse_args()

    df = read_csv(path=args.path, file_name=args.file)

    if args.time == "both":
        user_input = user_input["morning"]["questions"] + user_input["evening"]["questions"]
        user_input = list({question["name"]:question for question in user_input}.values())
    else:
        user_input = user_input[args.time]["questions"]
    user_answers = gather_input(user_input)
    write_data(user_answers=user_answers, df=df, csv_schema_mapping=csv_schema_mapping, file_name=args.file, path=args.path)
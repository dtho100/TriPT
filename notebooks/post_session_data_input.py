import numpy as np
import pandas as pd
import argparse
import datetime

questions = [
        {"name": "date", "prompt": "What date are you entering data for (YYYY-MM-DD)? ", "type": "date"},
        {"name": "body_weight", "prompt": "Enter morning BW: ", "type": "float"},
        {"name": "pain_notes", "prompt": "Enter any pains (out of 10) and where they occur: ", "type": "str"},
        {"name": "sleep", "prompt": "Enter number of hours slept: ", "type": "float"},
        {"name": "rhr", "prompt": "Enter RHR from last night: ", "type": "float"},
        {"name": "hrv", "prompt": "Enter HRV from last night: ", "type": "float"},
        {"name": "session_1_notes", "prompt": "Enter any Session 1 notes: ", "type": "str"},
        {"name": "session_2_notes", "prompt": "Enter any Session 2 notes: ", "type": "str"},
        {"name": "general_notes", "prompt": "Enter any other notes: ", "type": "str"},
    ]

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
    if path == None:
        df = pd.read_csv(f"/Users/daleythomsen/Documents/GitHub/TriPT/data/raw/post_workout/{file_name}")
    else:
        df = pd.read_csv(path)
    df = df.dropna(how="all").reset_index(drop=True)  
    return df

def gather_input(questions=questions):
    for question in questions:
        while True:
            user_answer = input(question["prompt"]).strip()
            if question["name"] == "date":
                if user_answer == '':
                    user_answer = datetime.datetime.now().strftime("%Y-%m-%d")
                    question["user_answer"] = user_answer
                    break
                else:
                    try:
                        date = datetime.datetime.strptime(user_answer, '%Y-%m-%d')
                        question["user_answer"] = user_answer
                        break
                    except ValueError:
                        print("Incorrect format. Must be YYYY-MM-DD.")
            elif question["type"] == "float":
                    if user_answer == '':
                        question["user_answer"] = None
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
    if df.empty:
        df = mapped_user_answers
    else:
        if df["Date"].eq(mapped_user_answers["Date"].iloc[0]).any():
            while True:
                user_input = input(f"Data for {mapped_user_answers['Date'].iloc[0]} found. Do you want to overwrite? (yes, no): ")
                if (user_input.lower() == 'yes') | (user_input.lower() == 'y'):
                    df = df[~df["Date"].eq(mapped_user_answers["Date"].iloc[0])]
                    df = pd.concat([df, mapped_user_answers], ignore_index=True)
                    break
                elif (user_input.lower() == 'no') | (user_input.lower() == 'n'):
                    break
                else:
                    print('Type yes or no')
        else:
            df = pd.concat([df, mapped_user_answers], ignore_index=True)
    if path == None:
        df.to_csv(f"/Users/daleythomsen/Documents/GitHub/TriPT/data/raw/post_workout/{file_name}", index=False)
        print(f"File written to /Users/daleythomsen/Documents/GitHub/TriPT/data/raw/post_workout/{file_name}")
    else:
        df.to_csv(path)
        print(f"File written to {path}")

    


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Update post-session training log.")
    parser.add_argument("--path", default=None)
    parser.add_argument("--file", default='post_session_data.csv')
    args = parser.parse_args()

    df = read_csv(path=args.path, file_name=args.file)
    user_answers = gather_input(questions)
    write_data(user_answers=user_answers, df=df, csv_schema_mapping=csv_schema_mapping, file_name=args.file, path=args.path)
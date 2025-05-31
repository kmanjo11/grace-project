#!/usr/bin/env python3
import json
import sys
import time
import pyotp
import requests
from typing import Dict, Any

def get_guest_token() -> str:
    res = requests.post(
        "https://api.twitter.com/1.1/guest/activate.json",
        headers={"Authorization": "Bearer AAAAAAAAAAAAAAAAAAAAAFXzAwAAAAAAMHCxpeSDG1gLNLghVe8d74hl6k4%3DRUMF4xAQLsbeBhTSRrCiQpJtxoGWeyHrDb5te2jpGskWDFW82F"},
    )
    return res.json()["guest_token"]

def get_flow_token(guest_token: str) -> str:
    res = requests.post(
        "https://api.twitter.com/1.1/onboarding/task.json?flow_name=login",
        headers={
            "Authorization": "Bearer AAAAAAAAAAAAAAAAAAAAAFXzAwAAAAAAMHCxpeSDG1gLNLghVe8d74hl6k4%3DRUMF4xAQLsbeBhTSRrCiQpJtxoGWeyHrDb5te2jpGskWDFW82F",
            "Content-Type": "application/json",
            "User-Agent": "TwitterAndroid/9.95.0-release.0 (29950000-r-0)",
            "X-Guest-Token": guest_token,
        },
        json={
            "input_flow_data": {
                "flow_context": {"debug_overrides": {}, "start_location": {"location": "splash_screen"}}
            },
            "subtask_versions": {},
        },
    )
    return res.json()["flow_token"]

def submit_username(guest_token: str, flow_token: str, username: str) -> str:
    res = requests.post(
        "https://api.twitter.com/1.1/onboarding/task.json",
        headers={
            "Authorization": "Bearer AAAAAAAAAAAAAAAAAAAAAFXzAwAAAAAAMHCxpeSDG1gLNLghVe8d74hl6k4%3DRUMF4xAQLsbeBhTSRrCiQpJtxoGWeyHrDb5te2jpGskWDFW82F",
            "Content-Type": "application/json",
            "User-Agent": "TwitterAndroid/9.95.0-release.0 (29950000-r-0)",
            "X-Guest-Token": guest_token,
        },
        json={
            "flow_token": flow_token,
            "subtask_inputs": [
                {
                    "subtask_id": "LoginEnterUserIdentifierSSO",
                    "settings_list": {
                        "setting_responses": [
                            {
                                "key": "user_identifier",
                                "response_data": {"text_data": {"result": username}},
                            }
                        ],
                        "link": "next_link",
                    },
                }
            ],
        },
    )
    return res.json()["flow_token"]

def submit_password(guest_token: str, flow_token: str, password: str) -> str:
    res = requests.post(
        "https://api.twitter.com/1.1/onboarding/task.json",
        headers={
            "Authorization": "Bearer AAAAAAAAAAAAAAAAAAAAAFXzAwAAAAAAMHCxpeSDG1gLNLghVe8d74hl6k4%3DRUMF4xAQLsbeBhTSRrCiQpJtxoGWeyHrDb5te2jpGskWDFW82F",
            "Content-Type": "application/json",
            "User-Agent": "TwitterAndroid/9.95.0-release.0 (29950000-r-0)",
            "X-Guest-Token": guest_token,
        },
        json={
            "flow_token": flow_token,
            "subtask_inputs": [
                {
                    "subtask_id": "LoginEnterPassword",
                    "enter_password": {"password": password, "link": "next_link"},
                }
            ],
        },
    )
    return res.json()["flow_token"]

def submit_2fa(guest_token: str, flow_token: str, code: str) -> Dict[str, Any]:
    res = requests.post(
        "https://api.twitter.com/1.1/onboarding/task.json",
        headers={
            "Authorization": "Bearer AAAAAAAAAAAAAAAAAAAAAFXzAwAAAAAAMHCxpeSDG1gLNLghVe8d74hl6k4%3DRUMF4xAQLsbeBhTSRrCiQpJtxoGWeyHrDb5te2jpGskWDFW82F",
            "Content-Type": "application/json",
            "User-Agent": "TwitterAndroid/9.95.0-release.0 (29950000-r-0)",
            "X-Guest-Token": guest_token,
        },
        json={
            "flow_token": flow_token,
            "subtask_inputs": [
                {
                    "subtask_id": "LoginTwoFactorAuthChallenge",
                    "enter_text": {"text": code, "link": "next_link"},
                }
            ],
        },
    )
    return res.json()

def get_session(username: str, password: str, totp_secret: str) -> Dict[str, Any]:
    guest_token = get_guest_token()
    flow_token = get_flow_token(guest_token)
    flow_token = submit_username(guest_token, flow_token, username)
    flow_token = submit_password(guest_token, flow_token, password)
    
    totp = pyotp.TOTP(totp_secret)
    code = totp.now()
    
    res = submit_2fa(guest_token, flow_token, code)
    subtasks = res["subtasks"]
    for subtask in subtasks:
        if subtask["subtask_id"] == "LoginSuccessSubtask":
            oauth_token = subtask["oauth_token"]
            oauth_token_secret = subtask["oauth_token_secret"]
            return {
                "id": int(time.time()),
                "start": int(time.time()),
                "oauth_token": oauth_token,
                "oauth_token_secret": oauth_token_secret,
                "valid": True,
            }
    raise Exception("Failed to get session")

def create_session_from_tokens(oauth_token: str, oauth_token_secret: str) -> Dict[str, Any]:
    return {
        "id": int(time.time()),
        "start": int(time.time()),
        "oauth_token": oauth_token,
        "oauth_token_secret": oauth_token_secret,
        "valid": True,
    }

def main():
    if len(sys.argv) == 3:
        # Direct token mode
        oauth_token = sys.argv[1]
        oauth_token_secret = sys.argv[2]
        session = create_session_from_tokens(oauth_token, oauth_token_secret)
        with open("../sessions.jsonl", "w") as f:
            json.dump(session, f)
            f.write("\n")
        print("Session saved to ../sessions.jsonl")
    elif len(sys.argv) == 5:
        # Full auth flow mode
        username = sys.argv[1]
        password = sys.argv[2]
        totp_secret = sys.argv[3]
        output_file = sys.argv[4]
        try:
            session = get_session(username, password, totp_secret)
            with open(output_file, "w") as f:
                json.dump(session, f)
                f.write("\n")
            print(f"Session saved to {output_file}")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"Usage:\n  {sys.argv[0]} <oauth_token> <oauth_token_secret>\n  {sys.argv[0]} <username> <password> <2fa_secret> <output_file>")
        sys.exit(1)

if __name__ == "__main__":
    main()

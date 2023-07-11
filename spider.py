import requests
import urllib.parse
import json
import os
import pickle
import base64
import re
from typing import Dict, List, Tuple
from datetime import datetime
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2 import credentials
from google.auth import external_account_authorized_user
from bs4 import BeautifulSoup

from utils import get_file_path
# Setup the Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def get_content(title: str, url: str) -> Path:
    """scrawl the content of a url and save it to a txt file

    Args:
        title (str): article title
        url (str): article url
    """
    token = json.load(open("./config/scrape_token.json"))["token"]

    encoded_url = urllib.parse.quote(url)
    url = "http://api.scrape.do?token={}&url={}".format(token, encoded_url)

    response = requests.request("GET", url)

    content = response.text
    soup = BeautifulSoup(content, "lxml")
    all_strings = [string for string in soup.stripped_strings]
    s = ''
    for string in all_strings:
        s += string

    f_path = get_file_path(title)
    with open(f_path, "w") as f:
        f.write(s)

    return f_path


def authenticate() -> external_account_authorized_user.Credentials | credentials.Credentials:
    """authenticate of the gmail api

    Returns:
        external_account_authorized_user.Credentials | credentials.Credentials: credentials that can be used to access gmail api
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('./config/token.pickle'):
        with open('./config/token.pickle', 'rb') as token:
            creds = pickle.load(token)
            return creds

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                './config/client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('./config/token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds


def is_ai_news_email(headers: List[Dict[str, str]]) -> bool:
    """if the email is about ai news

    Args:
        headers (List[Dict[str, str]]): email headers

    Returns:
        bool: if the email is about ai news
    """
    for header in headers:
        if header['name'] == 'Subject':
            return header['value'] == 'Trending AI news stories + papers'
    return False


def get_top_stories() -> List[Tuple[str, str]]:
    """get the latest ai news from the email

    Returns:
        List[Tuple[str, str]]: a list of (title, url) of the latest ai news
    """
    creds = authenticate()
    # Call the Gmail API
    service = build('gmail', 'v1', credentials=creds)
    results = service.users().messages().list(userId='me').execute()
    messages = results.get('messages', [])

    for message in messages:
        id = message['id']
        msg = service.users().messages().get(userId='me', id=id).execute()
        # Get the payload of the message
        payload = msg['payload']
        headers = payload['headers']
        if not is_ai_news_email(headers):
            continue
        parts = payload.get('parts')

        # decode the email body
        data = parts[0]['body']['data']
        data = data.replace("-", "+").replace("_", "/")
        decoded_data = base64.b64decode(data)

        # parse the email body
        soup = BeautifulSoup(decoded_data, "lxml")

        body = soup.body
        if not body:
            continue

        email_body = body()[0].text

        # find the index of the start and end of the news section
        start_index = email_body.find(
            "Top AI news stories") + len("Top AI news stories")
        end_index = email_body.find("Top AI papers")

        news_section = email_body[start_index:end_index].strip()
        news_items = news_section.split('\n')

        news_list = []

        for news in news_items:
            match = re.search(r'\[(.*?)\]', news)
            if match:
                url = match.group(1)
                title = news[:news.find('[')].strip()
                news_list.append((title, url))

        return news_list

    return []


if __name__ == "__main__":
    title = 'These are the American workers most worried that A.I. will soon make their jobs obsolete'
    url = 'https://substack.com/redirect/6078c0fe-8859-4b38-96bd-f3439427a54a?j=eyJ1IjoiMmR6aTV3In0.5_f9KebfPpDeeFzvTAYBkmyS55kERXXA2wTClkjMpko'
    get_content(title, url)

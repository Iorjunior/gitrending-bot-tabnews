import requests

from requests.adapters import Retry, HTTPAdapter
from datetime import datetime
from environs import Env

env = Env()
env.read_env()

SESSION = requests.session()
SESSION.headers["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"

retries = Retry(total=10, backoff_factor=1, status_forcelist=[502, 503, 504])

SESSION.mount('https://', HTTPAdapter(max_retries=retries))

BASE_TAB_API_URL = env('BASE_TAB_API_URL')
GITHUB_TRENDIND_API = env('GITHUB_TRENDIND_API')

CARD_TEMPLATE = """
### <img src="{}" alt="{}" width="80" loading=lazy /> [{} - ⭐ {} 🗜 {}]({}) 
{} \n _______________________________________________________________
"""


def get_token_session() -> str:
    payload = {
        'email': env('EMAIL'),
        'password': env('PASSWORD'),
    }

    response = SESSION.post(
        url=f'{BASE_TAB_API_URL}/sessions', data=payload).json()
    session_token = response['token']

    return session_token


def get_github_treding_list() -> list:
    response = SESSION.get(url=GITHUB_TRENDIND_API).json()

    return response


def generate_md(repos: list) -> str:
    md = ''

    for repo in repos:
        md += '\n' + CARD_TEMPLATE.format(repo['avatar'], repo['author'], repo['full_name'],
                                          repo['stars'], repo['forks'], repo['repo_url'], repo['description'])

    return md


def publish_post(session_token: str, md: str, title: str) -> str:
    payload = {
        "body": md,
        "source_url": "https://github.com/trending",
        "status": "published",
        "title": title
    }

    cookies = {
        'session_id': session_token
    }

    response = SESSION.post(
        url=f"{BASE_TAB_API_URL}/contents", data=payload, cookies=cookies).json()

    return response


def run_bot():
    repos_list = get_github_treding_list()
    md = generate_md(repos_list)
    title = f'🤖 Trending Repos Github - {datetime.today().strftime("%d/%m")}'

    session_token = get_token_session()
    publish_post(session_token, md, title)

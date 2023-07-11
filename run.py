import os
import time
from spider import get_content, get_top_stories
from llm import run_summarization
from tts import generate_audio_from_file
from utils import strip_string


def main():
    top5 = get_top_stories()[:5]
    for title, url in top5:
        print(title, url)
        title = strip_string(title)

        f_path = get_content(title, url.strip())
        summary, summary_path = run_summarization(f_path)
        print(summary)
        generate_audio_from_file(summary_path)
        time.sleep(1)


if __name__ == '__main__':
    os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
    os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'
    os.environ['ALL_PROXY'] = 'socks5://127.0.0.1:7890'

    main()

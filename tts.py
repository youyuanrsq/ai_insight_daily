from elevenlabs import clone, generate, play, set_api_key
from elevenlabs.api import History
import json


def generate_audio_from_file(file_path):
    with open('./config/elevenlab.json', 'r') as f:
        elevenlab_api_key = json.load(f)['api_key']

    set_api_key(elevenlab_api_key)

    text = ''

    with open(file_path) as f:
        text = f.read()

    audio = generate(
        text=text,
        voice="Bella",
        model='eleven_monolingual_v1'
    )

    play(audio)

# -*- coding: utf-8 -*-

# AwesomeTTS text-to-speech add-on for Anki
# Copyright (C) 2010-Present  Anki AwesomeTTS Development Team
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Service implementation for the Microsoft Azure Text-To-Speech service
https://azure.microsoft.com/en-us/services/cognitive-services/text-to-speech/
"""

import requests
from xml.etree import ElementTree
from .base import Service

__all__ = ['Azure']


VOICES = {
    'Microsoft Server Speech Text to Speech Voice (zh-CN, XiaoxiaoNeural)': ('zh-CN', 'female'),
    'Microsoft Server Speech Text to Speech Voice (zh-HK, Tracy, Apollo)': ('zh-HK', 'female')
}


class Azure(Service):
    """
    Provides a Service-compliant implementation for Microsoft Azure Text To Speech.
    """

    __slots__ = [
        'access_token'
    ]

    NAME = "Microsoft Azure"

    # Although Azure is an Internet service, we do not mark it with
    # Trait.INTERNET, as it is a paid-for-by-the-user API, and we do not want
    # to rate-limit it or trigger error caching behavior
    TRAITS = []

    #def __init__(self, temp_dir, lame_flags, normalize, logger, ecosystem):
    #    super(Azure, self).__init__(temp_dir, lame_flags, normalize, logger, ecosystem)
    #    self.access_token = None


    def desc(self):
        """Returns name with a voice count."""

        return "Azure API (%d voices)" % len(VOICES)

    def extras(self):
        """The Azure API requires an API key."""

        return [dict(key='key', label="API Key", required=True)]

    def options(self):
        """Provides access to voice only."""

        # make sure access token is requested when retrieving audio
        self.access_token = None

        def transform_voice(user_value):
            return user_value

        def get_voice_choices():
            result = []
            for voice_name, attributes in VOICES.items():
                entry = (voice_name, voice_name)
                result.append(entry)
            return result

        return [
            dict(key='voice',
                 label="Voice",
                 values=get_voice_choices(),
                 transform=transform_voice)
        ]

    def get_token(self, subscription_key):
        if len(subscription_key) == 0:
            raise ValueError("subscription key required")

        fetch_token_url = "https://eastus.api.cognitive.microsoft.com/sts/v1.0/issueToken"
        headers = {
            'Ocp-Apim-Subscription-Key': subscription_key
        }
        response = requests.post(fetch_token_url, headers=headers)
        self.access_token = str(response.text)

    def run(self, text, options, path):
        """Downloads from Azure API directly to an MP3."""

        subscription_key = options['key']
        if self.access_token == None:
            self.get_token(subscription_key)

        voice = options['voice']
        voice_name = voice
        language = VOICES[voice_name][0]

        base_url = 'https://eastus.tts.speech.microsoft.com/'
        url_path = 'cognitiveservices/v1'
        constructed_url = base_url + url_path
        headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'audio-24khz-96kbitrate-mono-mp3',
            'User-Agent': 'anki-awesome-tts'
        }

        xml_body = ElementTree.Element('speak', version='1.0')

        xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', language)
        voice = ElementTree.SubElement(xml_body, 'voice')
        voice.set('{http://www.w3.org/XML/1998/namespace}lang', language)
        voice.set(
            'name', voice_name)

        voice.text = text
        body = ElementTree.tostring(xml_body)

        response = requests.post(constructed_url, headers=headers, data=body)
        if response.status_code == 200:
            with open(path, 'wb') as audio:
                audio.write(response.content)
        else:
            error_message = f"Status code: {response.status_code} voice: [{voice_name}] language: [{language} subscription key: [{subscription_key}]]"
            raise ValueError(error_message)


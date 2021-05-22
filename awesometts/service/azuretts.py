# -*- coding: utf-8 -*-

# AwesomeTTS text-to-speech add-on for Anki
# Copyright (C) 2010-Present  Anki AwesomeTTS Development Team
# Copyright (C) 2020-2021 Nickolay <kelciour@gmail.com>
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
Service implementation for Microsoft Azure Text to Speech API
"""

import html
import requests
import time

from .base import Service
from .common import Trait

__all__ = ['AzureTTS']


class AzureTTS(Service):
    """
    Provides a Service-compliant implementation for Microsoft Azure Text to Speech.
    """

    __slots__ = [
        '_access_token',
        '_expire_time',
        '_api_key',
    ]

    NAME = "Microsoft Azure Text to Speech"

    TRAITS = [Trait.INTERNET]

    _voice_list = [
        ("ar-EG-SalmaNeural", "Arabic (Egypt), Salma (Neural)"),
        ("ar-EG-ShakirNeural", "Arabic (Egypt), Shakir (Neural)"),
        ("ar-EG-Hoda", "Arabic (Egypt), Hoda"),
        ("ar-SA-HamedNeural", "Arabic (Saudi Arabia), Hamed (Neural)"),
        ("ar-SA-ZariyahNeural", "Arabic (Saudi Arabia), Zariyah (Neural)"),
        ("ar-SA-Naayf", "Arabic (Saudi Arabia), Naayf"),
        ("bg-BG-BorislavNeural", "Bulgarian (Bulgaria), Borislav (Neural)"),
        ("bg-BG-KalinaNeural", "Bulgarian (Bulgaria), Kalina (Neural)"),
        ("bg-BG-Ivan", "Bulgarian (Bulgaria), Ivan"),
        ("ca-ES-JoanaNeural", "Catalan (Spain), Joana (Neural)"),
        ("ca-ES-AlbaNeural", "Catalan (Spain), Alba (Neural)"),
        ("ca-ES-EnricNeural", "Catalan (Spain), Enric (Neural)"),
        ("ca-ES-HerenaRUS", "Catalan (Spain), Herena"),
        ("zh-CN-XiaoxiaoNeural", "Chinese (Simplified, China), Xiaoxiao (Neural)"),
        ("zh-CN-YunyangNeural", "Chinese (Simplified, China), Yunyang (Neural)"),
        ("zh-CN-XiaoyouNeural", "Chinese (Simplified, China), Xiaoyou (Neural)"),
        ("zh-CN-YunyeNeural", "Chinese (Simplified, China), Yunye (Neural)"),
        ("zh-CN-XiaohanNeural", "Chinese (Simplified, China), Xiaohan (Neural)"),
        ("zh-CN-XiaomoNeural", "Chinese (Simplified, China), Xiaomo (Neural)"),
        ("zh-CN-XiaoruiNeural", "Chinese (Simplified, China), Xiaorui (Neural)"),
        ("zh-CN-XiaoxuanNeural", "Chinese (Simplified, China), Xiaoxuan (Neural)"),
        ("zh-CN-YunxiNeural", "Chinese (Simplified, China), Yunxi (Neural)"),
        ("zh-CN-HuihuiRUS", "Chinese (Simplified, China), Huihui"),
        ("zh-CN-Kangkang", "Chinese (Simplified, China), Kangkang"),
        ("zh-CN-Yaoyao", "Chinese (Simplified, China), Yaoyao"),
        ("zh-HK-HiuMaanNeural", "Chinese (Traditional, Hong Kong SAR China), HiuMaan (Neural)"),
        ("zh-HK-HiuGaaiNeural", "Chinese (Traditional, Hong Kong SAR China), HiuGaai (Neural)"),
        ("zh-HK-WanLungNeural", "Chinese (Traditional, Hong Kong SAR China), WanLung (Neural)"),
        ("zh-HK-Danny", "Chinese (Traditional, Hong Kong SAR China), Danny"),
        ("zh-HK-TracyRUS", "Chinese (Traditional, Hong Kong SAR China), Tracy"),
        ("zh-TW-HsiaoChenNeural", "Chinese (Traditional, Taiwan), HsiaoChen (Neural)"),
        ("zh-TW-HsiaoYuNeural", "Chinese (Traditional, Taiwan), HsiaoYu (Neural)"),
        ("zh-TW-YunJheNeural", "Chinese (Traditional, Taiwan), YunJhe (Neural)"),
        ("zh-TW-HanHanRUS", "Chinese (Traditional, Taiwan), HanHan"),
        ("zh-TW-Yating", "Chinese (Traditional, Taiwan), Yating"),
        ("zh-TW-Zhiwei", "Chinese (Traditional, Taiwan), Zhiwei"),
        ("hr-HR-GabrijelaNeural", "Croatian (Croatia), Gabrijela (Neural)"),
        ("hr-HR-SreckoNeural", "Croatian (Croatia), Srecko (Neural)"),
        ("hr-HR-Matej", "Croatian (Croatia), Matej"),
        ("cs-CZ-AntoninNeural", "Czech (Czechia), Antonin (Neural)"),
        ("cs-CZ-VlastaNeural", "Czech (Czechia), Vlasta (Neural)"),
        ("cs-CZ-Jakub", "Czech (Czechia), Jakub"),
        ("da-DK-ChristelNeural", "Danish (Denmark), Christel (Neural)"),
        ("da-DK-JeppeNeural", "Danish (Denmark), Jeppe (Neural)"),
        ("da-DK-HelleRUS", "Danish (Denmark), Helle"),
        ("nl-BE-ArnaudNeural", "Dutch (Belgium), Arnaud (Neural)"),
        ("nl-BE-DenaNeural", "Dutch (Belgium), Dena (Neural)"),
        ("nl-NL-ColetteNeural", "Dutch (Netherlands), Colette (Neural)"),
        ("nl-NL-FennaNeural", "Dutch (Netherlands), Fenna (Neural)"),
        ("nl-NL-MaartenNeural", "Dutch (Netherlands), Maarten (Neural)"),
        ("nl-NL-HannaRUS", "Dutch (Netherlands), Hanna"),
        ("en-AU-NatashaNeural", "English (Australia), Natasha (Neural)"),
        ("en-AU-WilliamNeural", "English (Australia), William (Neural)"),
        ("en-AU-Catherine", "English (Australia), Catherine"),
        ("en-AU-HayleyRUS", "English (Australia), Hayley"),
        ("en-CA-ClaraNeural", "English (Canada), Clara (Neural)"),
        ("en-CA-LiamNeural", "English (Canada), Liam (Neural)"),
        ("en-CA-HeatherRUS", "English (Canada), Heather"),
        ("en-CA-Linda", "English (Canada), Linda"),
        ("en-IN-NeerjaNeural", "English (India), Neerja (Neural)"),
        ("en-IN-PrabhatNeural", "English (India), Prabhat (Neural)"),
        ("en-IN-Heera", "English (India), Heera"),
        ("en-IN-PriyaRUS", "English (India), Priya"),
        ("en-IN-Ravi", "English (India), Ravi"),
        ("en-IE-ConnorNeural", "English (Ireland), Connor (Neural)"),
        ("en-IE-EmilyNeural", "English (Ireland), Emily (Neural)"),
        ("en-IE-Sean", "English (Ireland), Sean"),
        ("en-PH-JamesNeural", "English (Philippines), James (Neural)"),
        ("en-PH-RosaNeural", "English (Philippines), Rosa (Neural)"),
        ("en-GB-MiaNeural", "English (United Kingdom), Mia (Neural)"),
        ("en-GB-LibbyNeural", "English (United Kingdom), Libby (Neural)"),
        ("en-GB-RyanNeural", "English (United Kingdom), Ryan (Neural)"),
        ("en-GB-George", "English (United Kingdom), George"),
        ("en-GB-HazelRUS", "English (United Kingdom), Hazel"),
        ("en-GB-Susan", "English (United Kingdom), Susan"),
        ("en-US-JennyNeural", "English (United States), Jenny (Neural)"),
        ("en-US-GuyNeural", "English (United States), Guy (Neural)"),
        ("en-US-AriaNeural", "English (United States), Aria (Neural)"),
        ("en-US-AriaRUS", "English (United States), Aria"),
        ("en-US-BenjaminRUS", "English (United States), Benjamin"),
        ("en-US-GuyRUS", "English (United States), Guy"),
        ("en-US-ZiraRUS", "English (United States), Zira"),
        ("et-EE-AnuNeural", "Estonian (Estonia), Anu (Neural)"),
        ("et-EE-KertNeural", "Estonian (Estonia), Kert (Neural)"),
        ("fi-FI-SelmaNeural", "Finnish (Finland), Selma (Neural)"),
        ("fi-FI-HarriNeural", "Finnish (Finland), Harri (Neural)"),
        ("fi-FI-NooraNeural", "Finnish (Finland), Noora (Neural)"),
        ("fi-FI-HeidiRUS", "Finnish (Finland), Heidi"),
        ("fr-BE-CharlineNeural", "French (Belgium), Charline (Neural)"),
        ("fr-BE-GerardNeural", "French (Belgium), Gerard (Neural)"),
        ("fr-CA-SylvieNeural", "French (Canada), Sylvie (Neural)"),
        ("fr-CA-AntoineNeural", "French (Canada), Antoine (Neural)"),
        ("fr-CA-JeanNeural", "French (Canada), Jean (Neural)"),
        ("fr-CA-Caroline", "French (Canada), Caroline"),
        ("fr-CA-HarmonieRUS", "French (Canada), Harmonie"),
        ("fr-FR-DeniseNeural", "French (France), Denise (Neural)"),
        ("fr-FR-HenriNeural", "French (France), Henri (Neural)"),
        ("fr-FR-HortenseRUS", "French (France), Hortense"),
        ("fr-FR-Julie", "French (France), Julie"),
        ("fr-FR-Paul", "French (France), Paul"),
        ("fr-CH-ArianeNeural", "French (Switzerland), Ariane (Neural)"),
        ("fr-CH-FabriceNeural", "French (Switzerland), Fabrice (Neural)"),
        ("fr-CH-Guillaume", "French (Switzerland), Guillaume"),
        ("de-AT-IngridNeural", "German (Austria), Ingrid (Neural)"),
        ("de-AT-JonasNeural", "German (Austria), Jonas (Neural)"),
        ("de-AT-Michael", "German (Austria), Michael"),
        ("de-DE-KatjaNeural", "German (Germany), Katja (Neural)"),
        ("de-DE-ConradNeural", "German (Germany), Conrad (Neural)"),
        ("de-DE-HeddaRUS", "German (Germany), Hedda"),
        ("de-DE-Stefan", "German (Germany), Stefan"),
        ("de-CH-JanNeural", "German (Switzerland), Jan (Neural)"),
        ("de-CH-LeniNeural", "German (Switzerland), Leni (Neural)"),
        ("de-CH-Karsten", "German (Switzerland), Karsten"),
        ("el-GR-AthinaNeural", "Greek (Greece), Athina (Neural)"),
        ("el-GR-NestorasNeural", "Greek (Greece), Nestoras (Neural)"),
        ("el-GR-Stefanos", "Greek (Greece), Stefanos"),
        ("he-IL-AvriNeural", "Hebrew (Israel), Avri (Neural)"),
        ("he-IL-HilaNeural", "Hebrew (Israel), Hila (Neural)"),
        ("he-IL-Asaf", "Hebrew (Israel), Asaf"),
        ("hi-IN-MadhurNeural", "Hindi (India), Madhur (Neural)"),
        ("hi-IN-SwaraNeural", "Hindi (India), Swara (Neural)"),
        ("hi-IN-Hemant", "Hindi (India), Hemant"),
        ("hi-IN-Kalpana", "Hindi (India), Kalpana"),
        ("hu-HU-NoemiNeural", "Hungarian (Hungary), Noemi (Neural)"),
        ("hu-HU-TamasNeural", "Hungarian (Hungary), Tamas (Neural)"),
        ("hu-HU-Szabolcs", "Hungarian (Hungary), Szabolcs"),
        ("id-ID-ArdiNeural", "Indonesian (Indonesia), Ardi (Neural)"),
        ("id-ID-GadisNeural", "Indonesian (Indonesia), Gadis (Neural)"),
        ("id-ID-Andika", "Indonesian (Indonesia), Andika"),
        ("ga-IE-ColmNeural", "Irish (Ireland), Colm (Neural)"),
        ("ga-IE-OrlaNeural", "Irish (Ireland), Orla (Neural)"),
        ("it-IT-IsabellaNeural", "Italian (Italy), Isabella (Neural)"),
        ("it-IT-DiegoNeural", "Italian (Italy), Diego (Neural)"),
        ("it-IT-ElsaNeural", "Italian (Italy), Elsa (Neural)"),
        ("it-IT-Cosimo", "Italian (Italy), Cosimo"),
        ("it-IT-LuciaRUS", "Italian (Italy), Lucia"),
        ("ja-JP-NanamiNeural", "Japanese (Japan), Nanami (Neural)"),
        ("ja-JP-KeitaNeural", "Japanese (Japan), Keita (Neural)"),
        ("ja-JP-Ayumi", "Japanese (Japan), Ayumi"),
        ("ja-JP-HarukaRUS", "Japanese (Japan), Haruka"),
        ("ja-JP-Ichiro", "Japanese (Japan), Ichiro"),
        ("ko-KR-SunHiNeural", "Korean (South Korea), Sun-Hi (Neural)"),
        ("ko-KR-InJoonNeural", "Korean (South Korea), InJoon (Neural)"),
        ("ko-KR-HeamiRUS", "Korean (South Korea), Heami"),
        ("lv-LV-EveritaNeural", "Latvian (Latvia), Everita (Neural)"),
        ("lv-LV-NilsNeural", "Latvian (Latvia), Nils (Neural)"),
        ("lt-LT-LeonasNeural", "Lithuanian (Lithuania), Leonas (Neural)"),
        ("lt-LT-OnaNeural", "Lithuanian (Lithuania), Ona (Neural)"),
        ("ms-MY-OsmanNeural", "Malay (Malaysia), Osman (Neural)"),
        ("ms-MY-YasminNeural", "Malay (Malaysia), Yasmin (Neural)"),
        ("ms-MY-Rizwan", "Malay (Malaysia), Rizwan"),
        ("mt-MT-GraceNeural", "Maltese (Malta), Grace (Neural)"),
        ("mt-MT-JosephNeural", "Maltese (Malta), Joseph (Neural)"),
        ("nb-NO-PernilleNeural", "Norwegian Bokmål (Norway), Pernille (Neural)"),
        ("nb-NO-FinnNeural", "Norwegian Bokmål (Norway), Finn (Neural)"),
        ("nb-NO-IselinNeural", "Norwegian Bokmål (Norway), Iselin (Neural)"),
        ("nb-NO-HuldaRUS", "Norwegian Bokmål (Norway), Hulda"),
        ("pl-PL-AgnieszkaNeural", "Polish (Poland), Agnieszka (Neural)"),
        ("pl-PL-MarekNeural", "Polish (Poland), Marek (Neural)"),
        ("pl-PL-ZofiaNeural", "Polish (Poland), Zofia (Neural)"),
        ("pl-PL-PaulinaRUS", "Polish (Poland), Paulina"),
        ("pt-BR-FranciscaNeural", "Portuguese (Brazil), Francisca (Neural)"),
        ("pt-BR-AntonioNeural", "Portuguese (Brazil), Antonio (Neural)"),
        ("pt-BR-Daniel", "Portuguese (Brazil), Daniel"),
        ("pt-BR-HeloisaRUS", "Portuguese (Brazil), Heloisa"),
        ("pt-PT-DuarteNeural", "Portuguese (Portugal), Duarte (Neural)"),
        ("pt-PT-FernandaNeural", "Portuguese (Portugal), Fernanda (Neural)"),
        ("pt-PT-RaquelNeural", "Portuguese (Portugal), Raquel (Neural)"),
        ("pt-PT-HeliaRUS", "Portuguese (Portugal), Helia"),
        ("ro-RO-AlinaNeural", "Romanian (Romania), Alina (Neural)"),
        ("ro-RO-EmilNeural", "Romanian (Romania), Emil (Neural)"),
        ("ro-RO-Andrei", "Romanian (Romania), Andrei"),
        ("ru-RU-SvetlanaNeural", "Russian (Russia), Svetlana (Neural)"),
        ("ru-RU-DariyaNeural", "Russian (Russia), Dariya (Neural)"),
        ("ru-RU-DmitryNeural", "Russian (Russia), Dmitry (Neural)"),
        ("ru-RU-EkaterinaRUS", "Russian (Russia), Ekaterina"),
        ("ru-RU-Irina", "Russian (Russia), Irina"),
        ("ru-RU-Pavel", "Russian (Russia), Pavel"),
        ("sk-SK-LukasNeural", "Slovak (Slovakia), Lukas (Neural)"),
        ("sk-SK-ViktoriaNeural", "Slovak (Slovakia), Viktoria (Neural)"),
        ("sk-SK-Filip", "Slovak (Slovakia), Filip"),
        ("sl-SI-PetraNeural", "Slovenian (Slovenia), Petra (Neural)"),
        ("sl-SI-RokNeural", "Slovenian (Slovenia), Rok (Neural)"),
        ("sl-SI-Lado", "Slovenian (Slovenia), Lado"),
        ("es-MX-DaliaNeural", "Spanish (Mexico), Dalia (Neural)"),
        ("es-MX-JorgeNeural", "Spanish (Mexico), Jorge (Neural)"),
        ("es-MX-HildaRUS", "Spanish (Mexico), Hilda"),
        ("es-MX-Raul", "Spanish (Mexico), Raul"),
        ("es-ES-AlvaroNeural", "Spanish (Spain), Alvaro (Neural)"),
        ("es-ES-ElviraNeural", "Spanish (Spain), Elvira (Neural)"),
        ("es-ES-HelenaRUS", "Spanish (Spain), Helena"),
        ("es-ES-Laura", "Spanish (Spain), Laura"),
        ("es-ES-Pablo", "Spanish (Spain), Pablo"),
        ("sv-SE-SofieNeural", "Swedish (Sweden), Sofie (Neural)"),
        ("sv-SE-HilleviNeural", "Swedish (Sweden), Hillevi (Neural)"),
        ("sv-SE-MattiasNeural", "Swedish (Sweden), Mattias (Neural)"),
        ("sv-SE-HedvigRUS", "Swedish (Sweden), Hedvig"),
        ("ta-IN-PallaviNeural", "Tamil (India), Pallavi (Neural)"),
        ("ta-IN-ValluvarNeural", "Tamil (India), Valluvar (Neural)"),
        ("ta-IN-Valluvar", "Tamil (India), Valluvar"),
        ("te-IN-MohanNeural", "Telugu (India), Mohan (Neural)"),
        ("te-IN-ShrutiNeural", "Telugu (India), Shruti (Neural)"),
        ("te-IN-Chitra", "Telugu (India), Chitra"),
        ("th-TH-PremwadeeNeural", "Thai (Thailand), Premwadee (Neural)"),
        ("th-TH-AcharaNeural", "Thai (Thailand), Achara (Neural)"),
        ("th-TH-NiwatNeural", "Thai (Thailand), Niwat (Neural)"),
        ("th-TH-Pattara", "Thai (Thailand), Pattara"),
        ("tr-TR-AhmetNeural", "Turkish (Turkey), Ahmet (Neural)"),
        ("tr-TR-EmelNeural", "Turkish (Turkey), Emel (Neural)"),
        ("tr-TR-SedaRUS", "Turkish (Turkey), Seda"),
        ("uk-UA-OstapNeural", "Ukrainian (Ukraine), Ostap (Neural)"),
        ("uk-UA-PolinaNeural", "Ukrainian (Ukraine), Polina (Neural)"),
        ("ur-PK-AsadNeural", "Urdu (Pakistan), Asad (Neural)"),
        ("ur-PK-UzmaNeural", "Urdu (Pakistan), Uzma (Neural)"),
        ("vi-VN-HoaiMyNeural", "Vietnamese (Vietnam), HoaiMy (Neural)"),
        ("vi-VN-NamMinhNeural", "Vietnamese (Vietnam), NamMinh (Neural)"),
        ("vi-VN-An", "Vietnamese (Vietnam), An"),
        ("cy-GB-AledNeural", "Welsh (United Kingdom), Aled (Neural)"),
        ("cy-GB-NiaNeural", "Welsh (United Kingdom), Nia (Neural)"),
    ]

    _region_list = [
        ("australiaeast", "Australia East"),
        ("brazilsouth", "Brazil South"),
        ("canadacentral", "Canada Central"),
        ("centralus", "Central US"),
        ("eastasia", "East Asia"),
        ("eastus", "East US"),
        ("eastus2", "East US 2"),
        ("francecentral", "France Central"),
        ("centralindia", "India Central"),
        ("japaneast", "Japan East"),
        ("japanwest", "Japan West"),
        ("koreacentral", "Korea Central"),
        ("northcentralus", "North Central US"),
        ("northeurope", "North Europe"),
        ("southcentralus", "South Central US"),
        ("southeastasia", "Southeast Asia"),
        ("uksouth", "UK South"),
        ("westcentralus", "West Central US"),
        ("westeurope", "West Europe"),
        ("westus", "West US"),
        ("westus2", "West US 2"),
    ]

    def __init__(self, *args, **kwargs):
        self._access_token = None
        self._expire_time = None
        self._api_key = None
        super(AzureTTS, self).__init__(*args, **kwargs)

    def _languageCode(self, name):
        """
        Returns a language code (en-GB) from its name (en-GB-LibbyNeural).
        """

        return '-'.join(name.split('-')[:2])

    def desc(self):
        """
        Returns a short, static description.
        """

        return "Microsoft Azure Text to Speech (%d voices)." % (
            len(set(map(lambda x: self._languageCode(x[0]), self._voice_list))))

    def extras(self):
        """The Microsoft Azure Text to Speech requires an API key."""

        return [dict(key='key', label="API Key", required=True)]

    def options(self):
        """
        Provides access to voice only.
        """

        return [
            dict(
                key='voice',
                label="Voice",
                values=self._voice_list,
                transform=lambda x: x,
                default='en-GB-LibbyNeural',
            ),

            dict(
                key='region',
                label="Region",
                values=self._region_list,
                transform=lambda x: x,
                default='eastus',
            ),

            dict(
                key='quota',
                label="Quota",
                values=[
                    ('F0', "Free"),
                    ('S0', "Standard"),
                ],
                transform=lambda x: x,
                default='F0',
            ),

            dict(
                key='speed',
                label="Speed",
                values=(0.0, 3),
                transform=float,
                default=1.00,
            ),

            dict(
                key='pitch',
                label="Pitch",
                values=(0.0, 2.00),
                transform=float,
                default=0.00,
            ),
        ]

    def run(self, text, options, path):
        """
        Send a synthesis request to the Text-to-Speech API.
        """

        if self._api_key != options['key']:
            self._api_key = options['key']
            self._access_token = None

        if self._access_token is None or time.monotonic() > self._expire_time:
            fetch_token_url = 'https://{}.api.cognitive.microsoft.com/sts/v1.0/issueToken'.format(options['region'])
            headers = { 'Ocp-Apim-Subscription-Key': options["key"] }
            self._expire_time = time.monotonic() + 595 # valid for 10 minutes
            r = requests.post(fetch_token_url, headers=headers)
            r.raise_for_status()
            self._access_token = str(r.text)

        lang = self._languageCode(options['voice'])

        body = '<speak version="1.0" xmlns="https://www.w3.org/2001/10/synthesis" xml:lang="{}">'.format(lang)
        body += '<voice name="{}"><prosody rate="{}">{}</prosody></voice>'.format(options['voice'], options['speed'], text)
        body += '</speak>'

        body = body.encode("utf-8")

        headers = {
            "Authorization": "Bearer {}".format(self._access_token),
            "Content-type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "audio-24khz-48kbitrate-mono-mp3",
            "User-Agent": self.ecosystem.agent,
        }

        if options['quota'] == 'F0': # 20 requests per minute
            self._netops += 1

        r = requests.post('https://{}.tts.speech.microsoft.com/cognitiveservices/v1'.format(options['region']), headers=headers, data=body)

        r.raise_for_status()

        with open(path, 'wb') as response_output:
            response_output.write(r.content)

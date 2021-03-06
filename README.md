<img src="https://raw.githubusercontent.com/Macro303/PokemonGo-Eventer/master/logo.png" align="left" width="120" height="120" alt="PokemonGo - Eventer Logo">

# PokemonGo - Eventer
[![Version](https://img.shields.io/github/tag-pre/Macro303/PokemonGo-Eventer.svg?label=version&style=flat-square)](https://github.com/Macro303/PokemonGo-Eventer/releases)
[![Issues](https://img.shields.io/github/issues/Macro303/PokemonGo-Eventer.svg?style=flat-square)](https://github.com/Macro303/PokemonGo-Eventer/issues)
[![Contributors](https://img.shields.io/github/contributors/Macro303/PokemonGo-Eventer.svg?style=flat-square)](https://github.com/Macro303/PokemonGo-Eventer/graphs/contributors)
[![License](https://img.shields.io/github/license/Macro303/PokemonGo-Eventer.svg?style=flat-square)](https://opensource.org/licenses/MIT)

Uses Google Calendar + Google Sheets to create events for PokemonGo and invite people based on the type of Events they wish to be notified about

## Built Using
 - Python 3.8.2
 - PyYAML 5.3.1
 - google-api-python-client 1.8.0
 - google-auth-httplib2 0.0.3
 - google-auth-oauthlib 0.4.1
 - pytz 2019.3

## Execution
1. Create a project on [Google API Console](https://console.developers.google.com/apis/dashboard), adding both Google Sheets and Google Calendar APIs to the project.
2. Create a **OAuth 2.0 Client ID** and download the `credentials.json` file.
3. Run the following:
    ```bash
    $ pip install -r requirements.txt
    $ python -m Eventer -t
    ```
4. Edit the created `config.yaml` as needed.
5. Create the folder `events/`, fill it with a `.yaml` file for each event
6. Run the following:
    ```bash
   $ python -m Eventer
    ```

## Notes
If you want the full calendar you can find it with this link: [Pokemon Calendar](https://calendar.google.com/calendar?cid=MDZqaTEyY2tkZmVtbmFtNjJpb2MwbTZvbDRAZ3JvdXAuY2FsZW5kYXIuZ29vZ2xlLmNvbQ)
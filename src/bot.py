import time
import urllib.request
import requests
import yaml
import os
import socket

prev = 'live'
start = True
version = '1.1.2'

response = requests.get(f'http://twitchlurker.com/data.json')
latestVersion = response.json()["currentVersionLite"]

print("")
print(f"Running Twitch Lurker v{version}")
if version == latestVersion:
    print("You are on the latest version!")
else:
    print(f"\n! ! !\nVERSION ALERT: You are using v{version}. v{latestVersion} is now avaliable. Download it from: https://www.mc-market.org/resources/19906/\n! ! !\n")
print(f"If you need support feel free to ask in dsc.gg/fortbrleaks")
print("")

path = os.getcwd()+'/'

with open(path+r'settings.yml') as file:
    settings = yaml.load(file, Loader=yaml.FullLoader)

    system = settings['system']
    if system != 'windows' and system != 'raspberrypi' and system != 'linux':
        system = 'windows'
        print('Incorrect input found for "system", defaulted to "windows"')

    channel = settings['channel']
    if channel is None:
        channel = 'twitch'
        print('No input found for "channel", defaulted to "twitch"')

    delay = settings["delay"]
    if delay is None:
        delay = 300
        print('No input found for "delay", defaulted to "600"')

    twitch_accesstoken = settings["twitch"]["accesstoken"]
    if twitch_accesstoken is None:
        print('WARNING | Failed to load access token! Please see twitchlurker.com/getapi to learn how to get this.')

    twitch_clientid = settings["twitch"]["clientid"]
    if twitch_clientid is None:
        print('WARNING | Failed to load Client ID! Please see twitchlurker.com/getapi to learn how to get this.')

    pushbullet_enabled = settings["pushbullet"]["enabled"]
    if pushbullet_enabled != True and pushbullet_enabled != False:
        pushbullet_enabled = False
        print('Incorrect input found for "pushbullet_enabled", defaulted to "False"')

    pushbullet_thumbnail = settings["pushbullet"]["thumbnail"]
    if pushbullet_thumbnail != True and pushbullet_thumbnail != False:
        pushbullet_thumbnail = False
        print('Incorrect input found for "pushbullet_thumbnail", defaulted to "False"')

    if pushbullet_enabled:
        pushbullet_accesstoken = settings["pushbullet"]["accesstoken"]
        if pushbullet_accesstoken is None:
            pushbullet = False
            print('No access token for pushbullet has been found. Pushbullet integration has been disabled.')

if system == 'windows':
    from subprocess import Popen
if system == 'raspberrypi' or system == 'linux':
    import webbrowser

if pushbullet_enabled:
    from pushbullet import Pushbullet

    pb = Pushbullet(pushbullet_accesstoken)

headers = {'Authorization': f'Bearer {twitch_accesstoken}', 'Client-Id': f'{twitch_clientid}'}

if pushbullet_enabled:
    hostname = socket.gethostname()
    ipaddress = socket.gethostbyname(hostname)
    push = pb.push_note(f'🟢 TwitchLurker Started 🟢 (v{version})', f'⚙ SETTINGS:\nSystem: {system}\nHostname: {hostname}\nIP Address: {ipaddress}\nChannel: {channel}\nDelay: {delay}\nPushbullet Thumbnails: {pushbullet_thumbnail}\n\n⚡ TOKENS:\nTwitch Access Token: {twitch_accesstoken}\nTwitch Client ID: {twitch_clientid}\nPushbullet Access Token: {pushbullet_accesstoken}')

def checklive():
    response = requests.get(f'https://api.twitch.tv/helix/streams?client_id={twitch_clientid}&user_login={channel}',
                            headers=headers)

    try:
        data = response.json()["data"]
        if not data:
            live = False
        else:
            live = True
        return live

    except:
        message = response.json()["message"]
        print(f'\n* * * ERROR * * *\n{message}\n')
        print("Go to twitchlurker.com/getapi to get your tokens.")


def open_stream():
    print("Stream started, opening chrome now...")
    if system == 'windows':
        Popen(['start', 'chrome', f'http://www.twitch.tv/{channel}'], shell=True)
    elif system == 'raspberrypi':
        webbrowser.get('/usr/lib/chromium-browser/chromium-browser').open(f'http://www.twitch.tv/{channel}')
    elif system == 'linux':
        webbrowser.get('/usr/bin/google-chrome %s').open(f'http://www.twitch.tv/{channel}')


def close_stream():
    if not start:
        print("Stream ended, closing chrome now...")
        if system == 'windows':
            Popen('taskkill /F /IM chrome.exe', shell=True)
        elif system == 'raspberrypi':
            os.system("pkill chromium")
        elif system == 'linux':
            os.system("pkill chromium")


def open_pushbullet():
    response = requests.get(f'https://api.twitch.tv/helix/streams?client_id={twitch_clientid}&user_login={channel}',
                            headers=headers)
    try:
        title = response.json()["data"][0]["title"]
        game = response.json()["data"][0]["game_name"]
    except:
        title = 'null'
        game = 'null'

    if pushbullet_thumbnail:
        thumbnail_url = response.json()["data"][0]["thumbnail_url"].replace('{width}', '1920').replace('{height}',
                                                                                                       '1080')
        urllib.request.urlretrieve(thumbnail_url, path+"thumbnail.png")
        with open(path+"thumbnail.png", "rb") as pic:
            file_data = pb.upload_file(pic, "twitch.jpg")
        push = pb.push_file(**file_data)

        os.remove('thumbnail.png')

    push = pb.push_note(f'🔴 LIVESTREAM STARTED: {channel}: Started Lurking',
                        f'{channel}\'s livestream has started.\n\nTITLE: {title}\n\nGAME: {game}')


def close_pushbullet():
    push = pb.push_note(f'⚠ LIVESTREAM ENDED: Stopped Lurking',
                        f'{channel}\'s livestream has ended.\nTwitchLurker will re-open the stream when {channel} goes live again.')


while 1:
    try:
        if checklive() == False:
            clock = time.strftime('[%H:%M:%S]', time.localtime())
            print(f'{clock} Checking channel: {channel}\nNOT LIVE.\nNext check in {delay} seconds...\n')
            if prev == 'live':
                close_stream()
                if pushbullet_enabled:
                    close_pushbullet()
                start = False

            prev = 'notlive'


        else:
            clock = time.strftime('[%H:%M:%S]', time.localtime())
            print(f'{clock} Checking channel: {channel}\nResult: 🔴 LIVE.\nNext check in {delay} seconds...\n')
            if prev == 'notlive':
                open_stream()
                if pushbullet_enabled:
                    open_pushbullet()
            prev = 'live'
    except Exception as e:
        print(str(e)+"\n\nIf this persists please contact help @: dsc.gg/fortbrleaks")
        push = pb.push_note('⛔ Error found ⛔', str(e)+"\nIf this persists please contact help @: dsc.gg/fortbrleaks")
        pass

    time.sleep(delay)

# run
# python3 epplay.py -l http://ep256.hostingradio.ru:8052/europaplus256.mp3 -t 15 -a ./reklama
import vlc
import asyncio
import concurrent
from vlc import *
import time
import sys
from optparse import OptionParser
import os
from os import listdir
from os.path import isfile, join
import urllib.request


def audio_fade(player, timeout=2):
    player.audio_set_volume(100)
    player.play()
    interval = timeout / 100
    for i in range(100, 0, -1):
        player.audio_set_volume(i)
        time.sleep(interval)
    #player.stop()


def audio_raise(player, timeout=2):
    player.audio_set_volume(0)
    player.play()
    interval = timeout / 100
    for i in range(0, 100):
        player.audio_set_volume(i)
        time.sleep(interval)


url_check = ""


async def start_radio(radio):
  while True:
    print(url_check)
    try:
      code = urllib.request.urlopen(url_check).getcode()
      if code==200:
        break
      else:
        print('Oops, stream was down. Try to connect...')
        time.sleep(10)
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
      print('Oops, stream was down. Try to connect...')
      time.sleep(10)


loop=0
@vlc.callbackmethod
def replay(event, data):
  print("Solve problem...")
  loop.run_until_complete(start_radio(data))
  print("Problem solved!")

def main():
    global loop,executor
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    parser = OptionParser()
    parser.add_option("-l", "--listen", dest="url",
                      help="listen to sound from url")
    parser.add_option("-a", "--ads", dest="ads",
                      help="path to ads mp3 files")
    parser.add_option("-t", "--timeout", dest="timeout", type=int,
                      help="timeout to play ads")

    (options, args) = parser.parse_args()
    instance = vlc.Instance('--input-repeat=-1', '--fullscreen')
    radio = instance.media_player_new()
    media = instance.media_new(options.url)
    radio.set_media(media)
    global url_check
    url_check = options.url
    onlyfiles = [join(options.ads, f) for f in listdir(options.ads) if (isfile(join(options.ads, f)) and f.lower().endswith('.mp3'))]
    ads = sorted(onlyfiles, key=os.path.getmtime)
    print(ads)
    fade_timeout = 2
    cnt = 0
    e = radio.event_manager()
    e.event_attach(vlc.EventType.MediaPlayerEncounteredError, replay, radio)
    radio.audio_set_volume(100)
    radio.play()
    while True:
      print("Continue playing music!")
      time.sleep(options.timeout)
      print("Advertising time!")
      audio_fade(radio, fade_timeout)
      try:
        ad = vlc.MediaPlayer(ads[cnt])
        ad.audio_set_volume(100)
        ad.play()
        time.sleep(1)
        time.sleep(ad.get_length() / 1000 - fade_timeout)
        ad.stop()
        audio_raise(radio, fade_timeout)
        cnt += 1
        if cnt >= len(ads):
          cnt = 0
      except:
        audio_raise(radio, fade_timeout)
        print('Error playing advertising!')
        cnt += 1
        if cnt >= len(ads):
          cnt = 0


if __name__ == '__main__':
    main()

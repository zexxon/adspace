#!/usr/bin/env python

from __future__ import print_function
import time
import sys
import pychromecast

def getInput():
    if (len(sys.argv)) > 1:
        print(sys.argv[1])
        return sys.argv[1]
    return ""

def connectCast(ccName):
    chromeCasts = pychromecast.get_chromecasts()
    print(chromeCasts)
    [cc.device.friendly_name for cc in chromeCasts]
    cast = next(cc for cc in chromeCasts if cc.device.friendly_name == ccName)
    while cast.status is None:
        time.sleep(1)
        print("Waiting for Chromecast Status..")
    print(cast.device)
    print(cast.status)
    return cast

def controlMedia(cast):
    mc = cast.media_controller
    while True:
        muteAd(mc, cast)


def muteAd(mc, cast):
    # Check if there is any media available, if not sleep for 5 seconds and check again.
    if mc is None or mc.status.duration is None or mc.status.player_state == 'UNKNOWN' or cast.status.display_name == '':
        print("No Media Controller Found")
        time.sleep(5)
        return
    # Mute if there is no title, as it is an ad
    trackTime = (mc.status.duration - mc.status.current_time)
    if mc.status.title == '':
        if trackTime == 0:
            time.sleep(5)
        else:
            time.sleep(trackTime)
        cast.set_volume_muted(True)
        print("Ad detected or no music playing.. sleeping " + str(trackTime) + " seconds.")
        return
    # un-mute sound if muted
    cast.set_volume_muted(False)
    # if music is playing, sleep until track ends then check for ad
    if mc.status.artist is None:
        print("Track Artist: N/A")
    else:
        print("Track Artist: " + mc.status.artist)
    title = mc.status.title
    print("Track Title: " + title)
    print("Sleeping for " + str(trackTime) + " seconds")
    while mc.status.current_time < mc.status.duration:
        time.sleep(1)
        if mc.status.title != title:
            return
    return

# Main Program
controlMedia(connectCast(getInput()))
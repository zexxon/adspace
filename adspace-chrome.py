"""
Author: Matt Maloney
Simple auto ad mute program for Chromecast devices.
"""
from __future__ import print_function
import time
import sys
import pychromecast

def get_input():
    """
    Parse CLI inputs
    :return:
    """
    if (len(sys.argv)) > 1:
        if sys.argv[1] == "/?" or sys.argv[1] == "/h":
            print_help()
            sys.exit()
        if sys.argv[1] == "--discover" or sys.argv[1] == "-d":
            chromecasts = cast_discovery()
            print(chromecasts)
            sys.exit()
        # Else return chromecast device name
        print("Chrome Cast Device: ", sys.argv[1])
        return sys.argv[1]
    print_help()
    return sys.exit()


def print_help():
    """
    Help function
    :return:
    """
    print("Usage: python adspace-chrome.py [chromecast_friendly_name]|--discover")
    print("Example: python adspace-chrome.py livingroom")
    return


def cast_discovery():
    """
    Return discovered Chromecasts
    :return:
    """
    print("Discovering Chromecast devices...")
    try:
        chromecasts = pychromecast.get_chromecasts()
    except Exception as e:
        print("Unable to discover Chromecast devices, check network connection: ", str(e))
        sys.exit()  # If discovery failed, exit application
    return chromecasts  # Else return chromecast dictionary


def connect_cast(ccname):
    """
    Connect to a specific Chromecast device and return cast object
    :param ccname:
    :return:
    """
    chromecasts = cast_discovery()  # Discover available Chromecasts
    print("Discovered Chromecast(s): ", chromecasts)
    print(ccname)
    try:
        cast = next(cc for cc in chromecasts if cc.device.friendly_name == ccname)
        while cast.status is None:
            time.sleep(1)
            print("Waiting for Chromecast Status..")
            print("Device: ", cast.device)
            print("Device Status: ", cast.status)
    except Exception as e:
        print("Unable to connect to Chromecast device: ", ccname)
        print("Error Message: ", e)
        sys.exit()  # Exit application
    return cast


def control_media(cast):
    """
    Connect to Chromecast device media controller interface and run ad detection loop
    :param cast:
    :return:
    """
    try:
        mc = cast.media_controller
        while True:
            mute_ad(mc, cast)  # Look for ads to mute - forever
    except Exception as e:
        print("Error accessing Chromecast media controller: ", str(e))
        return


def mute_ad(mc, cast):
    """
    Look for 'ad' titles, mute when detected and then sleep.
    :param mc:
    :param cast:
    :return:
    """
    # Check if there is any media available, if not sleep for 5 seconds and check again.
    if mc is None or mc.status.duration is None or mc.status.player_state == 'UNKNOWN' or cast.status.display_name == '':
        print("No media is being streamed")
        time.sleep(5)
        return
    # Mute if there is no title, as it is an ad
    tracktime = (mc.status.duration - mc.status.current_time)
    if mc.status.title == '':
        if tracktime == 0:
            time.sleep(5)
        else:
            print("Track time:", str(tracktime))
            time.sleep(tracktime)
        cast.set_volume_muted(True)
        print("Ad detected or no music playing, muting sound and sleeping for a bit... ")
        return
    # un-mute sound if muted
    cast.set_volume_muted(False)
    # if music is playing, sleep until track ends then check for ad
    if mc.status.artist is None:
        print("Track Artist: N/A")
    else:
        print("Track Artist: " + mc.status.artist)
    title = mc.status.title  # Temporary title store for change detection
    print("Track Title: " + title)
    print("Sleeping for " + normalize_time(tracktime))
    while mc.status.current_time < mc.status.duration:
        time.sleep(1)
        if mc.status.title != title:
            return
    return

def normalize_time(rawtime):
    """
    Return normalized time for readability
    :param rawtime:
    :return:
    """
    try:  # Return normalized time in seconds or minutes
        if int(rawtime)/60 < 1:
                return str(round(int(rawtime), 1)) + " seconds"
        return str(round(int(rawtime)/60, 1)) + " minutes"
    except Exception as e:
        print("Error parsing time: ", str(e))
        return "N/A"  # Return N/A as time

# Main Program
control_media(connect_cast(get_input()))

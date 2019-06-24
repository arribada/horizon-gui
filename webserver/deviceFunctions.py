from flask import Flask
import subprocess




def callTrackerConfig(theCall):

    result = []

    try:
        result = subprocess.check_output(["sudo", "tracker_config", theCall])

    except subprocess.CalledProcessError as e:
        raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

    return result
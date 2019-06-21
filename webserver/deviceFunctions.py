from flask import Flask
import subprocess





def listConnectedDevices():

    result = []

    #subprocess.check_output(["sudo", "whatever-command", "params"])

    try:
        result = subprocess.check_output(["sudo", "tracker_config", "--status"])

    except subprocess.CalledProcessError as e:
        raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))



    return result
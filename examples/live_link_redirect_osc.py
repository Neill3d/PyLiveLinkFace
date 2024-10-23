#
# live_link_redirect_osc.py
#
# This script retransmits LiveLink packets into OSC packets,
# converting facial data (head orientation, eye orientation, and blendshapes).
# It runs in a loop until a keyboard button is pressed.
#
# Neill3d


from __future__ import annotations
import socket
import signal
import math

from pylivelinkface import PyLiveLinkFace, FaceBlendShape
from pythonosc import udp_client, osc_bundle_builder, osc_message_builder
from enum import Enum

LIVE_LINK_UDP_PORT = 11111  # defined in the LiveLink App
LIVE_LINK_UDP_IP = "127.0.0.1"  # Localhost (change if needed)
OSC_UDP_PORT = 9000         # default port for OSC UDP server
OSC_UDP_IP = '127.0.0.1'    # localhost

# Mapping function
def map_blendshape_indices():
    # Mapping from FaceBlendShape Enum to Blendshape index values
    blendshape_mapping = {
        FaceBlendShape.BrowInnerUp: 0,
        FaceBlendShape.BrowDownLeft: 1,
        FaceBlendShape.BrowDownRight: 2,
        FaceBlendShape.BrowOuterUpLeft: 3,
        FaceBlendShape.BrowOuterUpRight: 4,
        FaceBlendShape.EyeLookUpLeft: 5,
        FaceBlendShape.EyeLookUpRight: 6,
        FaceBlendShape.EyeLookDownLeft: 7,
        FaceBlendShape.EyeLookDownRight: 8,
        FaceBlendShape.EyeLookInLeft: 9,
        FaceBlendShape.EyeLookInRight: 10,
        FaceBlendShape.EyeLookOutLeft: 11,
        FaceBlendShape.EyeLookOutRight: 12,
        FaceBlendShape.EyeBlinkLeft: 13,
        FaceBlendShape.EyeBlinkRight: 14,
        FaceBlendShape.EyeSquintLeft: 15,
        FaceBlendShape.EyeSquintRight: 16,
        FaceBlendShape.EyeWideLeft: 17,
        FaceBlendShape.EyeWideRight: 18,
        FaceBlendShape.CheekPuff: 19,
        FaceBlendShape.CheekSquintLeft: 20,
        FaceBlendShape.CheekSquintRight: 21,
        FaceBlendShape.NoseSneerLeft: 22,
        FaceBlendShape.NoseSneerRight: 23,
        FaceBlendShape.JawOpen: 24,
        FaceBlendShape.JawForward: 25,
        FaceBlendShape.JawLeft: 26,
        FaceBlendShape.JawRight: 27,
        FaceBlendShape.MouthFunnel: 28,
        FaceBlendShape.MouthPucker: 29,
        FaceBlendShape.MouthLeft: 30,
        FaceBlendShape.MouthRight: 31,
        FaceBlendShape.MouthRollUpper: 32,
        FaceBlendShape.MouthRollLower: 33,
        FaceBlendShape.MouthShrugUpper: 34,
        FaceBlendShape.MouthShrugLower: 35,
        FaceBlendShape.MouthClose: 36,
        FaceBlendShape.MouthSmileLeft: 37,
        FaceBlendShape.MouthSmileRight: 38,
        FaceBlendShape.MouthFrownLeft: 39,
        FaceBlendShape.MouthFrownRight: 40,
        FaceBlendShape.MouthDimpleLeft: 41,
        FaceBlendShape.MouthDimpleRight: 42,
        FaceBlendShape.MouthUpperUpLeft: 43,
        FaceBlendShape.MouthUpperUpRight: 44,
        FaceBlendShape.MouthLowerDownLeft: 45,
        FaceBlendShape.MouthLowerDownRight: 46,
        FaceBlendShape.MouthPressLeft: 47,
        FaceBlendShape.MouthPressRight: 48,
        FaceBlendShape.MouthStretchLeft: 49,
        FaceBlendShape.MouthStretchRight: 50,
        FaceBlendShape.TongueOut: 51
    }
    return blendshape_mapping


# Function to send OSC messages via UDP
def send_osc_message(osc_client, address, *args):
    msg = osc_message_builder.OscMessageBuilder(address=address)
    for arg in args:
        msg.add_arg(arg)
    msg = msg.build()
    osc_client.send(msg)


def send_osc_bundle(osc_client, blendshape_values, head_rotation, left_eye_rotation, right_eye_rotation):
    # Create an OSC bundle
    bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
    
    # Add each blendshape value as a message to the bundle
    for blendshape_index, value in blendshape_values.items():
        # Build the OSC message with the address and value
        msg = osc_message_builder.OscMessageBuilder(address="/W")
        msg.add_arg(blendshape_index)  # Blendshape index (int)
        msg.add_arg(value)             # Blendshape value (float)
        bundle.add_content(msg.build())  # Add the message to the bundle

    # include rotations
    msg = osc_message_builder.OscMessageBuilder(address='/HR')
    msg.add_arg(head_rotation[0])
    msg.add_arg(head_rotation[1])
    msg.add_arg(head_rotation[2])
    bundle.add_content(msg.build())

    msg = osc_message_builder.OscMessageBuilder(address='/ELR')
    msg.add_arg(left_eye_rotation[0])
    msg.add_arg(left_eye_rotation[1])
    bundle.add_content(msg.build())

    msg = osc_message_builder.OscMessageBuilder(address='/ERR')
    msg.add_arg(right_eye_rotation[0])
    msg.add_arg(right_eye_rotation[1])
    bundle.add_content(msg.build())

    # Serialize the bundle to bytes
    bundle_bytes = bundle.build()
    osc_client.send(bundle_bytes)

#
# MAIN

blendshape_mapping = map_blendshape_indices()
blendshape_values = {index: 0.0 for index in blendshape_mapping.values()}
head_rotation = [0.0] * 3
left_eye_rotation = [0.0] * 3
right_eye_rotation = [0.0] * 3

live_link_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
osc_client = udp_client.SimpleUDPClient(OSC_UDP_IP, OSC_UDP_PORT)

def graceful_exit(signum, frame):
    print("Exiting...")
    live_link_sock.close()
    exit(0)

# Handle graceful exit on Ctrl+C or termination
signal.signal(signal.SIGINT, graceful_exit)
signal.signal(signal.SIGTERM, graceful_exit)

try: 
    # open a UDP socket on all available interfaces with the given port
    live_link_sock.bind(("", LIVE_LINK_UDP_PORT)) 
    while True: 
        data, addr = live_link_sock.recvfrom(1024) 

        success, live_link_face = PyLiveLinkFace.decode(data)
        if success:

            for blendshape, index in blendshape_mapping.items():
                value = live_link_face.get_blendshape(blendshape)    
                blendshape_values[index] = value

            head_rotation[0] = math.degrees(-live_link_face.get_blendshape(FaceBlendShape.HeadPitch))
            head_rotation[1] = math.degrees(live_link_face.get_blendshape(FaceBlendShape.HeadYaw))
            head_rotation[2] = math.degrees(live_link_face.get_blendshape(FaceBlendShape.HeadRoll))

            left_eye_rotation[0] = math.degrees(-live_link_face.get_blendshape(FaceBlendShape.LeftEyePitch))
            left_eye_rotation[1] = math.degrees(live_link_face.get_blendshape(FaceBlendShape.LeftEyeYaw))
            left_eye_rotation[2] = math.degrees(live_link_face.get_blendshape(FaceBlendShape.LeftEyeRoll))

            right_eye_rotation[0] = math.degrees(-live_link_face.get_blendshape(FaceBlendShape.RightEyePitch))
            right_eye_rotation[1] = math.degrees(live_link_face.get_blendshape(FaceBlendShape.RightEyeYaw))
            right_eye_rotation[2] = math.degrees(live_link_face.get_blendshape(FaceBlendShape.RightEyeRoll))

            send_osc_bundle(osc_client, blendshape_values, head_rotation, left_eye_rotation, right_eye_rotation)
            
except KeyboardInterrupt:
    pass
       
finally: 
    live_link_sock.close()
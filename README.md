# PyLiveLinkFace

PyLiveLinkFace enables you to receive data sent from Epics [LiveLinkFace App](https://apps.apple.com/us/app/live-link-face/id1495370836) and send your own facial data to the [Unreal Engine](https://www.unrealengine.com/en-US/) using the [LiveLink Plugin](https://docs.unrealengine.com/4.27/en-US/AnimatingObjects/SkeletalMeshAnimation/LiveLinkPlugin/) via python.
It's designed that you don't need to change anything inside the Unreal Engine, if you can receive facial Data from the IPhone app, this libary will also work out of the box for you.
Tested with Unreal Engine 4.27.

## Prerequisites
To setup the LiveLink plugin and system in Unreal, see the following tutorial:
https://docs.unrealengine.com/4.27/en-US/AnimatingObjects/SkeletalMeshAnimation/FacialRecordingiPhone/

## Requirements
PyLiveLinkFace needs the following python libraries:
<ul>
  <li>numpy</li>
  <li>timecode</li>
 </ul>
 
## Install

To install it, clone the git repo and install it with the setup.py file:
```
python setup.py install
```

## Redirect packets to OSC
If you want to use the LiveLink Face app for OSC-based input devices, you can run the examples/live_link_redirect_osc.py script as a service. It listens to LiveLink Face app packets, converts the data into OSC bundle messages, and sends OSC packets on port 9000.

The OSC messages follow the FaceCap format, as described here: https://www.bannaflak.com/face-cap/livemode.html.

There is an additional dependency required to make it work.
 <ul>
  <li>python-osc</li>
 </ul>

 MotionBuilder device to read OSC packets live in OpenMobu repository - https://github.com/Neill3d/OpenMoBu

## Usage

The default LiveLinkFace App works with UDP sockets on the Port 11111. You need to open an UDP-Socket for sending or receiving the data. For example files, see the [examples folder](examples)

#### Sending data

To send facial data to the UnrealEngine, create a new PyLiveLinkFace object, connect an UDP socket and set your desired values.
Finally pack all the data via the 'encode()' into bytes and send it over the socket.

```python
from pylivelinkface import PyLiveLinkFace, FaceBlendShape

py_face = PyLiveLinkFace()

UDP_IP = "127.0.0.1"
UDP_PORT = 11111

# connect to the udp socket of the running Unreal Project
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
s.connect((UDP_IP, UDP_PORT))

# set the head rotation to random values             
py_face.set_blendshape(FaceBlendShape.HeadPitch, random.uniform(-1, 1))
py_face.set_blendshape(FaceBlendShape.HeadRoll,random.uniform(-1, 1))
py_face.set_blendshape(FaceBlendShape.HeadYaw, random.uniform(-1, 1))

# encode the PyLiveLinkFace data to bytes and send them
s.sendall(py_face.encode())
s.close()
``` 

#### Receiving data

To receive facial data from an IPhone LiveLinkFace app or another PyLiveLinkFace instance, open an UDP socket and set your desired values.
Finally unpack all the data via the 'deencode()' into a PyLiveLinkFace object.

```python
from pylivelinkface import PyLiveLinkFace, FaceBlendShape

UDP_PORT = 11111

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# open a UDP socket on all available interfaces with the given port
s.bind(("", UDP_PORT)) 
while True: 
    data, addr = s.recvfrom(1024) 
    # decode the bytes data into a PyLiveLinkFace object
    success, live_link_face = PyLiveLinkFace.decode(data)
    if success:
        # get the blendshape value for the HeadPitch and print it
        pitch = live_link_face.get_blendshape(FaceBlendShape.HeadPitch)
        print (live_link_face.name, pitch)       
        pass

s.close()
``` 





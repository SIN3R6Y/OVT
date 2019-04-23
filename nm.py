import NetworkManager
from subprocess import Popen

# This can most likely be done just as easily with the python library,
# but this works. Why reinvent the wheel? As dirty as this feels,
# programming every wifi edge condition into this involves quite a bit
# of work with a large error margin. However nmcli already does this
# and when new wifi technologies come out it can just be updated
# rather than us having to keep this method constantly up to date.
#
# I'm all ears if you have a better idea...
#
# TODO: We probably need to detect 802-1x...
def addAp (path, ssid, key):
  args = [path, 'device', 'wifi', 'connect', ssid, 'password', key]
  nmcliProcess = Popen(args)
  nmcliProcess.wait()
  
  if nmcliProcess.returncode == 0:
    return True
  
  else:
    return False

def getAps():
  aps = []
  for device in NetworkManager.NetworkManager.GetDevices():
    if device.DeviceType != NetworkManager.NM_DEVICE_TYPE_WIFI:
      continue
    for ap in device.GetAccessPoints():
      aps.append(ap)
      
  return aps

# Not sure if this is ugly or elegant... probably ugly.
def isConnected():
  for connection in NetworkManager.NetworkManager.ActiveConnections:
    return True
    
  return False

import sys
import urllib2
from random import randint
from ssl import SSLContext, PROTOCOL_TLSv1_2
from xml.etree import cElementTree as ET

# The oVirt 3 SDK does all of this, but considering it is now
# deprecated it would be unwise to use it. Whereas the oVirt 4
# SDK does very little of this and would require a similar amount
# of work. Considering we just use a handful of API calls, it seemed
# easy enough to just maintain our own API reference and update it
# as neccesary.

def acquireVm(url, authStr, vmpid):
  request = urllib2.Request('%s/%s/%s/%s' % (url, 'vmpools',
    vmpid, 'allocatevm'), data="<action/>")

  request.add_header('Authorization', 'Basic ' + authStr)
  request.add_header('Content-Type', 'application/xml')
  sslContext = SSLContext(PROTOCOL_TLSv1_2)
      
  try:
    urllib2.urlopen(request, context=sslContext)
    return True

  # TODO: this is ugly
  except urllib2.HTTPError:
    return False


def getTicket(url, authStr, vmid, protocol):
  request = urllib2.Request('%s/%s/%s/%s' % (url, 'vms', vmid,
    'graphicsconsoles'))
  request.add_header('Authorization', 'Basic ' + authStr)
  sslContext = SSLContext(PROTOCOL_TLSv1_2)

  tickets = ET.fromstring(urllib2.urlopen(request,
    context=sslContext).read())

  ticket = None
  for data in tickets.findall('graphics_console'):
    displayProto = data.findall('protocol')[0]
    if displayProto.text.lower() == protocol:
        ticket = data.get('id')

  return ticket



def getVms(url, authStr):
  request = urllib2.Request('%s/%s' % (url, 'vms'))
  request.add_header('Authorization', 'Basic ' + authStr)
  sslContext = SSLContext(PROTOCOL_TLSv1_2)

  vms = []
  vmList = ET.fromstring(urllib2.urlopen(request,
    context=sslContext).read())

  for data in vmList.findall('vm'):
    vms.append({'id':data.get('id'), 'name':data.find('name').text})
  
  return vms

def getVmps(url, authStr):
  request = urllib2.Request('%s/%s' % (url, 'vmpools'))
  request.add_header('Authorization', 'Basic ' + authStr)
  sslContext = SSLContext(PROTOCOL_TLSv1_2)

  vmps = []
  vmPoolList = ET.fromstring(urllib2.urlopen(request,
    context=sslContext).read())
      
  for data in vmPoolList.findall('vm_pool'):
    vmps.append({'id':data.get('id'), 'name':data.find('name').text})

  return vmps

def getVvFile(url, authStr, vmid, ticket, fullscreen):
  request = urllib2.Request('%s/%s/%s/%s/%s' % (url, 'vms', vmid, 
    'graphicsconsoles', ticket))

  request.add_header('Authorization', 'Basic ' + authStr)
  request.add_header('Content-Type', 'application/xml')
  request.add_header('Accept', 'application/x-virt-viewer')
  sslContext = SSLContext(PROTOCOL_TLSv1_2)

  try:
    vvContents = urllib2.urlopen(request, context=sslContext).read()
  
  # TODO: this is ugly
  except urllib2.HTTPError:
    return 1
 
  if fullscreen.lower() == 'yes':
    vvContents = vvContents.replace('fullscreen=0', 'fullscreen=1')
  
  elif fullscreen.lower() != 'no':
    return 2

  filename = '/tmp/viewer-' + str(randint(10000, 99999))
  f = open(filename, 'w')
  f.write(vvContents)
  f.close()

  return filename

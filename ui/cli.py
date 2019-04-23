import api
import nm
import os
import sys
import time
import urllib2
import functions as func
from base64 import encodestring

# TODO: If windows support is desired, you could probably do most
#       of this with msvcrt...
class GetChar:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

def start(config):
	  
  while True:
    
    os.system('clear')
    if nm.isConnected():
      break
    
    printHeader(config)
    
    print('No active network connection detected, '
      + 'obtaining network list...')
    
    aps = nm.getAps()
    if aps:
      i = 1
      validIndices = []
      for ap in aps:
        print str(i) + '. ' + ap.Ssid
        validIndices.append(i)
        i = i + 1
      
      try:
        ap = raw_input('Select a Wireless Network:')
        
      except EOFError:
        return
      
      inputValid = False
      for index in validIndices:
        if int(ap) == index:
          inputValid = True
          
      if not inputValid:
        print 'Invalid Selection:' + ap
        time.sleep(5)
        return
      
      # We end up passing this directly to nmcli, which raises concerns
      # about shell injection. It appears that this is not the case
      # as Popen runs with Shell=False by default, but maybe we
      # should sanitize this anyways?
      key = maskPrompt('Security Key:')
      
      if not nm.addAp(config.get('environment', 'nmpath'),
        aps[int(ap) - 1].Ssid, key):
        
        # If we get here, nmcli returned an error. Let's
        # give the user a few seconds to read it.
        time.sleep(5)
        
    else:
      print 'No available networks found, scanning again...'
      time.sleep(5)

  os.system('clear')
  
  printHeader(config)

  try:
    uname = raw_input("Username:")
    
  except EOFError:
    return
  
  pword = maskPrompt('Password:')
  
  if not pword:
    return
  
  if '@' in uname:
    authStr = encodestring('%s:%s' % (uname, pword)).replace('\n', '')
  
  else:
    authStr = encodestring('%s:%s' % (uname + '@' + config.get('ovirt',
      'profile'), pword)).replace('\n', '')

  try:
    print 'Obtaining VM list from engine...'

    vms = api.getVms(config.get('ovirt', 'url'), authStr)
    
    if vms:
      # the user has VM's available 
      while True:
        # check for VM's again, needed if we reiterate this loop
        vms = api.getVms(config.get('ovirt', 'url'), authStr)
        
        if config.get('preferences', 'autocon').lower() == 'yes':
          if len(vms) == 1:
            skipVMSelect = True
          else:
            skipVMSelect = False
        elif config.get('preferences', 'autocon').lower() == 'no':
          skipVMSelect = False
          vms.append({'id':'pool', 'name':'Acquire from Pool'})
        else:
          print 'Invalid autocon value: ' + config.get('preferences',
            'autocon')
              
          print 'Please check settings.conf'
          time.sleep(5)
          return
        
        if not skipVMSelect: 
          i = 1
          validIndices = []
          sys.stdout.write("\n")
          for entry in vms:
            print str(i) + '. ' + entry['name']
            validIndices.append(i)
            i = i + 1
      
          try:
            vm = raw_input('Select a VM:')
            
          except EOFError:
            return
          
          inputValid = False
          for index in validIndices:
            if int(vm) == index:
              inputValid = True
              
          if not inputValid:
            print 'Invalid Selection:' + vm
            time.sleep(5)
            return
            
        else:
          vm = 1

        if vms[int(vm) - 1]['id'] == 'pool':
          print 'Obtaining VM pool list from engine...'
          if not poolHandler(config, authStr):
            if skipVMSelect:
              time.sleep(5)
              return
              
        else:
          ticket = api.getTicket(config.get('ovirt', 'url'), authStr,
            vms[int(vm) - 1]['id'], config.get('ovirt', 'protocol'))
            
          if ticket == None:
            print ('No display with ' + config.get('ovirt', 'protocol')
              + ' protocol found.')
            time.sleep(5)
            return

          timeout = 0
          while True:
            vvFile = api.getVvFile(config.get('ovirt', 'url'),
              authStr, vms[int(vm) - 1]['id'], ticket,
              config.get('preferences', 'fullscreen'))
                
            if vvFile == 1:
              time.sleep(5)
          
            elif vvFile == 2:
              print 'Invalid fullscreen setting: ' + config.get(
                'preferences', 'fullscreen')
            
              print 'Please check settings.conf'
              time.sleep(5)
              return
              
            else:
              break
                  
            if timeout >= 12:
              print 'Retrieving .vv file timed out!'
              time.sleep(5)
              return
            timeout = timeout + 1
          
          if config.get('environment', 'startx').lower() == 'no':
            viewerThread = func.startViewerNoX(config, vvFile)
              
          elif config.get('environment', 'startx').lower() == 'yes':
            viewerThread = func.startViewerX(config, vvFile)
              
          else:
            print 'Invalid startx setting: ' + config.get(
              'environment', 'startx')
              
            print 'Please check settings.conf'
            time.sleep(5)
            return
          
          if viewerThread == None:
            print 'Invalid kiosk setting: ' + config.get(
              'preferences', 'kiosk')

            print 'Please check settings.conf'
            time.sleep(5)
            return
              
          sessTime = 0
          while viewerThread.isAlive():
            if sessTime >= int(config.get('preferences', 'maxsess')):
              viewerThread.kill = True
            time.sleep(1)
            sessTime = sessTime + 1
          break
    else:
      print 'No VMs found, obtaining VM pool list from engine.'
      
      if not poolHandler(config, authStr):
        time.sleep(5)
        return
          
      vms = api.getVms(config.get('ovirt', 'url'), authStr)
      
      if vms:
        while True:
          vms = api.getVms(config.get('ovirt', 'url'), authStr)
          
          if config.get('preferences', 'autocon').lower() == 'yes':
            if len(vms) == 1:
              skipVMSelect = True
            else:
              skipVMSelect = False
          elif config.get('preferences', 'autocon').lower() == 'no':
            skipVMSelect = False
            vms.append({'id':'pool', 'name':'Acquire from Pool'})
          else:
            print 'Invalid autocon value: ' + config.get('preferences',
                'autocon')
              
            print 'Please check settings.conf'
            time.sleep(5)
            return
          
          if not skipVMSelect:
            i = 1
            validIndices = []
            sys.stdout.write("\n")
            for entry in vms:
              print str(i) + '. ' + entry['name']
              validIndicies.append(i)
              i = i + 1

            try:
              vm = raw_input('Select a VM:')
            
            except EOFError:
              return
            
            inputValid = False
            for index in validIndices:
              if int(vm) == index:
                inputValid = True
              
            if not inputValid:
              print 'Invalid Selection:' + vm
              time.sleep(5)
              return
            
          else:
            vm = 1

          if vms[int(vm) - 1]['id'] == 'pool':
            print 'Obtaining VM pool list from engine...'
            if not poolHandler(config, authStr):
              if skipVMSelect:
                time.sleep(5)
                return

          else:
            ticket = api.getTicket(config.get('ovirt', 'url'), authStr,
              vms[int(vm) - 1]['id'], config.get('ovirt', 'protocol'))
              
            if ticket == None:
              print ('No display with ' + config.get('ovirt', 
                'protocol') + ' protcol found.')
              time.sleep(5)
              return

            timeout = 0
            while True:
              vvFile = api.getVvFile(config.get('ovirt', 'url'),
                authStr, vms[int(vm) - 1]['id'], ticket,
                config.get('preferences', 'fullscreen'))
                
              if vvFile == 1:
                time.sleep(5)
          
              elif vvFile == 2:
                print 'Invalid fullscreen setting: ' + config.get(
                  'preferences', 'fullscreen')
            
                print 'Please check settings.conf'
                time.sleep(5)
                return
              
              else:
                break
                  
              if timeout >= 12:
                print 'Retrieving .vv file timed out!'
                time.sleep(5)
                return
              timeout = timeout + 1
          
            if config.get('environment', 'startx').lower() == 'no':
              viewerThread = func.startViewerNoX(config, vvFile)
              
            elif config.get('environment', 'startx').lower() == 'yes':
              viewerThread = func.startViewerX(config, vvFile)
              
            else:
              print 'Invalid startx setting: ' + config.get(
                'environment', 'startx')
              
              print 'Please check settings.conf'
              time.sleep(5)
              return
              
            if viewerThread == None:
              print 'Invalid kiosk setting: ' + config.get(
                'preferences', 'kiosk')
                
              print 'Please check settings.conf'
              time.sleep(5)
              return
              
            sessTime = 0
            while viewerThread.isAlive():
              if sessTime >= int(config.get('preferences', 'maxsess')):
                viewerThread.kill = True
              time.sleep(1)
              sessTime = sessTime + 1
            break
            
      else:
        print 'Failed to acquire VM from pool, please try again later.'
        time.sleep(5)
        return

  # TODO: this is ugly
  except urllib2.HTTPError:
    print 'Authentication error, please try again.'
    time.sleep(5)
    return

  except urllib2.URLError:
    return
    
def maskPrompt(prompt):
  for char in prompt:
    sys.stdout.write(char)
  pword = ""
  
  i = 0
  getChar = GetChar()

  while True:
    char = getChar()
    if ord(char) == 3:
      return False
    elif ord(char) == 13:
      break
    elif ord(char) == 127:
      if i > 0:
        sys.stdout.write("\x08 \x08")
        pword= pword[:-1]
        i = i - 1
    else:
      sys.stdout.write('*')
      pword = pword + char
      i = i + 1
  sys.stdout.write('\r\n')
  return pword
    
def poolHandler(config, authStr):
  vmps = api.getVmps(config.get('ovirt', 'url'), authStr)

  if vmps:
    
    if config.get('preferences', 'autocon').lower() == 'yes':
      if len(vmps) == 1:
        skipVMPSelect = True
      else:
        skipVMPSelect = False
    elif config.get('preferences', 'autocon').lower() == 'no':
        skipVMPSelect = False
    else:
      print 'Invalid autocon value: ' + config.get('preferences',
        'autocon')
              
      print 'Please check settings.conf'
      time.sleep(5)
      return
    
    if not skipVMPSelect:
      i = 1
      validIndices = []
      sys.stdout.write("\n")
      for entry in vmps:
        print str(i) + '. ' + entry['name']
        validIndices.append(i)
        i = i + 1
      
      try:  
        vmp = raw_input('Select a VM Pool:')
      
      except EOFError:
        return
      
      inputValid = False
      for index in validIndices:
        if int(vmp) == index:
          inputValid = True
             
      if not inputValid:
        print 'Invalid Selection:' + vmp
        time.sleep(5)
        return

    else:
      vmp = 1
      
    print 'Acquiring VM from pool...'

    if not api.acquireVm(config.get('ovirt', 'url'), authStr,
      vmps[int(vmp) - 1]['id']):
        
      print 'Pool acquisition limit reached, please try again later.'
      return False
        
    return True
  
  else:
    print 'No VM pools found, please try again later.'
    return False

def printHeader(config):
    curdir = os.path.dirname(os.path.realpath(__file__))
    
    disclaimerFile = open(curdir + '/resources/disclaimer.txt', 'r')
    logoFile = open(curdir + '/resources/cli_logo.txt', 'r')
    versionFile = open(curdir + '/resources/version.txt', 'r')
    
    disclaimer = disclaimerFile.read()
    logo = logoFile.read()
    version = versionFile.read()
    
    pname = config.get('preferences', 'pname')
    
    print logo
    print pname + ' - ' + version
    print disclaimer
    
    disclaimerFile.close()
    logoFile.close()
    versionFile.close()

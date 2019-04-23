#!/bin/python

import ConfigParser
import hashlib
import os
import time
from subprocess import Popen

curdir = os.path.dirname(os.path.realpath(__file__))
config = ConfigParser.ConfigParser()

kicount = 0

while True:
  config.read(curdir + '/settings.conf')
  interface = config.get('preferences', 'interface')
  
  if config.get('preferences', 'mpwordhash').lower() == 'changeme':
    print 'Change the maintence password hash!'
    print 'See settings.conf.sample for more information.'
    break
  
  try:
    if interface == 'cli':
      import ui.cli as cli
      
      cli.start(config)
      kicount = 0

    #TODO qt4, qt5

    else:
      print 'Unkown Interface:' + interface
      print 'Please check settings.conf'
      break
  
  except KeyboardInterrupt:
    kicount = kicount + 1
    
    if interface == 'cli':
      if kicount == 3:
        kicount = 0
        
        print '\n\nEntering Maintenance Mode!\n'
        pword = cli.maskPrompt('Maintenance Password:')
      
        if not pword:
          pass
      
        else:
          pwordSalt = pword + config.get('ovirt', 'url').lower()
          pwordHash = hashlib.sha1(pwordSalt).hexdigest()
          if pwordHash != config.get('preferences', 'mpwordhash'):
            print '\nInvalid maintenance password!'
            time.sleep(5)
          else:
            shellProcess = Popen(config.get('environment', 'shpath'))
            shellProcess.wait()
            pass

      else:
        pass
    

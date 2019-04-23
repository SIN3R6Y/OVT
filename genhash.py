import ConfigParser
import hashlib
import os
import ui.cli as cli

curdir = os.path.dirname(os.path.realpath(__file__))
config = ConfigParser.ConfigParser()
config.read(curdir + '/settings.conf')

if (config.get('ovirt', 'url').lower() == 
  'https://ovirt.example.org/ovirt-engine/api'):
  
  print 'Set the oVirt API URL before running genhash!'
  print 'See settings.conf.sample for more information.'
  
else:
  print 'Enter the maintenance password.\n'
  pword = cli.maskPrompt('Maintenance Password:')
  
  if pword:
    pwordSalt = pword +  config.get('ovirt', 'url').lower()
    pwordHash = hashlib.sha1(pwordSalt).hexdigest()
    print 'Set mpword hash in settings.conf to this value!'
    print pwordHash
  

import time
import sys
from subprocess import Popen
from threading import Thread

class ViewerThread(Thread):
  def __init__(self, args):
    self.args = args
    self.kill = False
    Thread.__init__(self)
    self.start()
    
  def run(self):
    viewerProcess = Popen(self.args)
    while viewerProcess.poll() is None:
      if self.kill:
        viewerProcess.kill()
      time.sleep(1)
    
    return

def startViewerX(config, vvFile):
   
  args = [config.get('environment', 'sxpath'),
    config.get('environment', 'rvpath'), 'file://%s' % (vvFile)]
    
  if config.get('preferences', 'kiosk').lower() == 'yes':
    args.append('-k')
    args.append('--kiosk-quit=on-disconnect')
    
  elif config.get('preferences', 'kiosk').lower() != 'no':
    return None
  
  paProcess = Popen([config.get('environment', 'pcpath'),
   'set-sink-mute', config.get('environment', 'psink'), 'n'])
    
  paProcess.wait()
  
  paProcess = Popen([config.get('environment', 'pcpath'),
   'set-sink-volume', config.get('environment', 'psink'), '100%'])
  
  paProcess.wait()
  
  thread = ViewerThread(args)

  return thread

def startViewerNoX(config, vvFile):
    
  args = [config.get('environment', 'rvpath'),
    'file://%s' % (vvFile)]
    
  if config.get('preferences', 'kiosk').lower() == 'yes':
    args.append('-k')
    args.append('--kiosk-quit=on-disconnect')
  
  elif config.get('preferences', 'kiosk').lower() != 'no':
    return None
  
  thread = ViewerThread(args)
  
  return thread

# Simple state machine class

#
# Example:
#    mysm = StateMachine()
#    mysm.add_state('STATE_1', state_1_handler)
#    mysm.add_state('STATE_1', state_2_handler)
#    mysm.add_state('END_STATE', end_handler, end_state=1)
#    mysm.set_initial_state('STATE_1')
#    mysm.run()
#

class StateMachine:
  def __init__(self, name):
      self.handlers = {}
      self.start_state = None
      self.end_states = []
      self.name = name

  def add_state(self, name, handler, end_state=0):
      self.handlers[name] = handler
      if end_state:
           self.end_states.append(name)

  def set_initial_state(self, name):
      self.start_state = name

  def run(self):
      try:
          handler = self.handlers[self.start_state]
      except:
          raise "InitializationError", "Initial state must be set"

      while 1:
          next_state = handler()
          if next_state in self.end_states:
              print "Shutting down state machine:", self.name
              handler = self.handlers[next_state] 
              handler()
              break 
          else:
              handler = self.handlers[next_state] 

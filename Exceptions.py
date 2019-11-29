class Error(Exception):
   """Base class for other exceptions"""
   pass

class WrongSequenceNumber(Error):
   """The sequence number is incorrect"""
   pass

class TimeoutError(Error):
   """Timeout"""
   pass

class WrongPayloadSize(Error):
   """Payload is too large"""
   pass

class ModeError(Error):
   """The mode is not defined correctly"""
   pass

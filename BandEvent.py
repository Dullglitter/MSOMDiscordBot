from datetime import datetime
TYPE = 'Band Event'

format_string = "%Y-%m-%d %H:%M"

class BandEvent:
    def __init__(self, name:str, time, doNotify, doCheckin):
        self.name = name
        if isinstance(time, str):
            self.time = datetime.strptime(time, format_string)
        elif isinstance(time, datetime):
            self.time = time
        else: 
            raise TypeError("time should be str or datetime")
        self.doNotify = bool(doNotify)
        self.doCheckin = bool(doCheckin)
        
    def toCSVrow(self):
        return 'event,' + self.internaltoCSVrow()
    
    def internaltoCSVrow(self):
        # if called by subclass, make sure to start with comma
        return '{},{},{},{}'.format(self.name, str(self.time), str(self.doNotify), str(self.doCheckin))
    
    def __lt__(self, other):
        return self.time < other.time
    
    def __gt__(self, other):
        return self.date > other.date
    
    
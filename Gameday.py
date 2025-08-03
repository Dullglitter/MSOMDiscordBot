from BandEvent import BandEvent
from datetime import datetime

class Gameday(BandEvent):
    
    def __init__(self, name:str, time, doNotify, doCheckin, otherTeam: str, isHome, isTimeAnnounced, otherMascot: str):
        super().__init__(name, time, doNotify, doCheckin)
        self.otherTeam = otherTeam
        self.isHome = bool(isHome)
        self.isTimeAnnounced = bool(isTimeAnnounced)
        self.otherMascot = otherMascot
        
        
    def toCSVrow(self):
        return 'gameday,' + super()._toCSVrow() + ',{},{},{},{}'.format(
            self.otherTeam, str(self.isHome), str(self.isTimeAnnounced), self.otherMascot)
        
        
    def __str__(self):
        location = 'UMD' if self.isHome else self.otherTeam
        time = 'with time finalized' if self.isTimeAnnounced else 'with time not announced'
        return 'Game' + super()._str() + ' against {} at {} {}, beat the {}!'.format(self.otherTeam, location, time, self.otherMascot)
    
    def announce_str(self, role):
        announcement = ''
        with open('gameday_notification.txt', 'r') as f:
            announcement = f.read()
        announcement = announcement.format(role=role, other_school=self.otherTeam, time=self.time.strftime('%#I:%M %p'), 
                                           other_mascot=self.otherMascot)
        return announcement
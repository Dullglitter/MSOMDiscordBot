from BandEvent import BandEvent
from datetime import datetime

class Gameday(BandEvent):
    
    def __init__(self, name, time, doNotify, doCheckin, otherTeam, isHome, isTimeAnnounced, otherMascot):
        super(name, time, doNotify, doCheckin)
        self.otherTeam = otherTeam
        self.isHome = isHome
        self.isTimeAnnounced = isTimeAnnounced
        self.otherMascot = otherMascot
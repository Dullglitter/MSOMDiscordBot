from BandEvent import BandEvent

class Gameday(BandEvent):
    
    def __init__(self, name:str, time, doNotify, doCheckin, otherTeam: str, isHome, isTimeAnnounced, otherMascot: str):
        super(name, time, doNotify, doCheckin)
        self.otherTeam = otherTeam
        self.isHome = bool(isHome)
        self.isTimeAnnounced = bool(isTimeAnnounced)
        self.otherMascot = otherMascot
        
        
    def toCSVrow(self):
        return 'gameday,' + super.internaltoCSVrow(self) + ',{},{},{},{}'.format(
            self.otherTeam, str(self.isHome), str(self.isTimeAnnounced), self.otherMascot)
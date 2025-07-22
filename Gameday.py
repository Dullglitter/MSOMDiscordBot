from BandEvent import BandEvent

class Gameday(BandEvent):
    
    def __init__(self, name:str, time, doNotify, doCheckin, otherTeam: str, isHome, isTimeAnnounced, otherMascot: str):
        super().__init__(name, time, doNotify, doCheckin)
        self.otherTeam = otherTeam
        self.isHome = bool(isHome)
        self.isTimeAnnounced = bool(isTimeAnnounced)
        self.otherMascot = otherMascot
        
        
    def toCSVrow(self):
        return 'gameday,' + super().internaltoCSVrow() + ',{},{},{},{}'.format(
            self.otherTeam, str(self.isHome), str(self.isTimeAnnounced), self.otherMascot)
        
        
    def __str__(self):
        location = 'UMD' if self.isHome else self.otherTeam
        time = 'with time finalized' if self.isTimeAnnounced else 'with time not announced'
        return 'Game' + super().internal_str() + ' against {} at {} {}, beat the {}!'.format(self.otherTeam, location, time, self.otherMascot)
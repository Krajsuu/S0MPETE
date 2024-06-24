class CSong :
    def __init__(self, title , arists, album, gentre) :
        self.title = title
        self.artist = arists
        self.album = album
        self.gentre = gentre
    def __str__(self) :
        return f'{self.title} by {self.artist} from {self.album}'
    def getArtist(self) :
        return self.artist
    def getTitle(self) :
        return self.title
    def getAlbum(self) :
        return self.album
    def getGentre(self) :
        return self.gentre

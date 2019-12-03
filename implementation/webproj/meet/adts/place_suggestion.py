# -*- encoding: utf-8 -*-


class PlaceSuggestion:
    def __init__(self, lang, lat, long, nm, abst, plc):
        self.language: str = lang
        self.latitude: float = lat
        self.longitude: float = long
        self.name: str = nm
        self.abstract: str = abst
        self.url: str = plc

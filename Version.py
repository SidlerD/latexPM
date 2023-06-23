from dateutil.parser import parse

class Version:
    def __init__(self, version = None) -> None:
        if(version == None):
            self.date = None
            self.number = None
        else:
            date, number = parse_version(version)
            self.date = date
            self.number = number



    def __eq__(self, other) -> bool:
        # TODO: Definitely need to test this     
        if other == None and self.date == None and self.number == None:
            return True
        if(type(other) != Version):
            return False
        if self.date != other.date and self.date and other.date: #Diff dates, both not none
            return False
        if self.number != other.number and self.number and other.number: #Diff numbers, both not none
            return False
        return True
    
    def __hash__(self) -> int:
        return hash((self.date, self.number))
    
    def __repr__(self) -> str:
        return f"v({self.date}, {self.number})"
    
def parse_version(version) -> tuple[str, str]:
    if type(version) == dict and 'date' in version and 'number' in version:
        date = parse(version['date']) if version["date"] else None
        number = version['number'] if version['number'] else None
        return date, number
    if version == "" or version == None:
        return Version()
    
    raise NotImplementedError("Cant convert string to Version yet")

    return date, number
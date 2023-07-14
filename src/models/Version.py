from datetime import datetime
import re
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
        # TODO: What about case where both have one field the same, and for the other field one has None while the other has something?  
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
    
def parse_version(version) -> tuple[datetime, str]:
    if type(version) == dict and 'date' in version and 'number' in version: # CTAN version field
        date = parse(version['date']) if version["date"] else None
        number = version['number'] if version['number'] else None
        return date, number
    if version == "" or version == None:
        return None, None
    
    if(type(version) == str): # e.g. '2005/05/09 v0.3 1, 2, many: numbersets  (ums)'
        # Try to extract date from string
        # TODO: Check if dates are sometimes present with dot-notation. If so, figure out way to catch them without catching version like v12.10.21
        date_pattern = r"\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2}"
        date_match = re.search(date_pattern, version)
        date = date_match.group() if date_match else None

        # Assumes version number is followed by a space
        number_pattern = r"\d*\.\d*(\.\d+)?-?([a-z]+(?=\s))?"
        single_number_pattern = r"(?<=v)\d" # FIXME: Problem: Trying to capture single-digit versions without leading v would capture numbers in date

        number_match = re.search(number_pattern, version)
        if number_match:
            number = number_match.group()
        else:
            single_number_match = re.search(single_number_pattern, version)
            number = single_number_match.group() if single_number_match else None
            
        return parse(date) if date else None, number
    
    raise TypeError(f"Cannot parse {type(version)} {version}")
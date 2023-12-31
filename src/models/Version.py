import re
from datetime import date

from dateutil.parser import parse


class Version:
    """Class that models the version of a Package, made of a date and a number
    """
    def __init__(self, version: str | dict | None = None) -> None:
        """Class that models the version of a Package

        Args:
            version (str|dict|None, optional): Object describing version. If dict, needs keys 'date' and 'number
        """
        if version is None:
            self.date = None
            self.number = None
        else:
            date, number = parse_version(version)
            self.date = date
            self.number = number

    def __bool__(self) -> bool:
        return bool(self.date and self.number)

    def __eq__(self, other) -> bool:
        # TODO: What about case where both have one field the same,
        # and for the other field one has None while the other has something?
        if other == None and self.date is None and self.number is None:  # noqa: E711
            return True
        if not isinstance(other, Version):
            return False
        if self.date != other.date and self.date and other.date:  # Diff dates, both not none
            return False
        if self.number != other.number and self.number and other.number:  # Diff numbers, both not none
            return False
        if self.number == other.number and self.date == other.date:
            return True

        return False

    def __hash__(self) -> int:
        return hash((self.date, self.number))

    def __repr__(self) -> str:
        if not self.date and not self.number:
            return ""
        if self.date and not self.number:
            return f"({self.date})"
        elif self.number and not self.date:
            return f"({self.number})"

        return f"({self.date}, {self.number})"


def parse_version(version) -> tuple[date, str]:
    """Parse a version from the provided input

    Args:
        version (str|dict|None): Version to parse. If dict, needs keys 'date' and 'number

    Raises:
        TypeError: All attempts at parsing version failed

    Returns:
        tuple[date, str]: date and number components of the version
    """
    if isinstance(version, dict) and 'date' in version and 'number' in version:  # CTAN version field
        date = parse(version['date']).date() if version["date"] else None
        number = version['number'] if version['number'] else None
        return date, number
    if version == "" or version is None:
        return None, None

    if isinstance(version, str):  # e.g. '2005/05/09 v0.3 1, 2, many: numbersets  (ums)'
        # Try to extract date from string
        date_pattern = r"\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2}"
        date_match = re.search(date_pattern, version)
        date = date_match.group() if date_match else None

        # Assumes version number is followed by a space
        number_pattern = r"\d+\.\d+(?:\.\d+)?-?(?:[a-z0-9])*\b"
        single_number_pattern = r"(?<=v)\d"

        number_match = re.search(number_pattern, version)
        if number_match:
            number = number_match.group()
        else:
            single_number_match = re.search(single_number_pattern, version)
            number = single_number_match.group() if single_number_match else None

        return parse(date).date() if date else None, number

    raise TypeError(f"Cannot parse {type(version)} {version}")

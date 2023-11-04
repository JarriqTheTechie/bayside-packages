import json
import pprint
import re


class String:
    def __init__(self):
        self.string = ""

    @classmethod
    def of(self, string: str):
        """
        Instantiate a new String object.
        :param string:
        :return:
        """
        obj = self()
        obj.string = string
        return obj

    def is_alpha(self):
        """
        Check if the string contains only alphabetic characters.
        :return:
        """
        return self.string.isalpha()

    def is_alpha_numeric(self):
        """
        Check if the string contains only alphanumeric characters.
        :return:
        """
        return self.string.isalnum()

    def is_alpha_dash(self):
        """
        Check if the string contains only alpha-numeric characters, dashes, and underscores.
        :return:
        """
        return self.string.replace("-", "").replace("_", "").isalpha()

    def is_email(self):
        """
        Check if the string is an email.
        :return:
        """
        return self.matches_pattern(r"^[^@]+@[^@]+\.[^@]+$")

    def is_ip(self):
        """
        Check if the string is an ip address.
        :return:
        """
        return self.matches_pattern(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")

    def is_ipv4(self):
        """
        Check if the string is an ipv4 address.
        :return:
        """
        return self.matches_pattern(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")

    def is_ipv6(self):
        """
        Check if the string is an ipv6 address.
        :return:
        """
        return self.matches_pattern(r"^([0-9a-f]{1,4}:){7}[0-9a-f]{1,4}$")
    def is_mac_address(self):
        """
        Check if the string is a mac address.
        :return:
        """
        return self.matches_pattern(r"^([0-9a-f]{2}:){5}[0-9a-f]{2}$")

    def after(self, after: str):
        """
        Get the string after a substring.
        :param after:
        :return:
        """
        self.string = self.string.split(after)[1]
        return self

    def after_last(self, after):
        """
        Get the string after the last occurrence of a substring.
        :param after:
        :return:
        """
        self.string = self.string.split(after)[-1]
        return self

    def ascii(self):
        """
        Transliterate a UTF-8 value to ASCII.
        :return:
        """
        self.string = str(self.string).encode("ascii", "ignore").decode("ascii")
        return self

    def before(self, before):
        """
        Get the string before a substring.
        :param before:
        :return:
        """
        self.string = self.string.split(before)[0]
        return self

    def before_last(self, before):
        """
        Get the string before the last occurrence of a substring.
        :param before:
        :return:
        """
        self.string = self.string.split(before)[-2]
        return self

    def between(self, before, after):
        """
        Get the string between two substrings.
        :param before:
        :param after:
        :return:
        """
        self.string = self.after(before).before(after).string
        return self

    def between_first(self, before, after):
        """
        Get the string between the first occurrence of two substrings.
        :param before:
        :param after:
        :return:
        """
        self.string = self.after(before).before(after).string
        return self

    def between_last(self, before, after):
        """
        Get the string between the last occurrence of two substrings.
        :param before:
        :param after:
        :return:
        """
        self.string = self.after_last(before).before_last(after).string
        return self

    def camel(self):
        """
        Convert the string to camel case.
        :return:
        """
        self.string = self.string.title().replace(" ", "").replace("_", "").replace("-", "")
        first_char = self.string[0].lower()
        self.string = first_char + self.string[1:]
        return self

    def contains(self, substring: str | list):
        """
        Check if the string contains a substring.
        :param substring:
        :return:
        """
        if isinstance(substring, list):
            for sub in substring:
                if sub in self.string:
                    return True
            return False
        return substring in self.string

    def contains_all(self, substring: list):
        """
        Check if the string contains all substrings.
        :param substring:
        :return:
        """
        for sub in substring:
            if sub not in self.string:
                return False
        return True

    def ends_with(self, substring: str | list):
        """
        Check if the string ends with a substring.
        :param substring:
        :return:
        """
        if isinstance(substring, list):
            for sub in substring:
                if self.string.endswith(sub):
                    return True
            return False
        return self.string.endswith(substring)

    def finish(self, substring):
        """
        Append to the string if it does not end with a substring.
        :param substring:
        :return:
        """
        if self.string.endswith(substring):
            return self
        self.string = self.string + substring
        return self

    def headline(self):
        """
        Convert the string to headline case.
        :return:
        """
        self.string = self.string.title().replace("_", " ").replace("-", " ")
        return self

    def matches_pattern(self, pattern):
        """
        Check if the string matches a pattern.
        :param pattern:
        :return:
        """
        if re.match(pattern, self.string):
            return True
        return False

    def is_ascii(self):
        """
        Check if the string is ascii.
        :return:
        """
        return all(ord(char) < 128 for char in self.string)

    def is_json(self):
        """
        Check if the string is json.
        :return:
        """
        try:
            json.loads(self.string)
        except ValueError:
            return False
        return True

    def is_url(self):
        """
        Check if the string is a url.
        :return:
        """
        return self.matches_pattern(r"^https?://[^ ]+$")

    def is_ulid(self):
        """
        Check if the string is a ulid.
        :return:
        """
        return self.matches_pattern(r"^[0-7][0-9A-HJKMNP-TV-Z]{25}$")

    def is_uuid(self):
        """
        Check if the string is a uuid.
        :return:
        """
        return self.matches_pattern(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")

    def kebab(self):
        """
        Convert the string to kebab case.
        :return:
        """
        self.string = '-'.join(
            re.sub(r"(\s|_|-)+", " ",
                   re.sub(r"[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+",
                          lambda mo: ' ' + mo.group(0).lower(), self.string)).split())
        return self

    def lcfirst(self):
        """
        Make a string's first character lowercase.
        :return:
        """
        self.string = self.string[:1].lower() + self.string[1:]
        return self

    def length(self):
        """
        Get the length of the string.
        :return:
        """
        return len(self.string)

    def limit(self, limit, end="..."):
        """
        Limit the number of characters in a string.
        :param limit:
        :param end:
        :return:
        """
        if len(self.string) <= limit:
            return self
        self.string = self.string[:limit] + end
        return self

    def lower(self):
        """
        Convert the given string to lower-case.
        :return:
        """
        self.string = self.string.lower()
        return self

    @classmethod
    def ordered_uuid(self):
        """
        Generate a UUID that is ordered by time.
        :return:
        """
        import uuid
        return str(uuid.uuid1())

    def pad_left(self, length, pad=" "):
        """
        Pad both sides of a string with another.
        :param length:
        :param pad:
        :return:
        """
        if len(self.string) >= length:
            return self
        self.string = f"{pad * (length - len(self.string)) + self.string}"[-length:]
        return self

    def pad_right(self, length, pad=" "):
        """
        Pad both sides of a string with another.
        :param length:
        :param pad:
        :return:
        """
        if len(self.string) >= length:
            return self
        self.string = f"{self.string + pad * (length - len(self.string))}"[:length]
        return self

    def pad_both(self, length, pad=" "):
        """
        Pad both sides of a string with another.
        :param length:
        :param pad:
        :return:
        """
        if len(self.string) >= length:
            return self
        pad_length = length - len(self.string)
        pad_left = pad * (pad_length // 2)
        pad_right = pad * (pad_length - len(pad_left))
        self.string = pad_left + self.string + pad_right
        return self

    @classmethod
    def password(cls, length=32):
        """
        Generate a random password.
        :param length:
        :return:
        """
        import random
        import string
        password = ""
        while len(password) < length:
            password += random.choice(string.ascii_lowercase)
            password += random.choice(string.ascii_uppercase)
            password += random.choice(string.digits)
            password += random.choice(string.punctuation)
        return password[:length]

    def position(self, substring):
        """
        Find the position of the first occurrence of a substring in a string.
        :param substring:
        :return:
        """
        return self.string.index(substring)

    @classmethod
    def random(cls, length=32):
        """
        Generate a more truly "random" alpha-numeric string.
        :param length:
        :return:
        """
        import random
        import string
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

    def remove(self, removeable: str | list, case_sensitive=False):
        """
        Remove part of a string from the beginning or end.
        :param removeable:
        :param case_sensitive:
        :return:
        """
        if isinstance(removeable, list):
            for remove in removeable:
                string = self.remove(remove, case_sensitive)
            return self

        if case_sensitive is False:
            self.string = self.string.replace(removeable.lower(), "")
            self.string = self.string.replace(removeable.upper(), "")
            self.string = self.string.replace(removeable.title(), "")
        else:
            self.string = self.string.replace(removeable, "")
        return self

    def repeat(self, multiplier):
        """
        Repeat the string n times.
        :param multiplier:
        :return:
        """
        self.string = self.string * multiplier
        return self

    def replace(self, search, replace):
        """
        Replace all occurrences of the search string with the replacement string.
        :param search:
        :param replace:
        :return:
        """
        self.string = self.string.replace(search, replace)
        return self

    def replace_first(self, search, replace):
        """
        Replace the first occurrence of a given value in the string.
        :param search:
        :param replace:
        :return:
        """
        self.string = self.string.replace(search, replace, 1)
        return self

    def replace_last(self, search, replace):
        """
        Replace the last occurrence of a given value in the string.
        :param search:
        :param replace:
        :return:
        """
        self.string = self.string[::-1].replace(search[::-1], replace[::-1], 1)[::-1]
        return self

    def replace_matches(self, pattern, replace):
        """
        Replace a given pattern in the string sequentially with an array.
        :param pattern:
        :param replace:
        :return:
        """
        self.string = re.sub(pattern, replace, self.string)
        return self

    def replace_start(self, search, replace):
        """
        Replace the first occurrence of a given value in the string.
        :param search:
        :param replace:
        :return:
        """
        if self.string.startswith(search):
            self.string = replace + self.string[len(search):]
            return self
        return self

    def replace_end(self, search, replace):
        """
        Replace the last occurrence of a given value in the string.
        :param search:
        :param replace:
        :return:
        """
        if self.string.endswith(search):
            self.string = self.string[:-len(search)] + replace
            return self
        return self

    def reverse(self):
        """
        Reverse the string.
        :return:
        """
        self.string = self.string[::-1]
        return self

    def replace_array(self, items: list, replace):
        """
        Replace a given value in the string sequentially with an array.
        :param items:
        :param replace:
        :return:
        """
        for item in items:
            self.string = self.string.replace(replace, item, 1)
        return self

    def slug(self):
        """
        Generate a URL friendly "slug" from a given string.
        :return:
        """
        self.string = self.kebab()
        return self

    def snake(self):
        """
        Convert a string to snake case.
        :return:
        """
        self.string = re.sub(r"(\s|_|-)+", "_", re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", self.string)).lower()
        return self

    def squish(self):
        """
        Remove all spaces from the string.
        :return:
        """
        self.string = re.sub(r"(\s|_|-)+", " ", self.string).strip()
        return self

    def start(self, start):
        """
        Begin a string with a single instance of a given value.
        :param start:
        :return:
        """
        if self.string.startswith(start):
            return self
        self.string = start + self.string
        return self

    def starts_with(self, start):
        """
        Determine if a given string starts with a given substring.
        :param start:
        :return:
        """
        return self.string.startswith(start)

    def studly(self):
        """
        Convert a value to studly caps case.
        :return:
        """
        self.string = self.string.title().replace("_", "").replace("-", "")
        return self

    def substr(self, start, length=None):
        """
        Returns the portion of string specified by the start and length parameters.
        :param start:
        :param length:
        :return:
        """
        if length is None:
            self.string = self.string[start:]
            return self
        self.string = self.string[start:start + length]
        return self

    def substr_count(self, substring):
        """
        Count the number of substring occurrences.
        :param substring:
        :return:
        """
        return self.string.count(substring)

    def swap(self, replace: dict):
        """
        Swap the given value for the string.
        :param replace:
        :return:
        """
        for search, replace in replace.items():
            self.string = self.string.replace(search, replace)
        return self

    def take(self, length):
        """
        Returns the portion of string specified by the start and length parameters.
        :param length:
        :return:
        """
        self.string = self.string[:length]
        return self

    def title(self):
        """
        Convert the given string to title case.
        :return:
        """
        self.string.title()
        return self

    def uc_first(self):
        """
        Make a string's first character uppercase.
        :return:
        """
        self.string = self.string[:1].upper() + self.string[1:]
        return self

    def upper(self):
        """
        Convert the given string to upper-case.
        :return:
        """
        self.string = self.string.upper()
        return self

    def ulid(self):
        # Todo: implement ulid
        raise NotImplementedError

    @classmethod
    def uuid(cls):
        """
        Generate a UUID (version 4).
        :return:
        """
        import uuid
        return str(uuid.uuid4())

    def word_count(self):
        """
        Get the number of words a string contains.
        :return:
        """
        return len(self.string.split())

    def word_wrap(self, character_count=20, break_character="<br/>\n"):
        """
        Wrap a string into a given number of characters.
        :param character_count:
        :param break_character:
        :return:
        """
        import textwrap
        self.string = textwrap.fill(self.string, character_count).replace("\n", break_character)
        return self

    def words(self, limit, end="..."):
        """
        Limit the number of words in a string.
        :param limit:
        :param end:
        :return:
        """
        self.string = " ".join(self.string.split()[:limit]) + end
        return self

    def wrap(self, before, after=None):
        """
        Wrap the given string with the given value.
        :param before:
        :param after:
        :return:
        """
        if after:
            self.string = before + self.string + after
            return self
        self.string = before + self.string + before
        return self

    def append(self, string):
        """
        Append the given string to the string.
        :param string:
        :return:
        """
        self.string += string
        return self

    def prepend(self, string):
        """
        Prepend the given string to the string.
        :param string:
        :return:
        """
        self.string = string + self.string
        return self

    def trim(self, characters=None):
        """
        Trim the string of the given characters.
        :param characters:
        :return:
        """
        if characters:
            self.string = self.string.strip(characters)
            return self
        self.string = self.string.strip()
        return self

    def trim_end(self, characters=None):
        """
        Trim the string from the end of the given characters.
        :param characters:
        :return:
        """
        if characters:
            self.string = self.string.rstrip(characters)
            return self
        self.string = self.string.rstrip()
        return self

    def trim_start(self, characters=None):
        """
        Trim the string from the start of the given characters.
        :param characters:
        :return:
        """
        if characters:
            self.string = self.string.lstrip(characters)
            return self
        self.string = self.string.lstrip()
        return self

    def trim_slashes(self):
        """
        Trim the string of slashes.
        :return:
        """
        self.string = self.string.strip("/")
        return self

    def exactly(self, string):
        """
        Determine if the given string matches the string.
        :param string:
        :return:
        """
        return self.string == string

    def explode(self, delimiter):
        """
        Explode the string into an array.
        :param delimiter:
        :return:
        """
        return self.string.split(delimiter)

    def is_(self, pattern):
        """
        Determine if the given string matches the given pattern.
        :param pattern:
        :return:
        """
        return self.matches_pattern(pattern)

    def is_empty(self):
        """
        Determine if the string is empty.
        :return:
        """
        return self.string == ""

    def is_not_empty(self):
        """
        Determine if the string is not empty.
        :return:
        """
        return self.string != ""

    def ltrim(self, characters=None):
        """
        Trim the string from the start of the given characters.
        :param characters:
        :return:
        """
        return self.trim_start(characters)

    def rtrim(self, characters=None):
        """
        Trim the string from the end of the given characters.
        :param characters:
        :return:
        """
        return self.trim_end(characters)

    def new_line(self):
        """
        Append a new line to the string.
        :return:
        """
        self.string += "\n"
        return self

    def pipe(self, callback):
        """
        Pass the string to the given callback and return the result.
        :param callback:
        :return:
        """
        self.string = callback(self.string)
        return self

    def tap(self, callback):
        """
        Pass the string to the given callback without modification.
        :param callback:
        :return:
        """
        callback(self.string)
        return self

    def when(self, condition, callback):
        """
        Apply the given callback if the given condition is true.
        :param condition:
        :param callback:
        :return:
        """
        if condition:
            self.string = callback(self.string)
        return self

    def when_contains(self, substring, callback):
        """
        Apply the given callback if the string contains the given substring.
        :param substring:
        :param callback:
        :return:
        """
        if self.contains(substring):
            self.string = callback(self.string)
        return self

    def when_contains_all(self, substrings: list, callback):
        """
        Apply the given callback if the string contains all of the given substrings.
        :param substrings:
        :param callback:
        :return:
        """
        if self.contains_all(substrings):
            self.string = callback(self.string)
        return self

    def when_empty(self, callback):
        """
        Apply the given callback if the string is empty.
        :param callback:
        :return:
        """
        if self.is_empty():
            self.string = callback(self.string)
        return self

    def when_not_empty(self, callback):
        """
        Apply the given callback if the string is not empty.
        :param callback:
        :return:
        """
        if self.is_not_empty():
            self.string = callback(self.string)
        return self

    def when_starts_with(self, substring, callback):
        """
        Apply the given callback if the string starts with the given substring.
        :param substring:
        :param callback:
        :return:
        """
        if self.starts_with(substring):
            self.string = callback(self.string)
        return self

    def when_ends_with(self, substring, callback):
        """
        Apply the given callback if the string ends with the given substring.
        :param substring:
        :param callback:
        :return:
        """
        if self.ends_with(substring):
            self.string = callback(self.string)
        return self

    def when_exactly(self, string, callback):
        """
        Apply the given callback if the string exactly matches the given string.
        :param string:
        :param callback:
        :return:
        """
        if self.exactly(string):
            self.string = callback(self.string)
        return self

    def when_not_exactly(self, string, callback):
        """
        Apply the given callback if the string does not exactly match the given string.
        :param string:
        :param callback:
        :return:
        """
        if not self.exactly(string):
            self.string = callback(self.string)
        return self

    def when_is(self, pattern, callback):
        """
        Apply the given callback if the string matches the given pattern.
        :param pattern:
        :param callback:
        :return:
        """
        if self.is_(pattern):
            self.string = callback(self.string)
        return self

    def when_is_ascii(self, callback):
        """
        Apply the given callback if the string is ASCII.
        :param callback:
        :return:
        """
        if self.is_ascii():
            self.string = callback(self.string)
        return self

    def when_is_ulid(self, callback):
        """
        Apply the given callback if the string is a ULID.
        :param callback:
        :return:
        """
        if self.is_ulid():
            self.string = callback(self.string)
        return self

    def when_is_uuid(self, callback):
        """
        Apply the given callback if the string is a UUID.
        :param callback:
        :return:
        """
        if self.is_uuid():
            self.string = callback(self.string)
        return self

    def __str__(self):
        """
        Return the string.
        :return:
        """
        return self.string

    def __repr__(self):
        """
        Return the string.
        :return:
        """
        return self.string
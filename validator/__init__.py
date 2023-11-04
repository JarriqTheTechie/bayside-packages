import pprint
import re

import pendulum
from helpers.str import String
from flask_requester import requester, Session



class validator(object):
    def __init__(self):
        self.errors_ = None
        self.excluded = None

    def all(self):
        return self.errors_

    def any(self):
        return len(self.errors_) > 0

    def errors(self):
        return self.errors_

    def fails(self):
        return self.any()

    def old(self):
        return self.data


    @classmethod
    def of(self, data: dict):
        """
        Instantiate a new String object.
        :param string:
        :return:
        """
        obj = self()
        obj.data = data
        obj.errors_: dict[str, list[str]] = {}
        for key, value in data.items():
            obj.errors_[key] = []
        obj.excluded = []
        obj.messages = {}
        obj.rules = {}
        obj.messages = {}
        obj.custom_messages = {}
        return obj

    def get_modifiers(self, rule: str) -> tuple | None:
        if ":" not in rule:
            return None
        else:
            modifiers = tuple(rule.split(":")[1:])
            if "," in modifiers[0]:
                modifiers = tuple(modifiers[0].split(","))
        return modifiers

    def validate(self, rules: dict[str, str]):
        for key, value in self.data.items():
            current_key, current_value, rule_for_current_key = key, value, rules.get(key)
            if rule_for_current_key:
                if isinstance(rule_for_current_key, str):
                    rules_for_current_key = rule_for_current_key.split("|")
                    if len(rules_for_current_key) == 1:
                        rule_for_current_key = rules_for_current_key[0]
                        modifiers = self.get_modifiers(rule_for_current_key)
                        if modifiers:
                            rule_for_current_key = rule_for_current_key.split(":")[0]
                        # print(f"RULE FOR CURRENT KEY [{key}]: {rule_for_current_key} with modifiers: {modifiers}")

                        # write rules here
                        if rule_for_current_key == "accepted":
                            if current_value not in ["yes", "on", "1", "true"]:
                                self.errors_[key].append("The :attribute must be accepted.")

                        if rule_for_current_key == "active_url":
                            import socket
                            try:
                                socket.gethostbyaddr(current_value)[0]
                            except:
                                self.errors_[key].append("The :attribute is not a valid URL.")

                        if rule_for_current_key == "after":
                            modifier_date = pendulum.parse(modifiers[0], exact=True, tz="UTC")
                            try:
                                current_value_date = pendulum.parse(current_value, exact=True, tz="UTC")
                            except:
                                self.errors_[key].append(f"The :attribute must be a valid date.")
                                continue
                            date_diff = current_value_date.diff_for_humans(modifier_date)
                            if "after" not in date_diff:
                                self.errors_[key].append(f"The :attribute must be a date after {modifiers[0]}.")

                        if rule_for_current_key == "after_or_equal":
                            modifier_date = pendulum.parse(modifiers[0], exact=True, tz="UTC")
                            try:
                                current_value_date = pendulum.parse(current_value, exact=True, tz="UTC")
                            except:
                                self.errors_[key].append(f"The :attribute must be a valid date.")
                                continue
                            date_diff = current_value_date.diff_for_humans(modifier_date, absolute=True)
                            if "a few seconds" not in date_diff and "after" not in date_diff:
                                self.errors_[key].append(
                                    f"The :attribute must be a date after or equal to {modifiers[0]}.")

                        if rule_for_current_key == "alpha":
                            if not String.of(current_value).ascii().is_alpha():
                                self.errors_[key].append("The :attribute may only contain letters.")

                        if rule_for_current_key == "alpha_dash":
                            if not String.of(current_value).ascii().is_alpha_dash():
                                self.errors_[key].append(
                                    "The :attribute may only contain letters, numbers, dashes and underscores.")

                        if rule_for_current_key == "alpha_num":
                            if not String.of(current_value).ascii().is_alpha_numeric():
                                self.errors_[key].append("The :attribute may only contain letters and numbers.")

                        if rule_for_current_key == "ascii":
                            if not String.of(current_value).ascii().is_ascii():
                                self.errors_[key].append("The :attribute may only contain ASCII characters.")

                        if rule_for_current_key == "bail":
                            continue

                        if rule_for_current_key == "before":
                            modifier_date = pendulum.parse(modifiers[0], exact=True, tz="UTC")
                            current_value_date = pendulum.parse(current_value, exact=True, tz="UTC")
                            date_diff = current_value_date.diff_for_humans(modifier_date)
                            if "before" not in date_diff:
                                self.errors_[key].append(f"The :attribute must be a date before {modifiers[0]}.")

                        if rule_for_current_key == "before_or_equal":
                            modifier_date = pendulum.parse(modifiers[0], exact=True, tz="UTC")
                            current_value_date = pendulum.parse(current_value, exact=True, tz="UTC")
                            date_diff = current_value_date.diff_for_humans(modifier_date, absolute=True)
                            if "a few seconds" not in date_diff and "before" not in date_diff:
                                self.errors_[key].append(
                                    f"The :attribute must be a date before or equal to {modifiers[0]}.")

                        if rule_for_current_key == "between":
                            if not len(modifiers) == 2:
                                raise Exception("The between rule requires two modifiers.")
                            start_val = modifiers[0]
                            end_val = modifiers[1]
                            if isinstance(current_value, str) and isinstance(current_value, str):
                                # if String.of(current_value).length() is between start_val and end_val (inclusive) then continue else add error
                                if not String.of(current_value).length() in range(int(start_val), int(end_val) + 1):
                                    self.errors_[key].append(
                                        f"The :attribute must be between {start_val} and {end_val}.")
                            elif isinstance(current_value, int) and isinstance(current_value, int):
                                # if current_value is between start_val and end_val (inclusive) then continue else add error
                                if not current_value in range(int(start_val), int(end_val) + 1):
                                    self.errors_[key].append(
                                        f"The :attribute must be between {start_val} and {end_val}.")
                            elif isinstance(current_value, list):
                                # if len(current_value) is between start_val and end_val (inclusive) then continue else add error
                                if not len(current_value) in range(int(start_val), int(end_val) + 1):
                                    self.errors_[key].append(
                                        f"The :attribute must have between {start_val} and {end_val} items.")
                            elif isinstance(current_value, dict):
                                # if len(current_value) is between start_val and end_val (inclusive) then continue else add error
                                if not len(current_value) in range(int(start_val), int(end_val) + 1):
                                    self.errors_[key].append(
                                        f"The :attribute must have between {start_val} and {end_val} items.")

                        if rule_for_current_key == "boolean":
                            match current_value:
                                case "true":
                                    pass
                                case "false":
                                    pass
                                case "1":
                                    pass
                                case "0":
                                    pass
                                case 1:
                                    pass
                                case 0:
                                    pass
                                case True:
                                    pass
                                case False:
                                    pass
                                case _:
                                    self.errors_[key].append("The :attribute must be a boolean.")

                        if rule_for_current_key == "confirmed":
                            if not current_value == self.data.get(key + "_confirmation"):
                                self.errors_[key].append("The :attribute confirmation is not present.")

                        if rule_for_current_key == "current_password":
                            # TODO: Implement this rule
                            raise NotImplementedError("The current_password rule is not yet implemented.")

                        if rule_for_current_key == "date":
                            try:
                                pendulum.parse(current_value, exact=True, tz="UTC")
                            except:
                                self.errors_[key].append("The :attribute is not a valid date.")

                        if rule_for_current_key == "date_equals":
                            try:
                                current_value_date = pendulum.parse(current_value, exact=True, tz="UTC")
                                modifier_date = pendulum.parse(modifiers[0], exact=True, tz="UTC")
                                if not current_value_date == modifier_date:
                                    self.errors_[key].append(f"The :attribute must be a date equal to {modifiers[0]}.")
                            except:
                                self.errors_[key].append("The :attribute is not a valid date.")

                        if rule_for_current_key == "date_format":
                            # TODO: Test this rule
                            try:
                                pendulum.parse(current_value, exact=True, tz="UTC", formatter=modifiers[0])
                            except:
                                self.errors_[key].append(f"The :attribute does not match the format {modifiers[0]}.")

                        if rule_for_current_key == "decimal":
                            # TODO: Implement this rule
                            raise NotImplementedError("The decimal rule is not yet implemented.")

                        if rule_for_current_key == "declined":
                            match current_value:
                                case "no":
                                    pass
                                case "n":
                                    pass
                                case "false":
                                    pass
                                case "0":
                                    pass
                                case 0:
                                    pass
                                case False:
                                    pass
                                case "off":
                                    pass
                                case "disabled":
                                    pass
                                case _:
                                    self.errors_[key].append("The :attribute must be declined.")

                        if rule_for_current_key == "different":
                            if not current_value == self.data.get(modifiers[0]):
                                self.errors_[key].append(f"The :attribute and {modifiers[0]} must be different.")

                        if rule_for_current_key == "digits":
                            if isinstance(current_value, int):
                                if not len(str(current_value)) == int(modifiers[0]):
                                    self.errors_[key].append(f"The :attribute must be {modifiers[0]} digits.")

                        if rule_for_current_key == "digits_between":
                            if isinstance(current_value, int):
                                start_val = modifiers[0]
                                end_val = modifiers[1]
                                if not len(str(current_value)) in range(int(start_val), int(end_val) + 1):
                                    self.errors_[key].append(
                                        f"The :attribute must be between {start_val} and {end_val} digits.")

                        if rule_for_current_key == "dimensions":
                            # TODO: Implement this rule
                            raise NotImplementedError("The dimensions rule is not yet implemented.")

                        if rule_for_current_key == "distinct":
                            if isinstance(current_value, (list, dict)):
                                # Ensure that all items in the list are unique
                                if not len(current_value) == len(set(current_value)):
                                    self.errors_[key].append("The :attribute must be unique.")

                        if rule_for_current_key == "doesnt_start_with":
                            for modifier in modifiers:
                                if modifier:
                                    if current_value.startswith(modifier):
                                        self.errors_[key].append(f"The :attribute must not start with {modifier}.")

                        if rule_for_current_key == "doesnt_end_with":
                            for modifier in modifiers:
                                if modifier:
                                    if current_value.endswith(modifier):
                                        self.errors_[key].append(f"The :attribute must not end with {modifier}.")

                        if rule_for_current_key == "email":
                            # TODO: Add modifiers for email validation. Currently checks for valid email address format.
                            #  I think we should also check if the domain exists.
                            if not String.of(current_value).is_email():
                                self.errors_[key].append("The :attribute must be a valid email address.")

                        if rule_for_current_key == "ends_with":
                            for modifier in modifiers:
                                if modifier:
                                    if not current_value.endswith(modifier):
                                        self.errors_[key].append(f"The :attribute must end with {modifier}.")

                        if rule_for_current_key == "exclude":
                            self.excluded.append(key)

                        if rule_for_current_key == "exclude_if":
                            if self.data.get(current_key) == self.data.get(modifiers[0]):
                                self.excluded.append(key)

                        if rule_for_current_key == "exclude_unless":
                            if not self.data.get(current_key) == self.data.get(modifiers[0]):
                                self.excluded.append(key)

                        if rule_for_current_key == "exclude_with":
                            if self.data.get(current_key) in modifiers:
                                self.excluded.append(key)

                        if rule_for_current_key == "exclude_without":
                            if not self.data.get(current_key) in modifiers:
                                self.excluded.append(key)

                        if rule_for_current_key == "exists":
                            # TODO: Implement this rule
                            raise NotImplementedError("The exists rule is not yet implemented.")

                        if rule_for_current_key == "file":
                            # TODO: Implement this rule
                            raise NotImplementedError("The file rule is not yet implemented.")

                        if rule_for_current_key == "filled":
                            if not current_value:
                                self.errors_[key].append("The :attribute must be filled.")

                        if rule_for_current_key == "gt":
                            if isinstance(current_value, str) and isinstance(current_value, str):
                                # if String.of(current_value).length() is greater than modifiers[0] then continue else add error
                                if not String.of(current_value).length() > int(modifiers[0]):
                                    self.errors_[key].append(f"The :attribute must be greater than {modifiers[0]}.")
                            elif isinstance(current_value, int) and isinstance(current_value, int):
                                # if current_value is greater than modifiers[0] then continue else add error
                                if not current_value > int(modifiers[0]):
                                    self.errors_[key].append(f"The :attribute must be greater than {modifiers[0]}.")
                            elif isinstance(current_value, list):
                                # if len(current_value) is greater than modifiers[0] then continue else add error
                                if not len(current_value) > int(modifiers[0]):
                                    self.errors_[key].append(f"The :attribute must be greater than {modifiers[0]}.")
                            elif isinstance(current_value, dict):
                                # if len(current_value) is greater than modifiers[0] then continue else add error
                                if not len(current_value) > int(modifiers[0]):
                                    self.errors_[key].append(f"The :attribute must be greater than {modifiers[0]}.")

                        if rule_for_current_key == "gte":
                            if isinstance(current_value, str) and isinstance(current_value, str):
                                if not String.of(current_value).length() >= int(modifiers[0]):
                                    self.errors_[key].append(f"The :attribute must be greater than {modifiers[0]}.")
                            elif isinstance(current_value, int) and isinstance(current_value, int):
                                if not current_value >= int(modifiers[0]):
                                    self.errors_[key].append(f"The :attribute must be greater than {modifiers[0]}.")
                            elif isinstance(current_value, list):
                                if not len(current_value) >= int(modifiers[0]):
                                    self.errors_[key].append(f"The :attribute must be greater than {modifiers[0]}.")
                            elif isinstance(current_value, dict):
                                if not len(current_value) >= int(modifiers[0]):
                                    self.errors_[key].append(f"The :attribute must be greater than {modifiers[0]}.")

                        if rule_for_current_key == "image":
                            # TODO: Implement this rule
                            pass

                        if rule_for_current_key == "in":
                            if not current_value in modifiers:
                                self.errors_[key].append(f"The :attribute must be one of {modifiers}.")

                        if rule_for_current_key == "in_array":
                            if not current_value in self.data.get(modifiers[0]):
                                self.errors_[key].append(f"The :attribute must be in {modifiers[0]}.")

                        if rule_for_current_key == "integer":
                            if not isinstance(current_value, int):
                                self.errors_[key].append(f"The :attribute must be an integer.")

                        if rule_for_current_key == "ip":
                            if not String.of(current_value).is_ip():
                                self.errors_[key].append(f"The :attribute must be a valid IP address.")

                        if rule_for_current_key == "ipv4":
                            if not String.of(current_value).is_ipv4():
                                self.errors_[key].append(f"The :attribute must be a valid IPv4 address.")

                        if rule_for_current_key == "ipv6":
                            if not String.of(current_value).is_ipv6():
                                self.errors_[key].append(f"The :attribute must be a valid IPv6 address.")

                        if rule_for_current_key == "json":
                            if not String.of(current_value).is_json():
                                self.errors_[key].append(f"The :attribute must be a valid JSON string.")

                        if rule_for_current_key == "lt":
                            if isinstance(current_value, str) and isinstance(current_value, str):
                                # if String.of(current_value).length() is greater than modifiers[0] then continue else add error
                                if not String.of(current_value).length() < int(modifiers[0]):
                                    self.errors_[key].append(f"The :attribute must be greater than {modifiers[0]}.")
                            elif isinstance(current_value, int) and isinstance(current_value, int):
                                # if current_value is greater than modifiers[0] then continue else add error
                                if not current_value < int(modifiers[0]):
                                    self.errors_[key].append(f"The :attribute must be greater than {modifiers[0]}.")
                            elif isinstance(current_value, list):
                                # if len(current_value) is greater than modifiers[0] then continue else add error
                                if not len(current_value) < int(modifiers[0]):
                                    self.errors_[key].append(f"The :attribute must be greater than {modifiers[0]}.")
                            elif isinstance(current_value, dict):
                                # if len(current_value) is greater than modifiers[0] then continue else add error
                                if not len(current_value) < int(modifiers[0]):
                                    self.errors_[key].append(f"The :attribute must be greater than {modifiers[0]}.")

                        if rule_for_current_key == "lte":
                            if isinstance(current_value, str) and isinstance(current_value, str):
                                if not String.of(current_value).length() <= int(modifiers[0]):
                                    self.errors_[key].append(f"The :attribute must be greater than {modifiers[0]}.")
                            elif isinstance(current_value, int) and isinstance(current_value, int):
                                if not current_value <= int(modifiers[0]):
                                    self.errors_[key].append(f"The :attribute must be greater than {modifiers[0]}.")
                            elif isinstance(current_value, list):
                                if not len(current_value) <= int(modifiers[0]):
                                    self.errors_[key].append(f"The :attribute must be greater than {modifiers[0]}.")
                            elif isinstance(current_value, dict):
                                if not len(current_value) <= int(modifiers[0]):
                                    self.errors_[key].append(f"The :attribute must be greater than {modifiers[0]}.")

                        if rule_for_current_key == "lowercase":
                            if not current_value.islower():
                                self.errors_[key].append(f"The :attribute must be lowercase.")

                        if rule_for_current_key == "mac_address":
                            if not String.of(current_value).is_mac_address():
                                self.errors_[key].append(f"The :attribute must be a valid MAC address.")

                        if rule_for_current_key == "max":
                            if isinstance(current_value, str) and isinstance(current_value, str):
                                if not String.of(current_value).length() <= int(modifiers[0]):
                                    self.errors_[key].append(f"The :attribute must be greater than {modifiers[0]}.")
                            elif isinstance(current_value, int) and isinstance(current_value, int):
                                if not current_value <= int(modifiers[0]):
                                    self.errors_[key].append(f"The :attribute must be greater than {modifiers[0]}.")
                            elif isinstance(current_value, list):
                                if not len(current_value) <= int(modifiers[0]):
                                    self.errors_[key].append(f"The :attribute must be greater than {modifiers[0]}.")
                            elif isinstance(current_value, dict):
                                if not len(current_value) <= int(modifiers[0]):
                                    self.errors_[key].append(f"The :attribute must be greater than {modifiers[0]}.")

                        if rule_for_current_key == "max_digits":
                            if isinstance(current_value, int):
                                # len(int(current_value)) must be less than or equal to modifiers[0]
                                if not len(str(current_value)) <= int(modifiers[0]):
                                    self.errors_[key].append(f"The :attribute must be less than {modifiers[0]} digits.")

                        if rule_for_current_key == "mimetypes":
                            # TODO: Implement mimes validation
                            raise NotImplementedError("mimetypes validation is not implemented yet.")

                        if rule_for_current_key == "mimes":
                            # TODO: Implement mimes validation
                            raise NotImplementedError("mimes validation is not implemented yet.")

                        if rule_for_current_key == "min":
                            if isinstance(current_value, str) and isinstance(current_value, str):
                                if not String.of(current_value).length() >= int(modifiers[0]):
                                    self.errors_[key].append(f"The :attribute must be greater than {modifiers[0]}.")
                            elif isinstance(current_value, int) and isinstance(current_value, int):
                                if not current_value >= int(modifiers[0]):
                                    self.errors_[key].append(f"The :attribute must be greater than {modifiers[0]}.")
                            elif isinstance(current_value, list):
                                if not len(current_value) >= int(modifiers[0]):
                                    self.errors_[key].append(f"The :attribute must be greater than {modifiers[0]}.")
                            elif isinstance(current_value, dict):
                                if not len(current_value) >= int(modifiers[0]):
                                    self.errors_[key].append(f"The :attribute must be greater than {modifiers[0]}.")

                        if rule_for_current_key == "min_digits":
                            if isinstance(current_value, int) and isinstance(current_value, int):
                                if not String.of(current_value).length() >= int(modifiers[0]):
                                    self.errors_[key].append(f"The :attribute must be greater than {modifiers[0]}.")

                        # TODO: Implement multiple_of validation
                        # TODO: Implement missing* validation

                        if rule_for_current_key == "not_regex":
                            if not re.match(modifiers[0], current_value):
                                self.errors_[key].append(f"The :attribute must not match {modifiers[0]}.")

                        if rule_for_current_key == "numeric":
                            if isinstance(current_value, str):
                                if not current_value.isnumeric():
                                    self.errors_[key].append(f"The :attribute must be numeric.")
                            if isinstance(current_value, (int, float)):
                                continue

                        # TODO: Implement password validation

                        if rule_for_current_key == "present":
                            if current_key not in self.data:
                                self.errors_[key].append(f"The :attribute must be present.")

                        if rule_for_current_key == "prohibited":
                            if current_key in self.data:
                                self.errors_[key].append(f"The :attribute must be prohibited.")

                        # TODO: Implement prohibited* validation

                        if rule_for_current_key == "regex":
                            if not re.match(modifiers[0], current_value):
                                self.errors_[key].append(f"The :attribute must match {modifiers[0]}.")

                        if rule_for_current_key == "required":
                            if current_key not in self.data:
                                self.errors_[key].append(f"The :attribute is required.")

                        # TODO: Implement required_* validation

                        if rule_for_current_key == "same":
                            modifier_field_value = self.data.get(modifiers[0])
                            if current_value != modifier_field_value:
                                self.errors_[key].append(f"The :attribute and {modifiers[0]} must match.")

                        if rule_for_current_key == "size":
                            if isinstance(current_value, str) and isinstance(current_value, str):
                                if not String.of(current_value).length() == int(modifiers[0]):
                                    self.errors_[key].append(f"The :attribute must be equal to {modifiers[0]}.")
                            elif isinstance(current_value, int) and isinstance(current_value, int):
                                if not current_value == int(modifiers[0]):
                                    self.errors_[key].append(f"The :attribute must be equal to {modifiers[0]}.")
                            elif isinstance(current_value, list):
                                if not len(current_value) == int(modifiers[0]):
                                    self.errors_[key].append(f"The :attribute must be equal to {modifiers[0]}.")
                            elif isinstance(current_value, dict):
                                if not len(current_value) == int(modifiers[0]):
                                    self.errors_[key].append(f"The :attribute must be equal to {modifiers[0]}.")

                        if rule_for_current_key == "starts_with":
                            for modifier in modifiers:
                                if modifier:
                                    if not current_value.startswith(modifier):
                                        self.errors_[key].append(f"The :attribute must end with {modifier}.")

                        if rule_for_current_key == "string":
                            if not isinstance(current_value, str):
                                self.errors_[key].append(f"The :attribute must be a string.")

                        if rule_for_current_key == "timezone":
                            try:
                                pendulum.now(current_value)
                            except:
                                self.errors_[key].append(f"The :attribute must be a valid timezone.")

                        # TODO: Implement unique validation

                        if rule_for_current_key == "uppercase":
                            if not current_value.isupper():
                                self.errors_[key].append(f"The :attribute must be uppercase.")

                        if rule_for_current_key == "url":
                            if not String.of(current_value).is_url():
                                self.errors_[key].append(f"The :attribute must be a valid URL.")

                        if rule_for_current_key == "uuid":
                            if not String.of(current_value).is_uuid():
                                self.errors_[key].append(f"The :attribute must be a valid UUID.")

                        if rule_for_current_key == "ulid":
                            if not String.of(current_value).is_ulid():
                                self.errors_[key].append(f"The :attribute must be a valid ULID.")








                    else:
                        rules_for_current_key = rule_for_current_key.split("|")
                        for rule in rules_for_current_key:
                            self.validate({key: rule})
        return self


validated_request = validator.of({
    "name": "Jarriq dagadgdgaËq",
    "age": 16,
    "email": "jrolle@equitybahamas.com",
    "website": "www.goosgle.com",
    "dob": "1991-01-01",
    "cart_items": {"item1": "item1", "item2": "item2", "item3": "item3"},
    "accepted": "da",
    "password": "password",
    "ip": "0.0.0.0"
}).validate({
    "name": "required|max:10|alpha_num|between:1,16|doesnt_start_with:J|doesnt_end_with:q",
    "email": "required|email|between:1,16",
    "age": "required|ascii|between:1,17|gt:18",
    "website": "active_url",
    "dob": "date|date_equals:1991-01-01",
    "cart_items": "between:1,1",
    "accepted": "boolean|exclude_if:password",
    "password": "confirmed",
    "ip": "ip"
})

print(validated_request.fails())

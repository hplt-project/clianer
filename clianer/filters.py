import json
import os
import sys
from typing import Callable, Any, List


FILTERS_LOCATION = "/home/helcl/hplt/OpusCleaner/opuscleaner/filters/"


class FilterConfig:

    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FilterConfig, cls).__new__(cls)
            cls._instance.location = FILTERS_LOCATION
            cls._instance.filters = FilterConfig._load(cls._instance.location)
        return cls._instance

    @classmethod
    def reload_filters(cls):
        cls()._instance.filters = get_filters(cls._instance.location)

    @classmethod
    def set_location(cls, location):
        cls()._instance.location = location
        cls()._instance.filters = _load_filters(location)

    @classmethod
    def get_filters(cls):
        return cls()._instance.filters

    @staticmethod
    def _load(location: str):
        filters = []

        for root, _, paths in os.walk(location):
            for path in paths:
                if not path.endswith(".json"):
                    continue
                filename = os.path.join(root, path)
                flt = FilterConfig._parse_filter(filename, location)
                if flt is not None:
                    filters.append(flt)

        return filters

    @staticmethod
    def _parse_filter(filename: str, location: str):
        name = filename[len(location):].replace("/", ".").replace(".json", "")
        with open(filename, "r") as f:
            filter_cfg = json.load(f)
            try:
                return Filter.from_json(name, filter_cfg)
            except FilterError as e:
                #print(f"Error parsing filter {name}", file=sys.stderr)
                #print(e, file=sys.stderr)
                return None


def parse_bool(value: str):
    return value in ["True", "true", "1", "t"]


class FilterError(Exception):
    pass


class Parameter:
    parsers = {"str": str, "bool": parse_bool, "int": int, "float": float}

    def __init__(self, name: str, helpstr: str = None,
                 default: Any = None, required: bool = None,
                 ptype: Callable[[str], bool] = None):
        self.name = name
        self.helpstr = helpstr
        self.default = default
        self.required = required
        self.ptype = ptype

        # todo maybe warn here if the default value is not of the correct type

    def check_value(self, value: str):
        try:
            self.ptype(value)
            return True
        except ValueError:
            return False

    @staticmethod
    def from_json(name: str, json_dict: dict):

        typestr = json_dict.get("type")
        helpstr = json_dict.get("help")
        if typestr == "tuple":
            assert "parameters" in json_dict
            params = json_dict["parameters"]
            subparams = [Parameter.from_json("", param)
                         for param in params]
            return ParameterGroup(name, helpstr=helpstr, parameters=subparams)

        if typestr not in Parameter.parsers:
            raise FilterError(f"Unknown parameter type: {typestr}")

        ptype = Parameter.parsers[typestr]
        default = json_dict.get("default")
        required = parse_bool(json_dict.get("required", "False"))

        return Parameter(name, helpstr=helpstr, default=default,
                         required=required, ptype=ptype)


class ParameterGroup(Parameter):
    def __init__(self, name: str, helpstr: str, parameters: List[Parameter]):
        super().__init__(name, helpstr=helpstr)
        self.parameters = parameters

    def check_value(self, values: Any):
        return all(p.check_value(v) for p, v in zip(self.parameters, values))


class Filter:
    def __init__(self, name: str, description: str,
                 parameters: List[Parameter], command: str, filter_type: str):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.command = command
        self.filter_type = filter_type  # bilingual or monolingual
        if self.filter_type not in ["bilingual", "monolingual"]:
            raise FilterError(f"Filter {name}: Bad type: {self.filter_type}")

    @staticmethod
    def from_json(name, json_dict: dict):
        return Filter(name, description=json_dict["description"],
                      parameters=[
                          Parameter.from_json(p, json_dict["parameters"][p])
                          for p in json_dict["parameters"]],
                      command=json_dict["command"],
                      filter_type=json_dict["type"])

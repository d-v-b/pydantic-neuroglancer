# @license
# Copyright 2017 Google Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# copied with modifications from
# https://github.com/google/neuroglancer/blob/master/python/neuroglancer/url_state.py

import collections
import json
import re
import urllib
import numbers

from pydantic import ValidationError

from .viewer_state import ViewerState

default_neuroglancer_url = "https://neuroglancer-demo.appspot.com"

SINGLE_QUOTE_STRING_PATTERN = "('(?:[^'\\\\]|(?:\\\\.))*')"
DOUBLE_QUOTE_STRING_PATTERN = '("(?:[^"\\\\]|(?:\\\\.))*")'
SINGLE_OR_DOUBLE_QUOTE_STRING_PATTERN = (
    SINGLE_QUOTE_STRING_PATTERN + "|" + DOUBLE_QUOTE_STRING_PATTERN
)
DOUBLE_OR_SINGLE_QUOTE_STRING_PATTERN = (
    DOUBLE_QUOTE_STRING_PATTERN + "|" + SINGLE_QUOTE_STRING_PATTERN
)


DOUBLE_QUOTE_PATTERN = '^((?:[^"\'\\\\]|(?:\\\\.))*)"'
SINGLE_QUOTE_PATTERN = "^((?:[^\"'\\\\]|(?:\\\\.))*)'"

min_safe_integer = -9007199254740991
max_safe_integer = 9007199254740991


def json_encoder_default(obj):
    """JSON encoder function that handles some numpy types."""
    if isinstance(obj, numbers.Integral) and (
        obj < min_safe_integer or obj > max_safe_integer
    ):
        return str(obj)
    elif isinstance(obj, (set, frozenset)):
        return list(obj)
    raise TypeError


def decode_json(x):
    return json.loads(x, object_pairs_hook=collections.OrderedDict)


def encode_json(obj):
    return json.dumps(obj, default=json_encoder_default)


def encode_json_for_repr(obj):
    return json.dumps(obj, default=json_encoder_default_for_repr)


def _convert_string_literal(x, quote_initial, quote_replace, quote_search):
    if len(x) >= 2 and x[0] == quote_initial and x[-1] == quote_initial:
        inner = x[1:-1]
        s = quote_replace
        while inner:
            m = re.search(quote_search, inner)
            if m is None:
                s += inner
                break
            s += m.group(1)
            s += "\\"
            s += quote_replace
            inner = inner[m.end() :]
        s += quote_replace
        return s
    return x


def _convert_json_helper(x, desired_comma_char, desired_quote_char):
    comma_search = "[&_,]"
    if desired_quote_char == '"':
        quote_initial = "'"
        quote_search = DOUBLE_QUOTE_PATTERN
        string_literal_pattern = SINGLE_OR_DOUBLE_QUOTE_STRING_PATTERN
    else:
        quote_initial = '"'
        quote_search = SINGLE_QUOTE_PATTERN
        string_literal_pattern = DOUBLE_OR_SINGLE_QUOTE_STRING_PATTERN
    s = ""
    while x:
        m = re.search(string_literal_pattern, x)
        if m is None:
            before = x
            x = ""
            replacement = ""
        else:
            before = x[: m.start()]
            x = x[m.end() :]
            original_string = m.group(1)
            if original_string is not None:
                replacement = _convert_string_literal(
                    original_string, quote_initial, desired_quote_char, quote_search
                )
            else:
                replacement = m.group(2)
        s += re.sub(comma_search, desired_comma_char, before)
        s += replacement
    return s


def url_safe_to_json(x):
    return _convert_json_helper(x, ",", '"')


def json_to_url_safe(x):
    return _convert_json_helper(x, "_", "'")


def url_fragment_to_json(fragment_value):
    unquoted = urllib.parse.unquote(fragment_value)
    if unquoted.startswith("!"):
        unquoted = unquoted[1:]
    return url_safe_to_json(unquoted)


def parse_url_fragment(fragment_value):
    json_string = url_fragment_to_json(fragment_value)
    json_blob = json.loads(json_string)
    try:
        vs = ViewerState(**json_blob)
    except ValidationError as e:
        print(json.dumps(json_blob, indent=2))
        raise e
    return vs


def parse_url(url):
    result = urllib.parse.urlparse(url)
    return parse_url_fragment(result.fragment)


def to_url_fragment(state: ViewerState):
    json_string = json.dumps(
        state.json(), separators=(",", ":"), default=json_encoder_default
    )
    return urllib.parse.quote(json_string, safe="~@#$&()*!+=:;,.?/'")


def to_url(state, prefix=default_neuroglancer_url):
    return "%s#!%s" % (prefix, to_url_fragment(state))


def to_json_dump(state, indent=None, separators=None):
    return json.dumps(
        to_json(state),
        separators=separators,
        indent=indent,
        default=json_encoder_default,
    )

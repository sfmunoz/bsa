#!/usr/bin/env python3
# vim: set foldmethod=marker:

# {{{ AI agent instructions
#
# - The only context required to make changes is this file -> ignore other files in the project
# - The only file to change is this one (nothing else)
# - Keep the file style as it is when you make changes
# - Methods must have fewer than 25 lines -> create other methods as required
# - Don't create standalone functions -> everything must be contained in classes
# - Only use Python3 standard library -> no external libraries
# - Don't add comments unless it is unavoidable to describe some critical part
# - Apply what's defined in the Changes section
#   - [X] Marks a completed change — skip it
#   - [ ] Marks a pending change — process only the first one
#
# }}}
# {{{ Changes
#
# [X] Add counter method
#     - Create BSA.__counter(self, tot) which runs "log.info()" to output ">> <number>" from 1 to tot (inclusive)
#     - Call it from BSA.run() to show 20 lines
# [X] Add support for calling OpenCode Go -> "deepseek-v4-flash" model
#     - Do it in a class with name 'OpenCodeGoDeepSeekV4Flash'
#       - 'OpenCodeGoDeepSeekV4Flash.run()' orchestrates execution (like BSA.run())
#       - Create other private methods as needed
#     - Input: data read from stdin by bsa.py
#     - Output: bsa.py must write to stdout
#     - Use "log" object to show progress if needed
#     - Ref: https://opencode.ai/docs/go/
#     - Call it from 'BSA.run()'
#
# }}}
# --------------------------------------
# {{{ imports

import os
import json
import sys
import urllib.request
from argparse import ArgumentParser
from logging import getLogger, basicConfig, INFO, DEBUG

basicConfig(format='%(asctime)s [%(relativeCreated)7.0f] [%(levelname).1s] %(message)s (%(module)s:%(lineno)d)',level=INFO,stream=sys.stderr)
log = getLogger(__name__)

# }}}
# -------- BSA(object) -- class --------
# {{{ BSA -- class

class BSA(object):

# }}}
# {{{ BSA.__init__()

    def __init__(self,args):
        log.info("BSA.__init__()")
        self.__args = args

# }}}
# {{{ BSA.run()

    def run(self):
        log.info("BSA.run()")
        if not sys.stdin.isatty():
            OpenCodeGoDeepSeekV4Flash(self.__args).run()
        else:
            self.__counter(20)

# }}}
# {{{ BSA.__counter()

    def __counter(self, tot):
        for i in range(1, tot + 1):
            log.info(">> %d", i)

# }}}
# -------- OpenCodeGoDeepSeekV4Flash(object) -- class --------
# {{{ OpenCodeGoDeepSeekV4Flash -- class

class OpenCodeGoDeepSeekV4Flash(object):

# }}}
# {{{ OpenCodeGoDeepSeekV4Flash.__init__()

    def __init__(self, args):
        log.info("OpenCodeGoDeepSeekV4Flash.__init__()")
        self.__args = args
        self.__api_key: str = os.environ.get("OPENCODE_GO_API_KEY", "")
        if not self.__api_key:
            log.error("OPENCODE_GO_API_KEY environment variable not set")
            sys.exit(1)

# }}}
# {{{ OpenCodeGoDeepSeekV4Flash.run()

    def run(self):
        log.info("OpenCodeGoDeepSeekV4Flash.run()")
        prompt = sys.stdin.read()
        if not prompt.strip():
            log.error("No input data on stdin")
            sys.exit(1)
        response = self.__call_api(prompt)
        sys.stdout.write(response)

# }}}
# {{{ OpenCodeGoDeepSeekV4Flash.__call_api()

    def __call_api(self, prompt):
        payload = {
            "model": "deepseek-v4-flash",
            "messages": [{"role": "user", "content": prompt}]
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            "https://opencode.ai/zen/go/v1/chat/completions",
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + self.__api_key,
                "User-Agent": "bsa-agent/0.0.1"
            }
        )
        log.info("Calling OpenCode Go API (deepseek-v4-flash)...")
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        return result["choices"][0]["message"]["content"]

# }}}
# -------- main --------
# {{{ main

if __name__ == "__main__":
    parser = ArgumentParser(
        description = 'main.py (v1.0)',
        epilog = "sfmunoz (C) 2026"
    )

    parser.add_argument('-d', '--debug', action='store_true',
                        help='enable debug mode')

    args = parser.parse_args()

    if args.debug:
        log.setLevel(DEBUG)

    BSA(args).run()

# }}}

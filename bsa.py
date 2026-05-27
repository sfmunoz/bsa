#!/usr/bin/env python3
# vim: set foldmethod=marker:

# {{{ AI agent instructions
#
# - The only context required to make changes is this file: nothing else
# - The only file to change is this one: nothing else
# - The only input provided to the model is this file: nothing else
# - The only output returned by the model must be the updated file: nothing else
#   - Don't include markup at the top (e.g. "```python")
#   - Don't include markup at the bottom (e.g. "```")
# - Keep the file style as it is when you make changes
# - Methods must have fewer than 25 lines -> create other methods as required
# - Don't create standalone functions -> everything must be contained in classes
# - Only use Python3 standard library -> no external libraries
# - Don't add comments unless it is unavoidable to describe some critical part
# - Apply what's defined in the Changes section
#   - [X] Marks a completed change — skip it
#   - [ ] Marks a pending change — process only the first one
# - Code conventions:
#   - BSA class must be the last one in the file
#   - run() method must be the last one if the class implements it
#   - for multiline dictionaries, function calls, etc. the last always has a trailing comma
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
# [X] Delete BSA.__counter() and related stuff
# [X] Apply code conventions added to the instructions in this file (Code conventions within AI agent instructions)
# [X] Auto-patch support
#     - If there's stdin data use it as prompt
#     - If there is not stdin data build it with the following content
#       - Generate a "diff" output that can be used by "patch" tool to modify the file which will follow
#       - The instructions for the agent are included in the file
#       - ==== BEGIN ====
#       - the content of this file (bsa.py) must be included here
#       - ---- END ----
#     - The output must be dump to stdout in both cases (as it is now)
# [X] Debug support
#     - When debug flag is enabled the prompt must be sent to log (one line at a time)
# [X] Script-in, script-out
#     - The model must receive exactly the full file. Nothing more, nothing less
#     - The model must return exactly the modified full file. Nothing more, nothing less
#     - stdin processing behaviour is the same: if content is provided over stdin use that
# [X] Send the response of the model to 'log.debug()'
#     - When debug is enabled the output must be sent to 'log.debug()'
#     - The complete body of the output (JSON) must be sent to 'log.debug()'
#     - The body must be formatted using something like 'json.dumps(...,indent=2,sort_keys=True)'
#     - The resulting string must be sent to 'log.debug()' (one line at a time)
# [X] Create 'OpenCodeGoDeepSeekV4Flash.__write_self()'
#     - It's 'OpenCodeGoDeepSeekV4Flash.__read_self()' counterpart
#     - Must be used when 'OpenCodeGoDeepSeekV4Flash.__read_self()' is used
#     - Writes the model output to the same file the input was read from
#     - When model-input is read from stdin, model-output is written to stdout (as it is now)
# [ ] Multi-model support (to be detailed)
# [ ] Auto-modification support applying the patch (to be detailed)
# [ ] Auto-commit support (to be detailed)
# [ ] Stream support when interacting with the model
# [ ] Error handling support (feed it to the model)
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
# {{{ OpenCodeGoDeepSeekV4Flash.__call_api()

    def __call_api(self, prompt):
        payload = {
            "model": "deepseek-v4-flash",
            "messages": [{"role": "user", "content": prompt}],
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            "https://opencode.ai/zen/go/v1/chat/completions",
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + self.__api_key,
                "User-Agent": "bsa-agent/0.0.1",
            },
        )
        log.info("Calling OpenCode Go API (deepseek-v4-flash)...")
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        return result

# }}}
# {{{ OpenCodeGoDeepSeekV4Flash.__read_self()

    def __read_self(self):
        script_path = os.path.realpath(__file__)
        with open(script_path, 'r') as f:
            return f.read()

# }}}
# {{{ OpenCodeGoDeepSeekV4Flash.__write_self()

    def __write_self(self, content):
        script_path = os.path.realpath(__file__)
        log.info("Writing model output to %s", script_path)
        with open(script_path, 'w') as f:
            f.write(content)

# }}}
# {{{ OpenCodeGoDeepSeekV4Flash.run()

    def run(self):
        log.info("OpenCodeGoDeepSeekV4Flash.run()")
        is_self = sys.stdin.isatty()
        if is_self:
            log.info("No stdin pipe, reading self for script-in")
            prompt = self.__read_self()
        else:
            prompt = sys.stdin.read()
            if not prompt.strip():
                log.error("No input data on stdin")
                sys.exit(1)
        if self.__args.debug:
            for line in prompt.splitlines():
                log.debug(line)
        api_response = self.__call_api(prompt)
        content = api_response["choices"][0]["message"]["content"]
        if self.__args.debug:
            formatted = json.dumps(api_response, indent=2, sort_keys=True)
            for line in formatted.splitlines():
                log.debug(line)
        if is_self:
            self.__write_self(content)
        else:
            sys.stdout.write(content)

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
        OpenCodeGoDeepSeekV4Flash(self.__args).run()

# }}}
# -------- main --------
# {{{ main

if __name__ == "__main__":
    parser = ArgumentParser(
        description = 'bsa.py (v0.0.1)',
        epilog = "sfmunoz (C) 2026",
    )

    parser.add_argument('-d', '--debug', action='store_true',
                        help='enable debug mode',)

    args = parser.parse_args()

    if args.debug:
        log.setLevel(DEBUG)

    BSA(args).run()

# }}}

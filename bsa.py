#!/usr/bin/env python3
# vim: set foldmethod=marker:

# {{{ AI agent instructions
#
# - The only context required to make changes is this file: nothing else
# - The only file to change is this one: nothing else
# - The only input provided to the model is this file: nothing else
# - The only output returned by the model must be the updated file: nothing else
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
# - Types:
#   - Every method or function argument must have a type
#   - Every method or function return value must have a type
#   - Every new variable must have a type
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
# [X] Add dry-run support
#     - Command line flag: '-n' / '--dry-run'
#     - When enabled no interaction with the model is carried out
#       - Program stops right before that moment
#       - It must show a message explaining dry-run flag is on
# [X] Verify and remove python markup
#   - Make sure the first line of the model response is exactly "```python" (without quotes). Exception otherwise
#   - Make sure the last line of the model response is exactly "```" (without quotes). Exception otherwise
#   - Remove both the first and the last line
#   - Do this in a new single method
# [X] Add type to every argument and return value:
#   - Every argument of every method must have the type defined
#   - Every return value of every method must have the type defined
#   - 'uvx ty check' must finish without warnings/errors
# [X] Add type to every defined variable
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
from argparse import ArgumentParser, Namespace
from logging import getLogger, basicConfig, INFO, DEBUG, Logger
basicConfig(
    format="%(asctime)s [%(relativeCreated)7.0f] [%(levelname).1s] %(message)s",
    level=INFO,
    stream=sys.stderr,
)
log: Logger = getLogger(__name__)

# }}}
# -------- Prompt(object) -- class --------
# {{{ Prompt -- class

class Prompt(object):
    # }}}
    # {{{ Prompt.__init__()

    def __init__(self) -> None:
        log.info("Prompt.__init__()")
        self.__path: str = os.path.realpath(__file__)
        self.__from_stdin: bool = not sys.stdin.isatty()

    # }}}
    # {{{ Prompt.__read_self()

    def __read_self(self) -> str:
        with open(self.__path, "r") as f:
            return f.read()

    # }}}
    # {{{ Prompt.build()

    def build(self) -> str:
        if self.__from_stdin:
            prompt: str = sys.stdin.read()
            if not prompt.strip():
                log.error("No input data on stdin")
                sys.exit(1)
            return prompt
        log.info("No stdin pipe, reading self for script-in")
        return self.__read_self()

    # }}}
    # {{{ Prompt.from_self

    @property
    def from_self(self) -> bool:
        return not self.__from_stdin


# }}}
# -------- OpenCodeGoDeepSeekV4Flash(object) -- class --------
# {{{ OpenCodeGoDeepSeekV4Flash -- class


class OpenCodeGoDeepSeekV4Flash(object):
    # }}}
    # {{{ OpenCodeGoDeepSeekV4Flash.__init__()

    def __init__(self, args: Namespace) -> None:
        log.info("OpenCodeGoDeepSeekV4Flash.__init__()")
        self.__args: Namespace = args
        self.__api_key: str = os.environ.get("OPENCODE_GO_API_KEY", "")
        if not self.__api_key:
            log.error("OPENCODE_GO_API_KEY environment variable not set")
            sys.exit(1)

    # }}}
    # {{{ OpenCodeGoDeepSeekV4Flash.__call_api()

    def __call_api(self, prompt: str) -> dict:
        payload: dict = {
            "model": "deepseek-v4-flash",
            "messages": [{"role": "user", "content": prompt}],
        }
        data: bytes = json.dumps(payload).encode("utf-8")
        req: urllib.request.Request = urllib.request.Request(
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
            result: dict = json.loads(resp.read().decode("utf-8"))
        return result

    # }}}
    # {{{ OpenCodeGoDeepSeekV4Flash.__write_self()

    def __write_self(self, content: str) -> None:
        script_path: str = os.path.realpath(__file__)
        log.info("Writing model output to %s", script_path)
        with open(script_path, "w") as f:
            f.write(content)

    # }}}
    # {{{ OpenCodeGoDeepSeekV4Flash.__debug_prompt()

    def __debug_prompt(self, prompt: str) -> None:
        if self.__args.debug:
            for line in prompt.splitlines():
                log.debug(line)

    # }}}
    # {{{ OpenCodeGoDeepSeekV4Flash.__debug_response()

    def __debug_response(self, api_response: dict) -> None:
        if self.__args.debug:
            formatted: str = json.dumps(api_response, indent=2, sort_keys=True)
            for line in formatted.splitlines():
                log.debug(line)

    # }}}
    # {{{ OpenCodeGoDeepSeekV4Flash.__verify_and_strip_markup()

    def __verify_and_strip_markup(self, content: str) -> str:
        lines: list[str] = content.splitlines()
        if not lines:
            raise ValueError("Model response is empty")
        if lines[0].strip() != "```python":
            raise ValueError("First line is not exactly ```python")
        if lines[-1].strip() != "```":
            raise ValueError("Last line is not exactly ```")
        stripped: str = "\n".join(lines[1:-1])
        log.info("Stripped python markup from model response")
        return stripped

    # }}}
    # {{{ OpenCodeGoDeepSeekV4Flash.__write_output()

    def __write_output(self, content: str, is_self: bool) -> None:
        if is_self:
            self.__write_self(content)
        else:
            sys.stdout.write(content)

    # }}}
    # {{{ OpenCodeGoDeepSeekV4Flash.run()

    def run(self) -> None:
        log.info("OpenCodeGoDeepSeekV4Flash.run()")
        prompt_obj: Prompt = Prompt()
        prompt: str = prompt_obj.build()
        is_self: bool = prompt_obj.from_self
        self.__debug_prompt(prompt)
        if self.__args.dry_run:
            log.info("Dry-run mode enabled; no API call will be made.")
            sys.exit(0)
        api_response: dict = self.__call_api(prompt)
        content: str = api_response["choices"][0]["message"]["content"]
        self.__debug_response(api_response)
        try:
            content = self.__verify_and_strip_markup(content)
        except ValueError as e:
            log.error("Response markup verification failed: %s", e)
            sys.exit(1)
        self.__write_output(content, is_self)


# }}}
# -------- BSA(object) -- class --------
# {{{ BSA -- class


class BSA(object):
    # }}}
    # {{{ BSA.__init__()

    def __init__(self, args: Namespace) -> None:
        log.info("BSA.__init__()")
        self.__args: Namespace = args

    # }}}
    # {{{ BSA.run()

    def run(self) -> None:
        log.info("BSA.run()")
        OpenCodeGoDeepSeekV4Flash(self.__args).run()


# }}}
# -------- main --------
# {{{ main

if __name__ == "__main__":
    parser: ArgumentParser = ArgumentParser(
        description="bsa.py (v0.0.1)",
        epilog="sfmunoz (C) 2026",
    )

    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="enable debug mode",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="enable dry run mode (no API call)",
    )

    args: Namespace = parser.parse_args()

    if args.debug:
        log.setLevel(DEBUG)

    BSA(args).run()

# }}}

import json
import os.path

import util

_ATTRIBUTES_PATH: str = "./agent.json"
_SIGNATURE_KEY: str = "signature"
_DELTA_KEY: str = "delta"
_INITIALIZED: bool = False

SIGNATURE: str
DELTA: float

# there must be an attributes file in the root directory of the project
assert os.path.exists(_ATTRIBUTES_PATH), f"Agent attributes ({_ATTRIBUTES_PATH}) is missing."


def initialize() -> None:
    """ Sets the main agent's signature and delta based on the ``agent.json`` file.

    After successful initialization the main initialization flagged with ``INITIALIZED = True``.

    Raises:
        AssertionError: If attributes file does not contain the required agent information.
    """

    global SIGNATURE, DELTA, _INITIALIZED

    # open attributes file
    with open(_ATTRIBUTES_PATH) as attributes_file:
        # parse json data to dictionary
        attributes = json.load(attributes_file)

        # the attributes must include the agent's signature and delta
        util.assert_keys_exist([_SIGNATURE_KEY, _DELTA_KEY], attributes)

        # set the main agent's signature and delta and the initialization flag
        SIGNATURE = attributes[_SIGNATURE_KEY]
        DELTA = attributes[_DELTA_KEY]
        _INITIALIZED = True


# always initialize attributes when loaded
if not _INITIALIZED:
    initialize()

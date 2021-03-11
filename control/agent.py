import json
import os.path

from util.assertions import assert_keys_exist

ATTRIBUTES_PATH = "./agent.json"

SIGNATURE_KEY = "signature"
DELTA_KEY = "delta"

# there must be an attributes file in the root directory of the project
assert os.path.exists(ATTRIBUTES_PATH), f"Agent attributes ({ATTRIBUTES_PATH}) is missing."


def _initialize_agent() -> None:
    """ Sets the main agent's signature and delta based on the ``agent.json`` file.

    After successful initialization the main agent ist flagged with ``MainAgent.INITIALIZED = True``.
    """

    # open attributes file
    with open(ATTRIBUTES_PATH) as attributes_file:
        # parse json data to dictionary
        attributes = json.load(attributes_file)

        # the attributes must include the agent's signature and delta
        assert_keys_exist([SIGNATURE_KEY, DELTA_KEY], attributes)

        # set the main agent's signature and delta and the initialization flag
        MainAgent.SIGNATURE = attributes[SIGNATURE_KEY]
        MainAgent.DELTA = attributes[DELTA_KEY]
        MainAgent.INITIALIZED = True


class MainAgent:
    SIGNATURE: str
    DELTA: float
    INITIALIZED: bool = False

    pass


# always initialize the main agent when loaded
if not MainAgent.INITIALIZED:
    _initialize_agent()

from __future__ import annotations

from datetime import datetime
from typing import Dict, Callable, Any

import paho.mqtt.client as mqtt
from paho.mqtt import publish

from control import MainAgent
from interaction.message import Message, MessageContent
from util import Singleton

BROKER_URL = "test.mosquitto.org"
BROKER_PORT = 1883
TIMEOUT = 15

TOPIC_PREFIX = "parknet-21/communication/"

Callback = Callable[[Message], Any]


class _Subscription:
    def __init__(self, callback: Callback, receive_own: bool):
        self.callback: Callback = callback
        self.receive_own: bool = receive_own

    def handle(self, message: Message) -> None:
        """ Calls the callback function if the message applies to the subscription.

        The message applies to the subscription exactly if it was sent by another agent or if the subscription
        specifies to react to the agent's own messages.
        The callback function gets the message as its own argument.

        Args:
            message: Received message linked to the subscription.
        """

        # check if message was sent by another agent or subscription applies to the agent's own messages
        if message.sender != MainAgent.SIGNATURE or self.receive_own:
            self.callback(message)


@Singleton
class _Connection:
    def __init__(self):
        self.subscriptions: Dict[str, _Subscription] = {}
        self.client: mqtt.Client = mqtt.Client()
        self.client.on_message = self.react
        self.client.connect(BROKER_URL, BROKER_PORT, TIMEOUT)

        # start listening for messages
        self.client.loop_start()

    def subscribe(self, topic: str, callback: Callback, receive_own: bool) -> None:
        """ Adds a communication subscription for a given topic.

        As there can only be one subscription per topic, prior subscriptions for the same topic are overwritten.

        Args:
            topic: Topic to subscribe to.
            callback: Callback function to be triggered when a message for the subscribed topic is received.
            receive_own: Boolean whether the sender shall receive his own messages.
        """

        # add subscription
        self.subscriptions[topic] = _Subscription(callback, receive_own)

        # subscribe to communication broker
        self.client.subscribe(TOPIC_PREFIX + topic, qos=1)

    @staticmethod
    def send(message: Message) -> None:
        """ Publishes an encoded message.

        Args:
            message: Message to be published.
        """

        # encode message
        json_message = message.encode()

        # publish message to broker
        publish.single(TOPIC_PREFIX + message.topic, json_message, hostname=BROKER_URL)

    def react(self, _client, _user, data: mqtt.MQTTMessage) -> None:
        """ Handles an incoming message by triggering the corresponding callback function (if existent).

        Args:
            _client: Client data.
            _user: User data.
            data: Encoded MQTT message.
        """

        # decode message
        message = Message.decode(data.payload.decode())

        # trigger subscription if existent
        if message.topic in self.subscriptions:
            self.subscriptions[message.topic].handle(message)


class Communication:
    class TOPICS:
        FORMATION = "formation"

    def __init__(self):
        self._connection: _Connection = _Connection()

    def _subscribe(self, topic: str, callback: Callback, receive_own: bool = False) -> None:
        """ Adds a communication subscription to the connection.

        See Also:
            - ``def Connection.subscribe(...)``

        Args:
            topic: Topic to subscribe to.
            callback: Callback function to be triggered when a message for the subscribed topic is received.
            receive_own: Boolean whether the sender shall receive his own messages.
        """

        self._connection.subscribe(topic, callback, receive_own)

    def _send(self, topic: str, content: MessageContent) -> None:
        """ Publishes a message sent by the main agent.

        Args:
            topic: Topic of the message.
            content: Content of the message (JSON compatible).
        """

        self._connection.send(Message(MainAgent.SIGNATURE, topic, content, datetime.now()))

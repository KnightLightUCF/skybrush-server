"""A registry that contains information about all the different types of
communication channels that the server can handle.

Communication channels may include things like Socket.IO connections, bare
TCP or UDP connections and so on.

Note that the registry keeps track of the different *types* of communication
channels, not each individual channel between a client and the server.
"""

from __future__ import absolute_import

from blinker import Signal
from collections import namedtuple

from ..logger import log as base_log
from ..model import CommunicationChannel
from .base import RegistryBase

__all__ = ("ChannelTypeRegistry", )

log = base_log.getChild("registries.channels")


ChannelTypeDescriptor = namedtuple(
    "ChannelTypeDescriptor",
    "id factory broadcaster"
)


class ChannelTypeRegistry(RegistryBase):
    """Registry that contains information about all the communication channel
    types that the server can handle.

    Attributes:
        added (Signal): signal that is sent by the registry when a new
            communication channel type has been registered in the registry.
            The signal has a keyword argment named ``descriptor`` that
            contains information about the channel type that was added.
            ``descriptor`` will be an instance of ChannelTypeDescriptor_.

        count_changed (Signal): signal that is sent by the registry when the
            number of registered communication channel types has changed.

        removed (Signal): signal that is sent by the registry when a
            communication channel type has been removed from the registry.
            The signal has a keyword argment named ``descriptor`` that
            contains information about the channel type that was removed.
            ``descriptor`` will be an instance of ChannelTypeDescriptor_.
    """

    added = Signal()
    count_changed = Signal()
    removed = Signal()

    def add(self, channel_id, factory, broadcaster=None):
        """Adds a new communication channel class to the registry.

        This function throws an error if the ID is already taken.

        Arguments:
            channel_id (str): the ID of the communication channel type
            factory (callable): a callable that constructs a new
                communication channel of this type when invoked with no
                arguments. The callable is typically a class that extends
                CommunicationChannel_ and has an appropriate constructor,
                but can be an arbitrary callable as long as it returns an
                instance of CommunicationChannel_.
            broadcaster (Optional[callable]): a callable that implements
                broadcasting a message to all clients who are currently
                connected to the server with this communication channel
                type. The callable will be called with the message to be
                sent as its only argument. When this property is ``None``,
                it is assumed that there is no compact way to broadcast
                a message to all the clients who are connected with this
                channel type, and the application will fall back to sending
                individual messages.
        """
        if channel_id in self:
            return

        descriptor = ChannelTypeDescriptor(
            id=channel_id, factory=factory, broadcaster=broadcaster
        )
        self._entries[channel_id] = descriptor

        log.info("Channel registered", extra={"id": channel_id})

        self.added.send(self, id=channel_id, descriptor=descriptor)
        self.count_changed.send(self)

    def create_channel_for(self, channel_id):
        """Creates a new communication channel with the type whose ID is
        given in the first argument.

        Arguments:
            channel_id (str): the ID of the communication channel type

        Returns:
            CommunicationChannel: a new communication channel of the given
                type.
        """
        result = self._entries[channel_id].factory()
        assert isinstance(result, CommunicationChannel), \
            "communication channel factory did not return a "\
            "CommunicationChannel"
        return result

    @property
    def num_entries(self):
        """Returns the number of channel types currently registered in the
        registry.
        """
        return len(self._entries)

    def remove(self, channel_id):
        """Removes a communication channel class by ID from the set of
        channels registered in the registry.

        This function is a no-op if the channel class was already removed.

        The behaviour of the server is undefined if there are still clients
        who use a communication channel of this type.

        Arguments:
            channel_id (str): the ID of the channel type to remove
        """
        try:
            descriptor = self._entries.pop(channel_id)
        except KeyError:
            return

        log.info("Channel deregistered", extra={"id": channel_id})
        self.count_changed.send(self)
        self.removed.send(self, id=channel_id, descriptor=descriptor)
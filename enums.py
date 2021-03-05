import enum


class InteractionSendType(int, enum.Enum):
    pong = 1
    acknowledge = 2
    channel_message = 3
    channel_message_with_source = 4
    acknowledge_with_ource = 5
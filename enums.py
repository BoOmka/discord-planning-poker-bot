import enum


class InteractionSendType(enum.Enum, int):
    pong = 1
    acknowledge = 2
    channel_message = 3
    channel_message_with_source = 4
    acknowledge_with_ource = 5
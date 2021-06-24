import discord


class CustomPartialEmoji(discord.PartialEmoji):
    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other
        else:
            return super().__eq__(other)

    def __str__(self):
        return self.name

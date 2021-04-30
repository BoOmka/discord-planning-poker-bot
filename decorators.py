import functools

import storage


async def _complain_no_active_vote(ctx):
    await ctx.send(
        content="There's no active vote in this channel. You can start one by typing `/poker start`",
        complete_hidden=True
    )


def needs_active_vote(func):
    @functools.wraps(func)
    async def wrapped(ctx, *args, **kwargs):
        channel_storage = storage.get_channel_storage_or_none_by_ctx(ctx)
        if channel_storage is None:
            await _complain_no_active_vote(ctx)
            return
        return await func(ctx, *args, **kwargs)
    return wrapped

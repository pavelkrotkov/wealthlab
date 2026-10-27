"""Label native path completion without changing projection results or selection."""

from functools import partial


def observe(observer, phase, batch):
    if observer is None:
        return None
    observer(phase, 0, len(batch.mark_returns))
    return partial(observer, phase)

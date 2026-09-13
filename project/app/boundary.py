"""Where each step is allowed to run.

Checked at import, not reviewed in a document. Data that may not leave
cannot leave by construction, and an embedding is not an exception --
it is recoverable to its source, so it inherits the same placement.
"""

PLACEMENT = {
    'approve-integration': 'in_boundary',
    'boundary-split': 'in_boundary',
    'critic-integration': 'in_boundary',
    'deployment': 'in_boundary',
    'evaluation': 'in_boundary',
    'governance': 'in_boundary',
    'integration': 'in_boundary',
    'observability': 'in_boundary',
    'perception': 'in_boundary',
    'provisioning': 'in_boundary',
    'representation': 'in_boundary',
}

SENSITIVE = {
    'perception',
    'representation',
}


def check() -> None:
    """Fail loudly if anything sensitive has been moved outside."""
    outside = [s for s in SENSITIVE if PLACEMENT.get(s) != 'in_boundary']
    if outside:
        raise RuntimeError(
            f'{outside} handle data that may not leave, but are placed outside'
        )


check()

"""Minimized reproduction of Astropy separability logic."""

import numpy as np


class Model:
    """Placeholder model type used by the separability helpers."""

    def __init__(self, n_outputs):
        self.n_outputs = n_outputs


def _compute_n_outputs(left, right):
    if isinstance(left, Model):
        lnout = left.n_outputs
    else:
        lnout = left.shape[0]

    if isinstance(right, Model):
        rnout = right.n_outputs
    else:
        rnout = right.shape[0]

    return lnout + rnout


def _coord_matrix(model, pos, noutp):
    raise NotImplementedError("Model-based paths are not part of this minimized task")


def _cstack(left, right):
    noutp = _compute_n_outputs(left, right)

    if isinstance(left, Model):
        cleft = _coord_matrix(left, "left", noutp)
    else:
        cleft = np.zeros((noutp, left.shape[1]))
        cleft[: left.shape[0], : left.shape[1]] = left

    if isinstance(right, Model):
        cright = _coord_matrix(right, "right", noutp)
    else:
        cright = np.zeros((noutp, right.shape[1]))
        cright[-right.shape[0]:, -right.shape[1]:] = 1

    return np.hstack([cleft, cright])

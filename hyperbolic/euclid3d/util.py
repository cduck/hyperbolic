import numpy as np


dtype = np.float64


def relaxed_matmul(m1, m2):
    '''Numpy matmul where the summed-over dimensions may not match.

    Extra matrix entries are assumed to be zero.'''
    promote2 = m2.ndim == 1
    min_dim = min(m1.shape[-1], m2.shape[-2+promote2])
    if promote2:
        return m1[..., :min_dim] @ m2[..., :min_dim]
    return m1[..., :min_dim] @ m2[..., :min_dim, :]

def gram_schmidt(X, tolerance=1e-12, require_li=True):
    '''Performs Gram-Schmidt orthogonalization on the columns of a matrix.

    Args:
        X: The matrix (2D numpy array) with shape (n, p).
        tolerance: Any vector with norm less than tolerance is considered zero.
        require_li: Raises ValueError if the columns of X are not linearly
            independent.  If X has more than two dimensions, require_li must be
            True.

    Returns:
        U, a new matrix with shape (n, r) where r <= p.  r is the rank of X and
        U.
    '''
    if X.ndim > 2 and not require_li:
        raise ValueError(
            'require_li must be True if X has more than two dimensions.')

    if X.shape[-1] <= 0:
        # X has 0 columns
        return X
    if X.shape[-2] <= 0:
        # X has 0 rows => all columns are 0 => delete all columns
        if require_li and X.shape[-1] > 0:
            raise ValueError(
                'Basis vectors are not linearly independent: Columns are '
                'zero-dimensional.')
        return X[..., :0, :0]

    include_columns = []
    at_least_float = type(X.dtype.type() / 1)
    U = np.array(X, dtype=at_least_float, copy=True)
    any_zero = False

    for i in range(0, X.shape[-1]):
        if len(include_columns) <= 0:
            # Initialize 1st column
            norm = np.linalg.norm(U[..., i], axis=-1)
            if np.any(norm < tolerance):
                any_zero = True
                # Don't use zero vector columns
                if require_li:
                    raise ValueError(
                        'Basis vectors are not linearly independent: First '
                        'column is zero.')
                continue
            U[..., i] /= norm[..., np.newaxis]
            include_columns.append(i)
        else:
            # Add another column
            if any_zero:
                U_current = U[..., include_columns]
            else:
                U_current = U[..., :i]
            t = U_current.swapaxes(-2, -1) @ X[..., i, np.newaxis]
            t2 = U_current @ (t)
            U[..., i] -= t2[..., 0]
            norm = np.linalg.norm(U[..., i], axis=-1)
            if np.any(norm < tolerance):
                any_zero = True
                # Don't output zero vector columns
                if require_li:
                    raise ValueError(
                        'Basis vectors are not linearly independent: Column {} '
                        'is LD.'.format(i))
                continue
            U[..., i] /= norm[..., np.newaxis]
            include_columns.append(i)

    # Return the non-zero columns of U
    if require_li:
        return U
    return U[..., include_columns]

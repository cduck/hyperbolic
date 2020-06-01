from typing import Optional, Sequence, Tuple

import abc
import dataclasses
import numpy as np

from .util import dtype, relaxed_matmul


class Projection(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def in_dim(self):
        '''The expected dimension of input coordinates.'''

    @property
    @abc.abstractmethod
    def out_dim(self):
        '''The dimension of projected coordinates.'''

    def project_point(self, point):
        '''Projects a single point.'''
        points = np.asarray(point, dtype)[:,np.newaxis]
        return self.project(points)[..., 0]

    def p1(self, *coords):
        x, = self.project_point(coords)[:1]
        return x

    def p2(self, *coords):
        x, y = self.project_point(coords)[:2]
        return x, y

    def p3(self, *coords):
        x, y, z = self.project_point(coords)[:3]
        return x, y, z

    def project_list(self, point_list):
        '''Projects a list (or list of lists) of points.'''
        if len(point_list) <= 0:
            return np.zeros((0, self.out_dim), dtype)
        point_list = np.atleast_2d(np.asarray(point_list, dtype))
        points = point_list.swapaxes(-1, -2)
        return self.project(points).swapaxes(-1, -2)

    @abc.abstractmethod
    def project(self, points):
        '''Projects a numpy array with points in axis index -2.'''

    def scale_amount_point(self, point):
        '''Calculates the scaling factor of a coordinate due to perspective.'''
        points = np.asarray(point, dtype)[:,np.newaxis]
        return self.scale_amount(points)[..., 0]

    def s(self, *coords):
        return self.scale_amount_point(coords)

    def scale_amount_list(self, point_list):
        '''Calculates the scaling factor of a list of coordinates due to
        perspective.
        '''
        if len(point_list) <= 0:
            return np.zeros((0, self.out_dim), dtype)
        point_list = np.atleast_2d(np.asarray(point_list, dtype))
        points = point_list.swapaxes(-1, -2)
        return self.scale_amount(points)

    @abc.abstractmethod
    def scale_amount(self, points):
        '''Calculates the scaling factor of a numpy array of coordinates due to
        perspective.
        '''


@dataclasses.dataclass(frozen=True)
class LinearProjection(Projection):
    matrix: np.ndarray
    offset: Optional[np.ndarray] = None
    last_output_scale: bool = False

    @property
    def in_dim(self):
        return self.matrix.shape[-1]
    @property
    def out_dim_raw(self):
        return self.matrix.shape[-2]
    @property
    def out_dim(self):
        return self.out_dim_raw - self.last_output_scale

    @property
    def homogeneous_matrix(self):
        mat = np.zeros((self.out_dim+1, self.in_dim+1), dtype)
        mat[:self.matrix.shape[0], :self.matrix.shape[1]] = self.matrix
        if self.offset is not None:
            mat[:self.offset.shape[0], -1] = self.offset
        if not self.last_output_scale:
            mat[-1, -1] = 1
        return mat

    @staticmethod
    def from_homogeneous(homogeneous_matrix):
        if (np.all(homogeneous_matrix[-1, :-1] == 0)
                and homogeneous_matrix[-1, -1] == 1):
            mat = homogeneous_matrix[:-1, :-1]
            off = homogeneous_matrix[:-1, -1]
            last_scale = False
        else:
            mat = homogeneous_matrix[:, :-1]
            off = homogeneous_matrix[:, -1]
            last_scale = True
        if np.all(off == 0):
            off = None
        return LinearProjection(mat, off, last_output_scale=last_scale)

    @staticmethod
    def identity(num_axes):
        return LinearProjection(np.eye(num_axes, dtype=dtype))

    @staticmethod
    def translation(offset):
        offset = np.asarray(offset, dtype)
        return LinearProjection(np.eye(offset.shape[-1], dtype=dtype),
                          offset)

    @staticmethod
    def scaling(scale):
        mat = np.diag(np.array(scale, dtype))
        return LinearProjection(mat)

    @staticmethod
    def rotation(num_axes, i, j, rads):
        mat = np.eye(num_axes, dtype=dtype)
        c, s = np.cos(rads), np.sin(rads)
        mat[[i, i, j, j], [i, j, i, j]] = c, -s, s, c
        return LinearProjection(mat)

    @staticmethod
    def rotation3d(vector, rads):
        # Equation from
        # https://en.wikipedia.org/wiki/Rotation_matrix#Rotation_matrix_from_axis_and_angle
        c, s = np.cos(rads), np.sin(rads)
        vector = np.array(vector, dtype=dtype)
        x, y, z = vector / np.linalg.norm(vector)
        mat = np.array([
            [c+x*x*(1-c), x*y*(1-c)-z*s, x*z*(1-c)+y*s],
            [y*x*(1-c)+z*s, c+y*y*(1-c), y*z*(1-c)-x*s],
            [z*x*(1-c)-y*s, z*y*(1-c)+x*s, c+z*z*(1-c)],
        ], dtype=dtype)
        return LinearProjection(mat)

    def __matmul__(self, right):
        if type(self) != type(right):
            return NotImplemented
        return self._matmul(self, right)

    def __rmatmul__(self, left):
        if type(self) != type(left):
            return NotImplemented
        return self._matmul(left, self)

    @staticmethod
    def _matmul(left, right):
        return LinearProjection.from_homogeneous(
            left.homogeneous_matrix @ right.homogeneous_matrix)

    def rotated(self, i, j, rads):
        return LinearProjection.rotation(self.out_dim, i, j, rads) @ self

    def inverse(self):
        inv = np.linalg.inv(self.homogeneous_matrix)
        return LinearProjection.from_homogeneous(inv)

    def pseudo_inverse(self):
        mat = self.homogeneous_matrix
        inv = np.linalg.inv(mat.T @ mat) @ mat.T
        return LinearProjection.from_homogeneous(inv)

    def project(self, points):
        points = np.asarray(points, dtype)
        projected = relaxed_matmul(self.matrix, points)
        if self.offset is not None:
            projected += self.offset[..., np.newaxis]
        if self.last_output_scale:
            projected /= projected[..., -1, :][..., np.newaxis, :]
            projected = projected[..., :-1, :]
        return projected

    def scale_amount(self, points):
        points = np.asarray(points, dtype)
        if not self.last_output_scale:
            return np.ones(np.swapaxes(points, -2, -1).shape[:-1], dtype)
        projected = relaxed_matmul(self.matrix, points)
        if self.offset is not None:
            projected += self.offset[..., np.newaxis]
        return 1 / projected[..., -1, :]


@dataclasses.dataclass(frozen=True)
class MultiProjection(Projection):
    projections: Tuple[Projection] = ()

    @property
    def in_dim(self):
        return self.projections[-1].in_dim

    @property
    def out_dim(self):
        return self.projections[0].out_dim

    def __matmul__(self, right):
        if not isinstance(right, Projection):
            return NotImplemented
        if type(right) == MultiProjection:
            return MultiProjection(right.projections + self.projections)
        return MultiProjection((right,) + self.projections)

    def __rmatmul__(self, left):
        if not isinstance(left, Projection):
            return NotImplemented
        if type(left) == MultiProjection:
            return MultiProjection(self.projections + left.projections)
        return MultiProjection(right.projections + (left,))

    def project(self, points):
        for proj in self.projections:
            points = proj.project(points)
        return points

    def scale_amount(self, points):
        scale = np.ones(points.shape[-1], dtype)
        for proj in self.projections:
            scale *= proj.scale_amount(points)
            points = proj.project(points)
        return scale


identity = LinearProjection.identity

translation = LinearProjection.translation

scaling = LinearProjection.scaling

rotation = LinearProjection.rotation

rotation3d = LinearProjection.rotation3d

def axis_swap(permutation, scale=None):
    size = len(permutation)
    perm_set = set(permutation)
    if len(perm_set) != size or perm_set != set(range(size)):
        raise ValueError('Not a permutation: {!r}'.format(permutation))
    mat = np.zeros((size, size), dtype)
    if scale is None:
        mat[range(size), permutation] = 1
    else:
        mat[range(size), permutation] = scale
    return LinearProjection(mat)

def axonometric3d(alpha, beta):
    return (LinearProjection.rotation(3, 1, 2, alpha)
            @ LinearProjection.rotation(3, 2, 0, beta))

def isometric3d():
    return axonometric3d(np.arcsin(np.tan(np.pi/6)), -np.pi/4)

def cabinet3d(x_shift=0.125**0.5, y_shift=0.125**0.5):
    matrix = np.array([[1, 0, -x_shift],
                       [0, 1, -y_shift],
                       [0, 0, 1]], dtype)
    return LinearProjection(matrix)

def military3d(rotation=np.pi/4):
    swap = axis_swap((2, 0, 1), (-1, -1, 1))
    return (cabinet3d(x_shift=0, y_shift=-1)
            @ LinearProjection.rotation(3, 0, 1, rotation)
            @ swap)

def camera3d(f, z_offset=0, x_offset=0, y_offset=0):
    matrix = np.array([[1, 0, -x_offset/f],
                       [0, 1, -y_offset/f],
                       [0, 0, 1],
                       [0, 0, -1/f]], dtype)
    offset = np.array([(z_offset-f)*x_offset/f, (z_offset-f)*y_offset/f, -1,
                       z_offset/f],
                      dtype)
    return LinearProjection(matrix, offset, last_output_scale=True)

def perspective3d(field_of_view, view_size=2, x_offset=0, y_offset=0):
    z_offset = 1 / np.tan(field_of_view / view_size)
    return camera3d(z_offset, z_offset=z_offset, x_offset=x_offset,
                    y_offset=y_offset)

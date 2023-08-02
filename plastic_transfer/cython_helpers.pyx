from joblib import Parallel, delayed

import numpy as np
cimport numpy as np


cpdef match_ones(const np.int32_t[:] arr1, const np.int32_t[:] arr2):
    """ Match all instances of `1` in the two arrays

    Return `1` for where there is a `1` at the same location in the
    two arrays and `0` otherwise.
    """
    cdef np.int32_t i
    cdef np.int32_t n_elements
    cdef np.int32_t[:] matching_ones_c

    n_elements = arr1.shape[0]
    if n_elements != arr2.shape[0]:
        raise ValueError('Arrays have differing lengths')

    # Create array of zeros and a memory view of it
    matching_ones = np.zeros(n_elements, dtype=np.int32)
    matching_ones_c = matching_ones

    for i in range(n_elements):
        if arr1[i] == 1 and arr2[i] == 1:
            matching_ones_c[i] = 1

    return matching_ones


cpdef find_first_instance_column_indices(const np.int32_t[:, :] var,
                                         const np.int32_t value,
                                         const np.int32_t invalid):
    """ Find column indices corresponding to the first time value appears

    If value isn't found, return the value invalid for that row.
    """
    cdef np.int32_t i
    cdef np.int32_t j
    cdef np.int32_t n_rows
    cdef np.int32_t n_cols
    cdef np.int32_t[:] indices_c

    n_rows = var.shape[0]
    n_cols = var.shape[1]

    # Create array of invalid values and a memory view into it
    indices = np.ones(n_rows, dtype=np.int32) * invalid
    indices_c = indices

    for i in range(n_rows):
        for j in range(n_cols):
            if var[i, j] == value:
                indices_c[i] = j
                break

    return indices


cdef void cython_match_elements(int* hosts, int* flags, int* bdy_elements,
                                int m, int n) nogil:
    cdef int i
    cdef int left, right, mid

    for i in range(m):
        host = hosts[i]
        left = 0
        right = n - 1

        if bdy_elements[left] > host or bdy_elements[right] < host:
            continue

        while left <= right:
      
            mid = left + (right - left) // 2
              
            if bdy_elements[mid] == host:
                flags[i] = 1
                break
            elif bdy_elements[mid] < host:
                left = mid + 1
            else:
                right = mid - 1
              

cpdef cython_match_elements_wrapper(np.ndarray hosts, np.ndarray flags,
                                    np.ndarray bdy_elements):
    cdef int* hosts_ptr = <int*> hosts.data
    cdef int* flags_ptr = <int*> flags.data
    cdef int* bdy_elements_ptr = <int*> bdy_elements.data
    cdef int m = hosts.shape[0]
    cdef int n = bdy_elements.shape[0]

    if m != flags.shape[0]:
        raise ValueError('Shape of hosts and flags arrays do not match')

    with nogil:
        cython_match_elements(hosts_ptr, flags_ptr, bdy_elements_ptr, m, n)


def match_elements(hosts, bdy_elements, num_threads=16):
    flags = np.zeros_like(hosts, dtype=np.int32)

    hosts_split = np.array_split(hosts, num_threads)  
    flags_split = np.array_split(flags, num_threads)  
    
    with Parallel(n_jobs=num_threads, backend='threading') as parallel:
        parallel([delayed(cython_match_elements_wrapper)(hosts_split[i],
                  flags_split[i], bdy_elements) for i in range(num_threads)])

    # Join the arrays
    return np.concatenate(flags_split)    
 

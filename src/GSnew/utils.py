import numpy as np
from elements import Element, G1Element, G2Element, ZpElement
import json


def load_element_macro(element_string, element_type):
    # Fortunately, charm doesn't need to know the element type
    return f"Element.from_json({element_string})"

def load_crs(new=None, filename='crs.json'):
    try:
        with open(filename, 'r') as f:
            crs = CRS.from_json(json.load(f))
    except FileNotFoundError:
        if new == 'sound':
            crs = CRS.new_sound()
        elif new == 'wi':
            crs = CRS.new_wi()
        else:
            raise Exception('CRS not valid')
    return crs

def random_zp(a,b):
    return np.array([[ZpElement.random() for _ in range(b)] for _ in range(a)])

class CRS():
    def __init__(self, u1, u2, v1, v2, trapdoor=None):
        self._u1 = u1
        self._u2 = u2
        self._v1 = v1
        self._v2 = v2
        
    def iota_1(self, x: G1Element):
        return np.array([G1Element.zero(), x])
        
    def iota_prime_1(self, x: ZpElement):
        u = self.u2 + np.array([G1Element.zero(), g1])
        return x * u
        
    def iota_2(self, y: G2Element):
        return np.array([G2Element.zero(), y])
        
    def iota_prime_2(self, y: ZpElement):
        v = self.v2 + np.array([G2Element.zero(), g2])
        return y * v

    @property
    def u(self):
        return np.array([self._u1, self._u2])

    @property
    def v(self):
        return np.array([self._v1, self._v2])
    
    @property
    def u1(self):
        return np.array([self._u1])
    
    @property
    def u2(self):
        return np.array([self._u2])
    
    @property
    def v1(self):
        return np.array([self._v1])
    
    @property
    def v2(self):
        return np.array([self._v2])

    @staticmethod
    def from_json(json_string):
        u1 = np.array([G1Element.from_json(json_string['u1'][0]), G1Element.from_json(json_string['u1'][1])])
        u2 = np.array([G1Element.from_json(json_string['u2'][0]), G1Element.from_json(json_string['u2'][1])])
        v1 = np.array([G2Element.from_json(json_string['v1'][0]), G2Element.from_json(json_string['v1'][1])])
        v2 = np.array([G2Element.from_json(json_string['v2'][0]), G2Element.from_json(json_string['v2'][1])])
        return CRS(u1, u2, v1, v2)

    @staticmethod
    def new_sound(trapdoor=None):
        if  not trapdoor:
            trapdoor = {'alpha1': ZpElement.random(),
                        'alpha2': ZpElement.random(),
                        't1': ZpElement.random(),
                        't2': ZpElement.random()}
            
        alpha1 = trapdoor['alpha1']
        alpha2 = trapdoor['alpha2']
        t1 = trapdoor['t1']
        t2 = trapdoor['t2']

        u_1 = np.array([g1, alpha1 * g1])
        v_1 = np.array([g2, alpha2 * g2])
        u_2 = t1 * u_1
        v_2 = t2 * v_1
        
        return CRS(u_1, u_2, v_1, v_2, trapdoor=trapdoor)

    @staticmethod
    def new_wi(trapdoor=None):
        if  not trapdoor:
            trapdoor = {'alpha1': ZpElement.random(),
                        'alpha2': ZpElement.random(),
                        't1': ZpElement.random(),
                        't2': ZpElement.random()}
            
        alpha1 = trapdoor['alpha1']
        alpha2 = trapdoor['alpha2']
        t1 = trapdoor['t1']
        t2 = trapdoor['t2']

        u_1 = np.array([g1, alpha1 * g1])
        v_1 = np.array([g2, alpha2 * g2])
        u_2 = t1 * u_1 - np.array([G1Element.zero(), g1])
        v_2 = t2 * v_1 - np.array([G2Element.zero(), g2])
        
        return CRS(u_1, u_2, v_1, v_2, trapdoor=trapdoor)
        



def extended_pair(a, b):
    # Check that a and b have dimension 2
    if a.shape != (2,) or b.shape != (2,):
        raise ValueError(f"Invalid dimensions: a.shape={a.shape}, b.shape={b.shape}")
    return np.array( [a[0].pair(b[0]), a[1].pair(b[0]), a[0].pair(b[1]), a[1].pair(b[1])] )


def pair(a, b):
    return a.pair(b)

class CustomArray(np.ndarray):
    def __new__(cls, input_array):
        obj = np.asarray(input_array).view(cls)
        #obj.func = func  # Save the custom function to apply
        return obj

    def matfunc(self, other, func):
        if self.shape[1] != other.shape[0]:
            raise ValueError("Shapes are not aligned for matrix operation")
        
        # Define the result array
        result = np.zeros((self.shape[0], other.shape[1]), dtype=self.dtype)
        
        # Apply the function `f` to each multiplication step
        for i in range(self.shape[0]):
            for j in range(other.shape[1]):
                result[i, j] = sum(func(self[i, k], other[k, j]) for k in range(self.shape[1]))
        
        return result
    
    def e(self, other):
        func = pair
        return self.matfunc(other, func)
    
    def E(self, other):
        func = extended_pair
        return self.matfunc(other, func)
    
    
class NamedArray(np.ndarray):
    def __new__(cls, input_data):
        # Extract the data, names, and element types from the input tuples
        names = [item[0] for item in input_data]
        data = [item[1] for item in input_data]
        
        # Create the ndarray
        obj = np.asarray(data).view(cls)
        # Store the names and element types as instance attributes
        obj.names = names
        return obj

    def __array_finalize__(self, obj):
        if obj is None: return
        self.names = getattr(obj, 'names', None)

    def __getitem__(self, key):
        if isinstance(key, str):
            index = self.names.index(key)
            return super().__getitem__(index)
        else:
            return super().__getitem__(key)

    def __setitem__(self, key, value):
        if isinstance(key, str):
            index = self.names.index(key)
            super().__setitem__(index, value)
        else:
            super().__setitem__(key, value)
    
    def __sum__(self, other):
        if self.size == 0:
            return other
        if other.size == 0:
            return self
        return super().__sum__(other)
            
    def iota_1(self, crs):
        # Returns a NamedArray with same names and iota_1 applied to each element
        return NamedArray([(name, crs.iota_1(element)) for name, element in zip(self.names, self)])
            
    def iota_prime_1(self, crs):
        # Returns a NamedArray with same names and iota_prime_1 applied to each element
        return NamedArray([(name, crs.iota_prime_1(element)) for name, element in zip(self.names, self)])
            
    def iota_2(self, crs):
        # Returns a NamedArray with same names and iota_2 applied to each element
        return NamedArray([(name, crs.iota_2(element)) for name, element in zip(self.names, self)])
            
    def iota_prime_2(self, crs):
        # Returns a NamedArray with same names and iota_prime_2 applied to each element
        return NamedArray([(name, crs.iota_prime_2(element)) for name, element in zip(self.names, self)])
        
            
    def __json__(self):
        # Create a list of dicts with 'name' and 'value'
        return {name: value for name, value in zip(self.names, self.tolist())}
    
    def append(self, name, value, is_b=False):
        """Appends a new element with a given name and value."""
        # Add the new name
        self.names.append(name)
        # Create a new array with the appended value
        if is_b:
            # Handle empty NamedArray case
            if self.size == 0:
                new_array = np.array([value], ndmin=2)
            else:
                new_array = np.vstack([self, np.array(value, ndmin=2)])
        else:
            new_array = np.append(self, value)
        # View the new array as a NamedArray and update the names
        #if is_b:
        #    return NamedArray([(n, v) for n, v in zip(self.names, [new_array])])
        return NamedArray([(n, v) for n, v in zip(self.names, new_array)])
    
    def b_pair(self, other):
        if self.shape[0] != other.shape[0]:
            raise ValueError("Shapes are not aligned for matrix operation")
        if self.size == 0 or other.size == 0:
            return UnamedArray(np.empty((0, 4), dtype=object))
        if self.shape[1] != 2 or other.shape[1] != 2:
            raise ValueError(f"Invalid dimensions for b_pair: self.shape={self.shape}, other.shape={other.shape}")
        gt_array = np.array([np.array([l[0].pair(r[0]),
                             l[0].pair(r[1]),
                             l[1].pair(r[0]),
                             l[1].pair(r[1])]) for l,r in zip(self, other)])
        return UnamedArray(np.prod(gt_array,0))

    # Optional: Define a custom JSON encoder to handle NamedArray objects
    class NamedArrayEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, NamedArray):
                return obj.__json__()
            if isinstance(obj, Element):
                return obj.__json__()
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return super().default(obj)
        
class UnamedArray(np.ndarray):
    def __new__(cls, input_data):
        # Extract the data, names, and element types from the input tuples
        data = input_data
        
        # Create the ndarray
        obj = np.asarray(data).view(cls)
        return obj

    def __getitem__(self, key):
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
            
    def iota_1(self, crs):
        return UnamedArray([crs.iota_1(element) for element in self])
            
    def iota_prime_1(self, crs):
        return UnamedArray([crs.iota_prime_1(element) for element in self])
            
    def iota_2(self, crs):
        return UnamedArray([crs.iota_2(element) for element in self])
            
    def iota_prime_2(self, crs):
        return UnamedArray([crs.iota_prime_2(element) for element in self])
            
    def __json__(self):
        return self.tolist()
    
    def append(self, value):
        """Appends a new element with a given name and value."""
        # Create a new array with the appended value
        new_array = np.append(self, value)
        # View the new array as a NamedArray and update the names
        return UnamedArray(new_array)
    
    def __matmul__(self, other):
        if self.size == 0 or other.size == 0:
            other_shape = 0 if len(other.shape) == 1 else other.shape[1]
            return UnamedArray(np.empty((self.shape[0], other_shape), dtype=object))
        return super().__matmul__(other)
    
    def __mul__(self, other):
        if self.size == 0:
            return other
        if other.size == 0:
            return self
        return super().__mul__(other)
    
    def b_pair(self, other):
        if self.shape[0] != other.shape[0]:
            raise ValueError("Shapes are not aligned for matrix operation")
        if self.size == 0 or other.size == 0:
            return UnamedArray(np.empty((0, 4), dtype=object))
        if len(self.shape) == 1 and len(other.shape) == 1:
            gt_array = np.array([np.array([self[0].pair(other[0]),
                                 self[0].pair(other[1]),
                                 self[1].pair(other[0]),
                                 self[1].pair(other[1])])])
            return UnamedArray(np.prod(gt_array,0))
        if self.shape[1] != 2 or other.shape[1] != 2:
            raise ValueError("Invalid dimensions for b_pair")
        gt_array = np.array([np.array([l[0].pair(r[0]),
                             l[0].pair(r[1]),
                             l[1].pair(r[0]),
                             l[1].pair(r[1])]) for l,r in zip(self, other)])
        return UnamedArray(np.prod(gt_array,0))


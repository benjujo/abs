import numpy as np


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
            
    def __json__(self):
        # Create a list of dicts with 'name' and 'value'
        return {name: value for name, value in zip(self.names, self.tolist())}

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
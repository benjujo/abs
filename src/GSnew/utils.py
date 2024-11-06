import numpy as np

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
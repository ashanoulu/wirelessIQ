import time


def timer(f):
    def wrapper(*args, **kw): # To decorate a function with input arguments
        t_start = time.time() # Start timer
        result = f(*args, **kw) # Call function
        t_end = time.time() # End timer
        return result, t_end-t_start # Return the result AND the execution time
    return wrapper
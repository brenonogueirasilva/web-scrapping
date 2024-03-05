from google.api_core.exceptions import GoogleAPIError
import logging

def decorator_try_except(func):
    """
    A decorator for exception handling in class methods.

    This decorator wraps a class method and captures exceptions of type `GoogleAPIError`.
    If an exception occurs, it is logged as an error using the logging library.
    """
    def try_func(self, *args):
        try:
            return func(self, *args)
        except GoogleAPIError as e:
            print( f"ERROR {e}" ) 
    return try_func


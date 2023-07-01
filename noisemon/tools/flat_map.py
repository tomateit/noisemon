from typing import Callable, Sequence, List, Any, Union
from typing import TypeVar
T = TypeVar('T')  

def flat_map(function: Callable, seq: List, in_recursion=False) -> List:
    """
    Applies function to each element of seq which is not list
    Elements can have arbitrary nesting
    """
    buffer = []
    for item in seq:
        if type(item) == list:
            buffer.append(flat_map(function, item, in_recursion=True))
        else:
            buffer.append(function(item))
    return buffer

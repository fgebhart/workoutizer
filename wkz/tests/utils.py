from tenacity import retry, wait_exponential, stop_after_attempt

from wkz import configuration


@retry(
    wait=wait_exponential(multiplier=3, min=1, max=5),
    stop=stop_after_attempt(configuration.number_of_retries),
)
def delayed_condition(func, operator, right) -> bool:
    """
    Helper function to check if a function evaluates to given value with a fixed number of retries.
    """
    if operator(func(), right):
        return True
    else:
        raise Exception

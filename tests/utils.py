from tenacity import retry, stop_after_attempt, wait_exponential


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=3, min=1, max=5),
    stop=stop_after_attempt(3),
)
def delayed_assertion(func, operator, result):
    """
    Helper function to check if a function evaluates to given value with a fixed number of retries.
    """
    assert operator(func(), result), f"function: {func} did not return a result which is {operator} {result}"

from tenacity import retry, wait_exponential, stop_after_attempt


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=3, min=1, max=5),
    stop=stop_after_attempt(3),
)
def delayed_assertion(func, operator, right):
    """
    Helper function to check if a function evaluates to given value with a fixed number of retries.
    """
    assert operator(func(), right)

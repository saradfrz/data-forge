import time

def retry(operation, exceptions, attempts=3, delay=0.25):
    """Retry explicitly transient exceptions only; never swallow a final failure."""
    for attempt in range(attempts):
        try:
            return operation()
        except exceptions:
            if attempt + 1 == attempts:
                raise
            time.sleep(delay * 2 ** attempt)

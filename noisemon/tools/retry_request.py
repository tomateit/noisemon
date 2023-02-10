from urllib.error import HTTPError
from noisemon.logger import logger
from time import sleep


def retry_request(function):
    DEFAULT_TIMEOUT = 5
    timeout = 5

    def retried_function(*args, **kwargs):
        nonlocal timeout
        try:
            timeout = DEFAULT_TIMEOUT
            return function(*args, **kwargs)

        except HTTPError as e:
            if e.code == 429:
                timeout += 5
                logger.debug(f"Encountered 429. Gonna sleep for {timeout} and retry")
                sleep(timeout)
                return retried_function(*args, **kwargs)
            elif e.code == 403:
                timeout += 5
                logger.debug(f"Encountered 403. Gonna sleep for {timeout} and retry")
                sleep(timeout)
                return retried_function(*args, **kwargs)
            else:
                raise

    return retried_function

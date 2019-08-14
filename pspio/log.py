# Standard library
import logging

__all__ = ['logger']

Logger = logging.getLoggerClass()


class PSPLogger(Logger):

    def _set_defaults(self):
        """
        Reset logger to its initial state
        """

        # Remove all previous handlers
        for handler in self.handlers[:]:
            self.removeHandler(handler)

        # Set default level
        self.setLevel(logging.INFO)

        # Set up the stdout handler
        sh = logging.StreamHandler()
        self.addHandler(sh)


logging.setLoggerClass(PSPLogger)
logger = logging.getLogger('psp')
logger._set_defaults()

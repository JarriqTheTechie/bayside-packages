import logging

class QLog:
    def __init__(self, logger_name='my_logger', level=logging.DEBUG):
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(level)

        # Configure the console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        # Create a basic formatter and add it to the console handler
        formatter = logging.Formatter('%(levelname)s / %(asctime)s / ***** %(message)s *****')
        console_handler.setFormatter(formatter)

        # Add the console handler to the logger
        self.logger.addHandler(console_handler)

    def debug(self, message):
        self.logger.debug(message)
        return self

    def info(self, message):
        self.logger.info(message)
        return self

    def warning(self, message):
        self.logger.warning(message)
        return self

    def error(self, message):
        self.logger.error(message)
        return self

    def critical(self, message):
        self.logger.critical(message)
        return self

    def exception(self, message):
        self.logger.exception(message)
        return self
import logging

def configure_logging():
    # Define the logging configuration
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )

    # Create a logger instance
    logger = logging.getLogger("quiet_riot")
    return logger

# Example usage
if __name__ == "__main__":
    logger = configure_logging()
    logger.info("Logging is configured.")

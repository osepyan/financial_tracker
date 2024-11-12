import logging

def configure_logging(level: int = logging.INFO) -> None:
    """Set unified log output according to the settings."""
    logging.basicConfig(
        level=level,
        datefmt="%Y-%m-%d %H:%M:%S",
        format="[%(asctime)s.%(msecs)03d] %(module)-15s: %(lineno)03d %(levelname)-7s - %(message)s",
        handlers=[
            logging.FileHandler("app.log"),
            logging.StreamHandler()
        ]
    )


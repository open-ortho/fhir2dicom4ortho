import logging
from fhir2dicom4ortho import logger
from fhir2dicom4ortho.args_cache import ArgsCache
from fhir2dicom4ortho import verbosity_mapping

def setup_logging(level):
    """Configure root logger for the application"""
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Configure format for all handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s.%(funcName)s: %(message)s')
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

def fhir_api():
    args = ArgsCache.get_arguments()
    setup_logging(verbosity_mapping[args.verbosity])
    logger.debug(("Logging Level is {}".format(
        logger.getEffectiveLevel())))

    import uvicorn
    logger.info(f"Lighting a FHIR API on {args.fhir_listen}:{args.fhir_port}")
    uvicorn.run("fhir2dicom4ortho.fhir_api:fhir_api_app", host=args.fhir_listen, port=args.fhir_port)


if __name__ == "__main__":
    fhir_api()
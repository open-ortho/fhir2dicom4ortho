from PIL import Image
from io import BytesIO
from fhir.resources.binary import Binary
from fhir.resources.basic import Basic
from pydicom import Dataset, dcmread
from fhir2dicom4ortho import logger

def convert_binary_to_image(binary: Binary) -> Image:
    """ Convert a FHIR Binary resource to a PIL Image object.
    
    Initially written to pass the PIL to dicom4ortho, but it is better to pass the raw bytes.
    
    If not used, remove.
    """
    image_data = binary.data

    logger.debug(f"Decoded image data length: {len(image_data)}")
    logger.debug(f"Content type: {binary.contentType}")
    logger.debug(f"First 20 bytes of image data: {image_data[:20]}")

    # Create a BytesIO stream from the decoded data
    image_stream = BytesIO(image_data)

    # Open the image using PIL
    image = Image.open(image_stream)
    logger.debug(f"Image format: {image.format}")
    # If the content type is provided, use it to establish the kind of image
    if binary.contentType:
        image_format = binary.contentType.split('/')[-1].upper()
        logger.debug(f"Image format: {image_format}")
        image.format = image_format

    return image

def translate_all_scheduled_protocol_codes_to_opor(dataset: Dataset) -> Dataset:
    """ Translate Codes to OPOR
    
    Translate all the codes in the dataset to OPOR codes by looking up in the terminology server.
    """
    if 'ScheduledProcedureStepSequence' in dataset:
        for step in dataset.ScheduledProcedureStepSequence:
            if 'ScheduledProtocolCodeSequence' in step:
                for code in step.ScheduledProtocolCodeSequence:
                    if code.CodingSchemeDesignator != '99OPOR':
                        new_code = translate_code_to_opor(code)
                        step.ScheduledProtocolCodeSequence.remove(code)
                        step.ScheduledProtocolCodeSequence.append(new_code)
    return dataset

def get_opor_code_value_from_code(image_type_code):
    """ Get OPOR Code Value from Code
    
    Pass whatever code came from the get_code_from_mwl function, and return the CodeValue if the CodingSchemeDesignator is '99OPOR'. Otherwise, look up in the terminology server.
    """
    if image_type_code:
        if hasattr(image_type_code, 'CodingSchemeDesignator'):
            if image_type_code.CodingSchemeDesignator == "99OPOR":
                if hasattr(image_type_code, 'CodeValue'):
                    logger.debug(f"Code is a valid OPOR code: {image_type_code.CodeValue}")
                    image_type = image_type_code.CodeValue
                    return image_type
            else:
                logger.info("Code is not a valid OPOR code. Looking up in the terminology server...")
                return translate_code_to_opor(image_type_code)
        else:
            logger.warning("CodingSchemeDesignator is missing or does not match '99OPOR'.")
    else:
        logger.warning("image_type_code is None.")


def translate_code_to_opor(code:Dataset) -> Dataset:
    ''' Translate Code to OPOR
    
    Translate a code to an OPOR code by looking up in the terminology server.

    Assumes code is a valid DICOM Code, with CodeValue, CodeMeaning, and CodeSchemeDesignator.
    '''
    # TODO: Implement this function
    logger.warning(f"Translate Code: Function not implemented. Returning whatever code {code.CodeValue} was passed.")
    return code

    
def convert_binary_to_dataset(binary: Binary) -> Dataset:
    """ Convert a FHIR Binary resource to a pydicom Dataset object."""
    # Decode the base64 data
    dicom_data = binary.data

    # Create a BytesIO stream from the decoded data
    dicom_stream = BytesIO(dicom_data)

    # Read the DICOM dataset from the stream
    dataset = dcmread(dicom_stream)

    return dataset
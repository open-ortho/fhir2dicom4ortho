""" Module for processing tasks from FHIR resources to DICOM images and sending them to PACS. """
from fhir.resources.bundle import Bundle
from fhir.resources.binary import Binary
from fhir.resources.imagingstudy import ImagingStudy

from dicom4ortho.controller import OrthodonticController
from dicom4ortho.m_orthodontic_photograph import OrthodonticPhotograph
# from fhir2dicom4ortho.task_store import TaskStore # Cannot import TaskStore for circular import

from fhir2dicom4ortho.utils import convert_binary_to_dataset, translate_all_scheduled_protocol_codes_to_opor
from fhir2dicom4ortho import logger, args_cache

TASK_DRAFT = "draft"
TASK_RECEIVED = "received"
TASK_COMPLETED = "completed"
TASK_REJECTED = "rejected"
TASK_FAILED = "failed"
TASK_INPROGRESS = "in-progress"

def _build_dicom_image(bundle:Bundle, task_id, task_store)-> OrthodonticPhotograph:
    """ Build a DICOM image from a FHIR Bundle containing a Binary image, Binary DICOM MWL, a Basic with code..
    """
    logger.debug("Extracting Binary resources")
    image_binary = None
    dicom_binary = None
    imagingstudy = None

    for entry in bundle.entry:
        resource = entry.resource
        if isinstance(resource, Binary):
            if resource.contentType.startswith("image/"):
                image_binary = resource
            elif resource.contentType == "application/dicom":
                dicom_binary = resource
        elif isinstance(resource, ImagingStudy):
            imagingstudy = ImagingStudy.model_validate(resource)

    if not image_binary or not dicom_binary or not imagingstudy:
        task_store.modify_task_status(task_id, TASK_REJECTED)
        raise ValueError("Invalid Bundle: Must contain one image Binary, one DICOM Binary and one ImagingStudy.")

    logger.debug("Converting Binary resources to image and dataset")
    # image = convert_binary_to_image(image_binary)
    mwl_dataset = convert_binary_to_dataset(dicom_binary)
        
    # logger.debug("Getting proper 99OPOR image type code from MWL")
    mwl_dataset = translate_all_scheduled_protocol_codes_to_opor(mwl_dataset)

    logger.debug("Building OrthodonticPhotograph")
    try:
        series0 = imagingstudy.series[0]
        instance0 = series0.instance[0]
    except (IndexError, AttributeError) as e:
        raise ValueError("Invalid ImagingStudy: Must contain at least one Series and one Instance.") from e

    series0_number = None
    if hasattr(series0, 'number'):
        series0_number = series0.number

    series0_uid = None
    if hasattr(series0, 'uid'):
        series0_uid = series0.uid

    started = None
    if hasattr(imagingstudy, 'started'):
        started = imagingstudy.started

    instance0_uid = None
    if hasattr(instance0, 'uid'):
        instance0_uid = instance0.uid

    instance0_number = None
    if hasattr(instance0, 'number'):
        instance0_number = instance0.number

    orthodontic_photograph:OrthodonticPhotograph = OrthodonticPhotograph(
        sop_instance_uid=instance0_uid,
        input_image_bytes=image_binary.data,
        dicom_mwl=mwl_dataset
    )
        
    logger.debug("Copying MWL tags to OrthodonticPhotograph")
    orthodontic_photograph.copy_mwl_tags(dicom_mwl=mwl_dataset)
    orthodontic_photograph.series_instance_uid = series0_uid
    orthodontic_photograph.series_number = series0_number
    orthodontic_photograph.instance_number = str(instance0_number)
    if started:
        orthodontic_photograph.study_datetime = started
        orthodontic_photograph.series_datetime = started
    orthodontic_photograph.set_dicom_attributes_by_type_keyword()
    orthodontic_photograph.prepare()

    return orthodontic_photograph

def _send_dicom_image(orthodontic_photograph:OrthodonticPhotograph):
    """ Send a DICOM image to PACS
    
    Returns:
        response: Response from PACS. Either a DIMSE response or a WADO response
    """
    logger.debug("Sending OrthodonticPhotograph to PACS")
    controller = OrthodonticController()
    return controller.send(
        send_method=args_cache.pacs_send_method,
        pacs_dimse_hostname=args_cache.pacs_dimse_hostname,
        pacs_dimse_port=args_cache.pacs_dimse_port,
        pacs_dimse_aet=args_cache.pacs_dimse_aet,
        pacs_wado_url=args_cache.pacs_wado_url,
        pacs_wado_username=args_cache.pacs_wado_username,
        pacs_wado_password=args_cache.pacs_wado_password,
        dicom_datasets=[orthodontic_photograph.to_dataset()]
    )


def build_and_send_dicom_image(bundle:Bundle, task_id, task_store):
    """ Build a DICOM image and send it to PACS from a FHIR Bundle containing a Binary image, Binary DICOM MWL, a Basic with code..
    """
    logger.info(f"Processing Task: {task_id}")
    task_store.modify_task_status(task_id, TASK_INPROGRESS)

    try:
        orthodontic_photograph = _build_dicom_image(bundle, task_id, task_store)
        result = _send_dicom_image(orthodontic_photograph)

        task_status = _get_status_from_response(result)

        logger.debug(f"Setting Task status to {task_status}")
        task_store.modify_task_status(task_id, task_status)
        logger.info(f"Task {task_id} {task_status}")
    except Exception as e:
        task_store.modify_task_status(task_id, TASK_FAILED)
        logger.exception(e)
        logger.error(f"Error processing Bundle: {e}")

def _get_status_from_response(response):
    """ Set the status of a task from a response object
    """
    if response is None:
        return TASK_FAILED

    # DICOM DIMSE response
    if "Status" in response:
        if response.Status == 0x0000:
            return TASK_COMPLETED

    # DICOM WADO response
    if "status_code" in response:
        if response.status_code == 200:
            return TASK_COMPLETED
    
    return TASK_FAILED
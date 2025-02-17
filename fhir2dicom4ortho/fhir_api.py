from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fhir.resources.bundle import Bundle, BundleEntry
from fhir.resources.task import Task
from fhir.resources.operationoutcome import OperationOutcome

from fhir2dicom4ortho.scheduler import scheduler
from fhir2dicom4ortho.tasks import build_and_send_dicom_image, TASK_RECEIVED
from fhir2dicom4ortho.task_store import TaskStore
from fhir2dicom4ortho import logger
from fhir2dicom4ortho.args_cache import ArgsCache

fhir_api_app = FastAPI()
_task_store = None

def get_task_store():
    """FastAPI dependency that provides the TaskStore singleton instance"""
    try:
        global _task_store
        if _task_store is None:
            args = ArgsCache.get_arguments()
            _task_store = TaskStore(db_url=args.tasks_db_url)
        return _task_store
    except Exception as e:
        # I'm not sure if this is the best way to handle this error: i can't return a Response object here becuase these are FastAPI dependencies. Should we just not even catch this error?
        logger.error(f"Failed to initialize database: {str(e)}")
        raise e

def create_operation_outcome(severity: str, code: str, diagnostics: str) -> str:
    outcome = OperationOutcome(
        issue=[{
            "severity": severity,
            "code": code,
            "diagnostics": diagnostics
        }]
    )
    return outcome.model_dump_json()

@fhir_api_app.post("/fhir/Bundle")
async def handle_bundle(request: Request, task_store: TaskStore = Depends(get_task_store)):
    try:
        bundle_data = await request.json()
        bundle = Bundle(**bundle_data)
        for entry in bundle.entry:
            if not entry.resource:
                return Response(content=create_operation_outcome("error", "invalid", "Entry must contain a resource"), media_type="application/json", status_code=400)
            resource = entry.resource
            if isinstance(resource, Task):
                task: Task = resource
                break

        # Update Task status resource to represent the job
        task.status = TASK_RECEIVED
        task.description = "Processing Bundle"
        task = task_store.add_task(task)
        # Schedule the job with APScheduler
        job = scheduler.add_job(build_and_send_dicom_image, args=[bundle, task.id, task_store])
        logger.info(f"Job scheduled: {job.id}")

        task_store.modify_task_status(task.id, TASK_RECEIVED)
        return Response(content=task.model_dump_json(), media_type="application/json", status_code=200)

    except Exception as e:
        logger.exception(e)
        return Response(content=create_operation_outcome("error", "exception", str(e)), media_type="application/json", status_code=500)

@fhir_api_app.get("/fhir/Task/{task_id}")
async def get_task_status(task_id: str, task_store: TaskStore = Depends(get_task_store)):
    try:
        task = task_store.get_fhir_task_by_id(task_id)
        if not task:
            return Response(content=create_operation_outcome("error", "not-found", f"Task with ID {task_id} not found"), media_type="application/json", status_code=404)
        return Response(content=task.model_dump_json(), media_type="application/json", status_code=200)
    except Exception as e:
        logger.exception(e)
        return Response(content=create_operation_outcome("error", "exception", str(e)), media_type="application/json", status_code=500)

@fhir_api_app.get("/fhir/Task")
async def list_all_tasks(task_store: TaskStore = Depends(get_task_store)):
    try:
        tasks = task_store.get_all_tasks()
        bundle = Bundle(
            type="searchset",
            total=len(tasks),
            entry=[BundleEntry(resource=task) for task in tasks]
        )
        return Response(content=bundle.model_dump_json(), media_type="application/json", status_code=200)
    except Exception as e:
        logger.exception(e)
        return Response(content=create_operation_outcome("error", "exception", str(e)), media_type="application/json", status_code=500)
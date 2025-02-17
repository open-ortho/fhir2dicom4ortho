# tests/test_pacs.py
#
# End to End tests, complete processes. These are slow.
#
import test
import unittest
from logging import DEBUG
from time import sleep
from fhir.resources.bundle import Bundle
from fastapi.testclient import TestClient
from contextlib import contextmanager
import os

from fhir2dicom4ortho.fhir_api import fhir_api_app, get_task_store
from fhir2dicom4ortho.tasks import TASK_COMPLETED, TASK_FAILED, build_and_send_dicom_image
from fhir2dicom4ortho.task_store import TaskStore
from fhir2dicom4ortho import logger
from fhir2dicom4ortho.entry_points import setup_logging

class TestFHIRAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        setup_logging(DEBUG)
        
        # Create test-specific TaskStore
        cls.task_store = TaskStore(db_url='sqlite:///:memory:')
        
        # Override FastAPI dependency
        def get_test_task_store():
            return cls.task_store
        
        fhir_api_app.dependency_overrides[get_task_store] = get_test_task_store
        
        # Initialize test client
        cls.client = TestClient(fhir_api_app)
        cls.bundle = Bundle.model_validate(test.test_bundle)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'task_store'):
            cls.task_store.cleanup()
        # Clear dependency override
        fhir_api_app.dependency_overrides.clear()

    def setUp(self):
        self.task_store = self.__class__.task_store

    def tearDown(self):
        # Clean up any tasks created during the test
        if hasattr(self, 'task_store'):
            self.task_store.cleanup()

    def test_handle_bundle(self):
        """ Tests both Bundle and Task endpoints.

        - Sent test_bundle to the FHIR API: the system should accept it.
        - Check that the system accepte it with the response 200
        - As soon as it is accepted, the status should be "draft". Check the resopnse for the status of the Task to be "draft"
        - The system should generate the DICOM and try to send the image to the PACS server. Wait 1 second for the Task to complete
        - Query the Task endpoint to check the status of the Task to be either "completed" or "failed".

        This test does not test the actual sending of the DICOM image to the PACS server, so the orthanc-mock server is not necessary. It will try to send, and either log success or failure. Both will pass the test.
        """
        response = self.client.post("/fhir/Bundle", json=test.test_bundle)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn("status", response_data)
        self.assertEqual(response_data["status"], "draft")
        
        print("********** Waiting for Task to Complete... **********")
        sleep(1)
        
        response = self.client.get(f"/fhir/Task/{response_data['id']}")
        response_data = response.json()
        self.assertIn(response_data["status"], [TASK_COMPLETED, TASK_FAILED])

    def test_process_bundle_task(self):
        """ Test requires mock PACS server

        cd test/
        docker compose up -d 


        """
        try:
            task_id = self.task_store.reserve_id(description=self._testMethodName)
            build_and_send_dicom_image(self.bundle, task_id, self.task_store)

            task = self.task_store.get_fhir_task_by_id(task_id)
            self.assertIsNotNone(task)
            if task.status != TASK_COMPLETED:
                logger.error(f"Task failed with status {task.status}")
                logger.error(f"Environment: DIMSE_AET={os.getenv('F2D4O_PACS_DIMSE_AET')}")
            self.assertEqual(task.status, TASK_COMPLETED)
        except Exception as e:
            logger.exception("Failed to process bundle task")
            raise

    def test_list_all_tasks(self):
        # Create a task to ensure there's at least one
        self.task_store.reserve_id(description="Test task for listing")
        
        response = self.client.get("/fhir/Task")
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        bundle = Bundle.model_validate(response_data)
        self.assertGreater(len(bundle.entry), 0, "The bundle should contain at least one entry")
        self.assertGreater(bundle.total, 0)

if __name__ == '__main__':
    unittest.main()

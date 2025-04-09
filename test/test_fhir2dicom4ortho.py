import os
import test
from fhir2dicom4ortho.task_store import TaskStore
from fhir2dicom4ortho.tasks import _build_dicom_image, TASK_DRAFT, TASK_COMPLETED, TASK_FAILED, TASK_REJECTED, TASK_INPROGRESS
from fhir.resources.bundle import Bundle
from dicom4ortho.utils import get_scheduled_protocol_code
import unittest
from datetime import datetime, timezone, timedelta
from pydantic import ValidationError

class TestTasks(unittest.TestCase):
    def setUp(self):
        self.task_store = TaskStore(db_url='sqlite:///test_tasks.sqlite')
        self.bundle = Bundle.model_validate(test.test_bundle)

    def test_build_dicom_image(self):
        """ Test the _build_dicom_image function.
        """
        task_id = self.task_store.reserve_id(description=self._testMethodName)
        orthodontic_photograph = _build_dicom_image(self.bundle, task_id, self.task_store)
        self.assertIsNotNone(orthodontic_photograph)

        ds = orthodontic_photograph.to_dataset()
        print(ds)
        code = get_scheduled_protocol_code(ds)
        self.assertIsNotNone(code)
        self.assertEqual(code.CodeValue, "EV20")
        ds.save_as(os.path.join(test.current_dir,"test_build_dicom_image.dcm"))
        self.assertIsNotNone(ds)
        self.assertEqual(ds.InstanceNumber, "00100")
        self.assertEqual(ds.SeriesInstanceUID, "1.3.6.1.4.1.61741.11.2.3.250.184.10.136.8.7")
        self.assertEqual(ds.SOPInstanceUID, "1.3.6.1.4.1.61741.11.2.4.146.2.192.6.158.81")
        self.assertEqual(ds.StudyDate, "20240616")
        self.assertEqual(ds.StudyTime, "140000.000000")

    def test_different_datetime(self):
        test_cases = {
            "2024-06-16T14:00:00Z": ["20240616", "140000.000000"],  # Valid: UTC
            "2024-06-16T14:00:00+0200": ["20240616", "140000.000000"],  # Valid: UTC+2
            "2024-06-16T14:00:00-0500": ["20240616", "140000.000000"],  # Valid: UTC-5
            "2024-06-16T14:00:00+02:00": ["20240616", "140000.000000"],  # Valid: with ISO-8601 offset
            "2024-06-16T14:00:00+1000": ["20240616", "140000.000000"],  # Valid: UTC+10
            "invalid_date": [None, None],  # Invalid: date format
            "2024-06-16T25:00:00Z": [None, None],  # Invalid: time
            "2024-06-16T14:60:00Z": [None, None],  # Invalid: minute
            "2024-06-16T14:00:00": [None, None],  # Invalid: without TZ
            "2024-06-16T14:00": [None, None],  # Invalid: Missing seconds (assumed)
            "2024-06-16T140000Z": [None, None],  # Invalid: without colon in time
        }

        for started, expected in test_cases.items():
            with self.subTest(started=started):
                try:
                    self.bundle.entry[1].resource.started = started

                    task_id = self.task_store.reserve_id(description=self._testMethodName)
                    orthodontic_photograph = _build_dicom_image(self.bundle, task_id, self.task_store)
                    self.assertIsNotNone(orthodontic_photograph)

                    ds = orthodontic_photograph.to_dataset()

                    if expected[0] is not None:
                        self.assertTrue(ds.StudyDate, "StudyDate should be present.")
                        self.assertEqual(ds.StudyDate, expected[0])
                    else:
                        self.assertIsNone(ds.StudyDate, f"StudyDate should be None for started={started}")

                    if expected[1] is not None:
                        self.assertTrue(ds.StudyTime, "StudyTime should be present.")
                        self.assertEqual(ds.StudyTime, expected[1])
                    else:
                        self.assertIsNone(ds.StudyTime, f"StudyTime should be None for started={started}")

                except ValidationError:
                    if expected == [None, None]:
                        continue
                    else:
                        self.fail(f"Validation failed unexpectedly for started={started}")



if __name__ == "__main__":
    unittest.main()

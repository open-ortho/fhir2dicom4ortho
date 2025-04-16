""" Test the fhir2dicom4ortho module. """
import os
import unittest
from pydantic import ValidationError
from fhir.resources.bundle import Bundle

import test
from fhir2dicom4ortho.task_store import TaskStore
from fhir2dicom4ortho.tasks import _build_dicom_image
from dicom4ortho.utils import get_scheduled_protocol_code

class TestTasks(unittest.TestCase):
    """ Test the fhir2dicom4ortho module. """
    def setUp(self):
        self.task_store = TaskStore(db_url='sqlite:///test_tasks.sqlite')
        self.bundle = Bundle.model_validate(test.test_bundle)

    def test_build_dicom_image(self):
        """ 
        Test the `_build_dicom_image` function to ensure it generates a valid DICOM file.

        This test verifies that the DICOM file created from a FHIR Bundle contains all the expected 
        tags and values
        """
        task_id = self.task_store.reserve_id(description=self._testMethodName)
        orthodontic_photograph = _build_dicom_image(self.bundle, task_id, self.task_store)
        self.assertIsNotNone(orthodontic_photograph)

        ds = orthodontic_photograph.to_dataset()
        print(ds)
        code = get_scheduled_protocol_code(ds)
        self.assertIsNotNone(code)
        self.assertEqual(code.CodeValue, "EV20")
        self.assertIsNotNone(ds)
        self.assertEqual(ds.InstanceNumber, "00100")
        self.assertEqual(ds.SeriesInstanceUID, "1.3.6.1.4.1.61741.11.2.3.250.184.10.136.8.7")
        self.assertEqual(ds.SOPInstanceUID, "1.3.6.1.4.1.61741.11.2.4.146.2.192.6.158.81")
        self.assertEqual(ds.StudyDate, "20241115")
        self.assertEqual(ds.StudyTime, "115817.000000")
        self.assertEqual(ds.SeriesDate, "20241116")
        self.assertEqual(ds.SeriesTime, "115849.000000")

        ds.save_as(os.path.join(test.current_dir,"data/test_build_dicom_image.dcm"))

    def test_study_date_timezone(self):
        """
        Test the conversion of the `started` field in the FHIR Bundle to DICOM `StudyDate` and `StudyTime`.

        This test verifies that various timestamp formats in the `started` field of a FHIR Procedure 
        are correctly parsed and converted into valid DICOM `StudyDate` and `StudyTime` fields.

        Valid timestamps in different timezones (UTC, offsets like +0200, -0500, etc.) are expected 
        to be normalized and produce correct DICOM date/time values. Invalid formats or times should 
        result in missing (`None`) `StudyDate` and `StudyTime`.
        """
        # NOTE: data: [studyDate, studyTime]
        test_cases = {
            # Valid
            "2024-06-16T14:00:00Z": ["20240616", "140000.000000"],
            "2024-06-16T14:00:00+0200": ["20240616", "140000.000000"],
            "2024-06-16T14:00:00-0500": ["20240616", "140000.000000"],
            "2024-06-16T14:00:00+02:00": ["20240616", "140000.000000"],
            "2024-06-16T14:00:00+1000": ["20240616", "140000.000000"],
            # Invalid
            "invalid_date": [None, None],
            "2024-06-16T25:00:00Z": [None, None],
            "2024-06-16T14:60:00Z": [None, None],
            "2024-06-16T14:00:00": [None, None],
            "2024-06-16T14:00": [None, None],
            "2024-06-16T140000Z": [None, None],
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
                    # NOTE: If the input is invalid, a validation error is raised.
                    # If the test expects an error (i.e., an invalid date/time), the error is ignored.
                    # Otherwise, an unexpected error is reported.
                    if expected == [None, None]:
                        continue
                    else:
                        self.fail(f"Validation failed unexpectedly for started={started}")



if __name__ == "__main__":
    unittest.main()

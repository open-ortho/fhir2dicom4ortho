""" Test the fhir2dicom4ortho module. """
import os
import test
import unittest

from fhir.resources.bundle import Bundle
from dicom4ortho.utils import get_scheduled_protocol_code

from fhir2dicom4ortho.task_store import TaskStore
from fhir2dicom4ortho.tasks import _build_dicom_image

class TestTasks(unittest.TestCase):
    """ Test the fhir2dicom4ortho module. """
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


if __name__ == "__main__":
    unittest.main()

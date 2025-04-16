import os
import json

os.environ['F2D4O_VERBOSITY'] = '2'
os.environ['F2D4O_FHIR_LISTEN'] = ''
os.environ['F2D4O_FHIR_PORT'] = '8123'
os.environ['F2D4O_PACS_SEND_METHOD'] = 'dimse'
os.environ['F2D4O_PACS_DIMSE_AET'] = 'ORTHANC-MOCK'
os.environ['F2D4O_PACS_DIMSE_IP'] = '127.0.0.1'
os.environ['F2D4O_PACS_DIMSE_PORT'] = '4242'



# Get the directory of the current file
current_dir = os.path.dirname(__file__)

# Construct the path to the JSON file
json_file_path = os.path.join(current_dir, 'data/fhir2dicom4ortho.Bundle.json')
json_instances_path = os.path.join(current_dir, 'data/instances_bundle.json')

# Load the test_bundle from the JSON file
with open(json_file_path, 'r') as f:
    test_bundle = json.load(f)

# Load instance values representing 3 different images
with open(json_instances_path, 'r') as f:
    test_instances = json.load(f)

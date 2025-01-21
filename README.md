[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/open-ortho/fhir2dicom4ortho">
    <img src="https://raw.githubusercontent.com/open-ortho/fhir2dicom4ortho/master/images/open-ortho.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">fhir2dicom4ortho 0.1.0</h3>

  <p align="center">
    A FHIR API Frontend to dicom4ortho.
    <br />
    <a href="https://open-ortho.github.io/fhir2dicom4ortho/"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/open-ortho/fhir2dicom4ortho">View Demo</a>
    ·
    <a href="https://github.com/open-ortho/fhir2dicom4ortho/issues">Report Bug</a>
    ·
    <a href="https://github.com/open-ortho/fhir2dicom4ortho/issues">Request Feature</a>
  </p>
</p>

<!-- TABLE OF CONTENTS -->
- [About The Project](#about-the-project)
  - [Built With](#built-with)
- [Building](#building)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
  - [`POST /fhir/Bundle`](#post-fhirbundle)
  - [`GET /fhir/Task/{task_id}`](#get-fhirtasktask_id)
  - [`GET /fhir/Task`](#get-fhirtask)
- [Known Issues](#known-issues)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
  - [Development](#development)
  - [requirement.txt](#requirementtxt)
- [Building the FHIR Bundle](#building-the-fhir-bundle)
  - [Example FHIR Bundle](#example-fhir-bundle)
    - [Task Resource](#task-resource)
    - [ImagingStudy Resource](#imagingstudy-resource)
    - [Binary (DICOM MWL) Resource](#binary-dicom-mwl-resource)
    - [Binary (Image File) Resource](#binary-image-file-resource)
  - [Constructing the Bundle](#constructing-the-bundle)
- [License](#license)
- [Contact](#contact)
- [Acknowledgements](#acknowledgements)


## About The Project

TODO

### Built With

* [dicom4ortho](https://github.com/open-ortho/dicom4ortho/)
* [fhir.resource]
* [fastapi]

## Building

    poetry install

## Getting Started

### Prerequisites

    Poetry

### Installation

    # Install Poetry
    curl -sSL https://install.python-poetry.org | python3 -

    # or install with pipx

    # Install dependencies
    poetry install

    # Activate the virtual environment
    poetry shell

<!-- USAGE EXAMPLES -->
## Usage

TODO

## API Endpoints

The `fhir2dicom4ortho` project implements a partial set of FHIR API endpoints to interact with DICOM Orthodontic imaging studies. Below are the currently implemented endpoints along with their functionalities and references to the official FHIR documentation.

### `POST /fhir/Bundle`

**Description:**  
Accepts a FHIR `Bundle` containing `Task`, `ImagingStudy`, and `Binary` resources. Processes the bundle by scheduling the creation and sending of a DICOM image to the PACS server.

**Functionality:**
- Validates the incoming Bundle for required resources.
- Updates the `Task` status to "received".
- Schedules the job using APScheduler.
- Returns the updated `Task` resource.

**FHIR Documentation:**  
[Task Resource](https://www.hl7.org/fhir/task.html)
[ImagingStudy Resource](https://www.hl7.org/fhir/imagingstudy.html)
[Binary Resource](https://www.hl7.org/fhir/binary.html)
[Bundle Resource](https://www.hl7.org/fhir/bundle.html)

### `GET /fhir/Task/{task_id}`

**Description:**  
Retrieves the status of a specific Task by its `task_id`.

**Functionality:**
- Fetches the `Task` resource corresponding to the provided `task_id`.
- Returns the `Task` resource if found.
- Returns an `OperationOutcome` if the `Task` is not found.

**FHIR Documentation:**  
[Task Resource](https://www.hl7.org/fhir/task.html)
[OperationOutcome Resource](https://www.hl7.org/fhir/operationoutcome.html)

### `GET /fhir/Task`

**Description:**  
Retrieves all existing Tasks.

**Functionality:**
- Fetches all `Task` resources.
- Returns a FHIR `Bundle` containing the list of Tasks.

**FHIR Documentation:**  
[Task Resource](https://www.hl7.org/fhir/task.html)
[Bundle Resource](https://www.hl7.org/fhir/bundle.html)

**Note:**  
The current implementation includes only the above endpoints. Additional endpoints and functionalities could be  planned for future releases to provide better support for FHIR operations.

## Known Issues

Please check the [Implementation Status](docs/IMPLEMENTATION_STATUS.md)
document.

<!-- ROADMAP -->
## Roadmap

See the [open issues](https://github.com/open-ortho/fhir2dicom4ortho/issues) for a list of proposed features (and known issues).

<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a [Pull Request](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request)

### Development

Before development, 
1. `poetry update` to update all dependencies;
2. Run all tests and fix issues caused by update dependecies;
3. Continue development;

### requirement.txt

The `requirements.txt` file is only used for Dependabot, which i think works off of that and not `poetry.lock`. However, the project's dependencies are managed by poetry.

Building a new docker image should trigger the generation of a new `requirements.txt`, which you should then safely commit.

## Building the FHIR Bundle

To operate this API, you need to construct a FHIR Bundle containing specific resources. Below is an example of how to build the required FHIR Bundle, using `fhir2dicom4ortho.Bundle.json` as a reference.

### Example FHIR Bundle

The FHIR Bundle should contain the following resources:

1. **Task**: Describes the task to be performed.
2. **ImagingStudy**: Contains information about the imaging study.
3. **Binary (DICOM MWL)**: Contains the DICOM Modality Worklist (MWL) data.
4. **Binary (Image File)**: Contains the image file data.

#### Task Resource

The Task resource describes the task to be performed, including references to the Binary and ImagingStudy resources.

```json
{
  "resourceType": "Task",
  "id": "task-id",
  "status": "requested",
  "intent": "order",
  "description": "Process DICOM MWL and Image Input",
  "authoredOn": "2024-06-16T14:00:00Z",
  "requester": {
    "reference": "Practitioner/456",
    "display": "Dr. John Doe"
  },
  "for": {
    "reference": "Patient/123",
    "display": "Patient Example"
  },
  "input": [
    {
      "type": {
        "text": "DICOM MWL"
      },
      "valueReference": {
        "reference": "Binary/dicom-mwl-id"
      }
    },
    {
      "type": {
        "text": "Image File"
      },
      "valueReference": {
        "reference": "Binary/image-file-id"
      }
    },
    {
      "type": {
        "text": "Image Study"
      },
      "valueReference": {
        "reference": "ImagingStudy/imaging-study-id"
      }
    }
  ]
}
```

#### ImagingStudy Resource

The ImagingStudy resource contains information about the imaging study, including series and instances.

```json
{
  "resourceType": "ImagingStudy",
  "id": "imaging-study-id",
  "status": "available",
  "subject": {
    "reference": "Patient/123",
    "display": "Patient Example"
  },
  "started": "2024-06-16T14:00:00Z",
  "numberOfSeries": 1,
  "numberOfInstances": 1,
  "series": [
    {
      "uid": "series-uid",
      "number": 7,
      "modality": {
        "coding": [
          {
            "system": "http://dicom.nema.org/resources/ontology/DCM",
            "code": "XC",
            "display": "External-camera Photography"
          }
        ]
      },
      "started": "2024-06-16T14:00:00Z",
      "description": "Sample XC Series",
      "numberOfInstances": 1,
      "instance": [
        {
          "uid": "instance-uid",
          "sopClass": {
            "system": "https://dicom.nema.org/medical/dicom/current/output/chtml/part04/sect_B.5.html#table_B.5-1",
            "code": "1.2.840.10008.5.1.4.1.1.77.1.4.1",
            "display": "VL Photographic Image Storage"
          },
          "number": 100,
          "title": "Sample Orthodontic Image"
        }
      ]
    }
  ]
}
```

#### Binary (DICOM MWL) Resource

The Binary resource containing the DICOM Modality Worklist (MWL) data.

```json
{
  "resourceType": "Binary",
  "id": "dicom-mwl-id",
  "contentType": "application/dicom",
  "data": "base64-encoded-dicom-mwl-data"
}
```

#### Binary (Image File) Resource

The Binary resource containing the image file data.

```json
{
  "resourceType": "Binary",
  "id": "image-file-id",
  "contentType": "image/png",
  "data": "base64-encoded-image-data"
}
```

### Constructing the Bundle

Combine the above resources into a single FHIR Bundle.

```json
{
  "resourceType": "Bundle",
  "type": "batch",
  "entry": [
    {
      "fullUrl": "urn:uuid:task-id",
      "resource": { /* Task resource */ },
      "request": {
        "method": "POST",
        "url": "http://fhir2dicom4ortho/fhir/Bundle"
      }
    },
    {
      "fullUrl": "urn:uuid:imaging-study-id",
      "resource": { /* ImagingStudy resource */ },
      "request": {
        "method": "POST",
        "url": "http://fhir2dicom4ortho/fhir/Bundle"
      }
    },
    {
      "fullUrl": "urn:uuid:dicom-mwl-id",
      "resource": { /* Binary (DICOM MWL) resource */ },
      "request": {
        "method": "POST",
        "url": "http://fhir2dicom4ortho/fhir/Bundle"
      }
    },
    {
      "fullUrl": "urn:uuid:image-file-id",
      "resource": { /* Binary (Image File) resource */ },
      "request": {
        "method": "POST",
        "url": "http://fhir2dicom4ortho/fhir/Bundle"
      }
    }
  ]
}
```

This FHIR Bundle can then be sent to the API to process the DICOM MWL and image input.

<!-- LICENSE -->
## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

<!-- CONTACT -->
## Contact

Toni Magni- [@zgypa](https://twitter.com/zgypa) - open-ortho@afm.co

Project Link: [https://github.com/open-ortho/fhir2dicom4ortho](https://github.com/open-ortho/fhir2dicom4ortho)

<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements

- [DICOM](https://www.webpagefx.com/tools/emoji-cheat-sheet)
- [American Dental Association Standards Committee for Dental Informatics](https://www.ada.org/en/science-research/dental-standards/standards-committee-on-dental-informatics)

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/open-ortho/fhir2dicom4ortho.svg?style=for-the-badge
[contributors-url]: https://github.com/open-ortho/fhir2dicom4ortho/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/open-ortho/fhir2dicom4ortho.svg?style=for-the-badge
[forks-url]: https://github.com/open-ortho/fhir2dicom4ortho/network/members
[stars-shield]: https://img.shields.io/github/stars/open-ortho/fhir2dicom4ortho.svg?style=for-the-badge
[stars-url]: https://github.com/open-ortho/fhir2dicom4ortho/stargazers
[issues-shield]: https://img.shields.io/github/issues/open-ortho/fhir2dicom4ortho.svg?style=for-the-badge
[issues-url]: https://github.com/open-ortho/fhir2dicom4ortho/issues
[license-shield]: https://img.shields.io/github/license/open-ortho/fhir2dicom4ortho.svg?style=for-the-badge
[license-url]: https://github.com/open-ortho/fhir2dicom4ortho/blob/master/LICENSE
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/open-ortho
[product-screenshot]: images/screenshot.png
[example-csv-url]: resources/example/input_from.csv

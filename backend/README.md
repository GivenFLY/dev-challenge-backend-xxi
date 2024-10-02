# Backend Service

## Overview

The Backend Service is the core component of the MFA Ukraine Call Processing System. It provides RESTful APIs for managing conversation categories and processing audio calls. This service orchestrates interactions between the Speech to Text (STT) Service and the Categorization Service to transform raw audio data into structured, analyzable information. By handling CRUD operations for conversation categories and managing the lifecycle of call processing, the Backend Service ensures seamless data flow and integration across the system.

## Features

- **RESTful API:** Provides endpoints for managing categories and processing calls.
- **Category Management:** Create, read, update, and delete conversation topics.
- **Call Processing:** Submit audio files for transcription and categorization.
- **Integration with STT and Categorization Services:** Coordinates tasks between services to extract and analyze call data.
- **Asynchronous Processing:** Ensures efficient handling of large volumes of audio data.
- **Dockerized Deployment:** Simplifies setup and scalability using Docker Compose.

## Corner Cases Covered

- **Invalid Audio URLs or Formats:** The system validates the `audio_url` to ensure it points to a supported file format and is accessible.
- **Concurrent Requests:** Implements asynchronous processing to handle multiple call submissions simultaneously without performance degradation.
- **Category Updates:** When updating a category, the system re-evaluates existing conversations to ensure they still belong to the updated category.
- **Data Extraction Failures:** Handles scenarios where extracting `name` or `location` from the call fails, returning `null` for those fields.
- **Service Availability:** Returns appropriate error messages if dependent services (STT or Categorization) are unavailable.

## Running with Docker Compose

Ensure all services are defined in the `docker-compose.yml` file. To build and run the Backend Service along with its dependencies:

```bash
docker-compose up --build backend
```

This command will:

- Build the Backend Service Docker image.
- Start the Backend Service, Speech to Text Service, and Categorization Service.
- Expose the Backend API at `http://localhost:8080/api`.

## API Documentation

### Base URL

```
http://localhost:8080/api
```

### Category Management

Manage conversation topics through the following endpoints.

#### GET `/category`
**Description:** Retrieve a list of all conversation topics.

**Response:**

- **Status Code:** `200 OK`
- **Body:**

  ```json
  [
    {
      "id": "category_id_1",
      "title": "Visa and Passport Services",
      "points": ["Border crossing", "International documentation"]
    },
    {
      "id": "category_id_2",
      "title": "Diplomatic Inquiries",
      "points": ["Embassy support", "International relations"]
    }
    // ... other categories
  ]
  ```

#### POST `/category`
**Description:** Create a new conversation topic. Will create a task for zero-shot classification to evaluate all processed calls and assign them to the new category if they match.

**Request:**

- **Headers:** `Content-Type: application/json`
- **Body:**

  ```json
  {
    "title": "Topic Title",
    "points": ["Key Point 1", "Key Point 2"]
  }
  ```

**Response:**

- **Success:**
  - **Status Code:** `201 Created`
  - **Body:**

    ```json
    {
      "id": "new_category_id",
      "title": "Topic Title",
      "points": ["Key Point 1", "Key Point 2"]
    }
    ```

- **Error:**
  - **Status Code:** `422 Unprocessable Entity`
  - **Body:**

    ```json
    {
      "detail": "Validation error message."
    }
    ```

#### PUT `/category/{category_id}`

**Description:** Update an existing conversation topic.

**Request:**

- **Headers:** `Content-Type: application/json`
- **Body:**

  ```json
  {
    "title": "New Topic Title",
    "points": ["New Key Point 1", "New Key Point 2"]
  }
  ```

**Response:**

- **Success:**
  - **Status Code:** `200 OK`
  - **Body:**

    ```json
    {
      "id": "category_id",
      "title": "New Topic Title",
      "points": ["New Key Point 1", "New Key Point 2"]
    }
    ```

- **Error:**
  - **Status Code:** `422 Unprocessable Entity`
  - **Body:**

    ```json
    {
      "detail": "Validation error message."
    }
    ```

#### DELETE `/category/{category_id}`

**Description:** Delete a conversation topic by its identifier.

**Response:**

- **Success:**
  - **Status Code:** `200 OK`
  - **Body:**

    ```json
    {
      "message": "Category deleted successfully."
    }
    ```

- **Error:**
  - **Status Code:** `404 Not Found`
  - **Body:**

    ```json
    {
      "detail": "Category not found."
    }
    ```

**Validation Rules:**

- `title` is **required** for `POST` requests and **optional** for `PUT` requests.
- `points` must be an array of strings if provided.

### Call Processing

Handle the submission and retrieval of audio calls through the following endpoints.

#### POST `/call`

**Description:** Submit a new call for processing based on the provided audio file URL. Supported file formats are `.wav` and `.mp3`. Max file size is `300 MB`.

**Request:**

- **Headers:** `Content-Type: application/json`
- **Body:**

  ```json
  {
    "audio_url": "http://example.com/audiofile.wav"
  }
  ```

**Response:**

- **Success:**
  - **Status Code:** `200 OK`
  - **Body:**

    ```json
    {
      "id": "new_call_id"
    }
    ```

- **Error:**
  - **Status Code:** `422 Unprocessable Entity`
  - **Body:**

    ```json
    {
      "detail": "Invalid audio file format or inaccessible URL."
    }
    ```

- **Error:**
  - **Status Code:** `413 Request Entity Too Large`
  - **Body:**

    ```json
    {
      "detail": "File size exceeds the limit of 300 MB."
    }
    ```
  
- **Error:**
  - **Status Code:** `415 Unsupported Media Type`
  - **Body:**

    ```json
    {
      "detail": "Invalid audio format. Only MP3 or WAV are allowed."
    }
    ```


#### GET `/call/{id}`

**Description:** Retrieve details of a specific call by its identifier. The emotional tone will be one of the following values: `Neutral`, `Positive`, `Negative`, `Angry`. The `name` and `location` fields are extracted from the call if possible; otherwise, they are returned as `null`.

**Response:**

- **Success (Processing Complete):**
  - **Status Code:** `200 OK`
  - **Body:**

    ```json
    {
      "id": "call_id",
      "name": "Call Name",
      "location": "Kyiv",
      "emotional_tone": "Neutral",
      "text": "Transcribed text",
      "categories": ["Category 1", "Category 2"]
    }
    ```

- **Processing Incomplete:**
  - **Status Code:** `202 Accepted`
  - **Body:**

    ```json
    {
      "message": "Call is still being processed."
    }
    ```

## Validation Rules

- **Category Endpoints:**
  - `title`: Required for `POST`, optional for `PUT`.
  - `points`: Must be an array of strings if provided.

- **Call Endpoints:**
  - `audio_url`: Must be a valid URL pointing to a `.wav` or `.mp3` file.


## Playground Jupyter Notebook

In this service two notebooks are present `tts_playground.ipynb` and `cat_playground.ipynb` which can be used to test the service.  
They are less detailed than the Postman collection in the root folder but can be used to test the required service.

* `tts_playground.ipynb` is used to test the Text to Speech service.
* `cat_playground.ipynb` is used to test the Categorization service.

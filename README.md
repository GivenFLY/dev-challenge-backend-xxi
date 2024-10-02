# MFA Ukraine Call Processing System

## Project Overview

The **MFA Ukraine Call Processing System** is a containerized application designed to process and analyze a large volume of telephone conversations for the Ministry of Foreign Affairs of Ukraine. The system converts audio recordings into structured datasets, extracting key information such as the caller's name, location, emotional tone, and categorizing conversations into relevant topics.

## How the project works

![Scheme](scheme.png?raw=true)

The system consists of three main services:
* **Backend Service**: Provides an API for managing conversation topics and processing calls.
* **Speech-to-Text Service**: Transcribes audio files to text using a pre-trained model.
* **Categorization Service**: Categorizes call transcripts into predefined topics using zero-shot classification and extracts name and location information using question answering.

### Full Pipeline
* **Receiving Calls:** The backend receives a new call, stores the audio file in a shared volume, and submits its path to the Speech-to-Text Service.
* **Transcription:** After transcription, the Speech-to-Text Service saves the transcript to the shared volume and sends its path back to the backend.
* **Categorization:** The backend makes several API calls to the Categorization Service:
    * Two calls to extract the caller's name and location.
    * One call for zero-shot classification to categorize the call.
* **Processing Results:** Once tasks are completed, the Categorization Service sends results back to the backend, which then stores these in the database and marks the call as processed.
    * You can see in [backend's .env file](./backend/.env) parameters with `_THRESHOLD` suffix. These parameters are predefined and used to adjust the categorization service to meet the requirements of the project.
    * If the QA model answers the name question with a confidence score below `NAME_ANSWER_THRESHOLD`, the answer will be ignored.
    * For categorization, two thresholds are considered: `ZERO_SHOT_CATEGORY_THRESHOLD` and `ZERO_SHOT_TOPICS_THRESHOLD`. A category is added to the call if:
      * The zero-shot model's confidence for the category title exceeds `ZERO_SHOT_CATEGORY_THRESHOLD`.
      * **Or** the sum of confidence scores for all points in the category exceeds `ZERO_SHOT_TOPICS_THRESHOLD`.
* **Retrieving Call Details:** Users can access call details through the backend service when the all models returns the result.


### Speech to Text Service
This service uses the Whisper model from Hugging Face's Transformers to transcribe audio to text. Built with FastAPI and powered by Redis, it manages tasks efficiently and can send transcription results to any specified webhook URL.

### Categorization Service
Utilizing Hugging Face's Transformers for zero-shot classification and question answering, this service is also built with FastAPI and uses Redis for task management. It supports endpoints for classification and question answering and can dispatch results to any webhook URL.


## Technologies Used

- **Docker & Docker Compose**: Containerization and orchestration of services.
- **Django & Django REST Framework**: Backend framework for main API development.
- **FastAPI**: Backend API framework for categorization and speech to text services.
- **PostgreSQL**: Database for storing categories and call data.
- **Redis**: In-memory data structure store for task queues.
- **ARQ (Async Redis Queue)**: Asynchronous task processing.

## Getting Started

### Installation

**Build and Start the Services**

```bash
docker-compose up --build
```

This command will build the Docker images and start all services defined in the `docker-compose.yml` file. The API will be accessible at `http://localhost:8080/api`.

## Usage

### API Endpoints

The API provides the following endpoints for managing categories and processing calls:

#### Category Management

- **GET /category**: Retrieve all conversation topics.
- **POST /category**: Create a new conversation topic.
- **PUT /category/{category_id}**: Update an existing conversation topic.
- **DELETE /category/{category_id}**: Delete a conversation topic by ID.

#### Call Processing

- **POST /call**: Submit a new call via an audio URL. Ensure the audio file has a `.wav` or `.mp3` extension and not larger than `300MB`.
- **GET /call/{id}**: Retrieve details of a processed call.

For detailed API specifications, refer to the README files within each service folder:

- Detailed information about required api calls stored here: [backend/README.md](./backend/README.md)
- API specs and details for STT service: [speech_to_text_service/README.md](./speech_to_text_service/README.md)
- API specs and details for categorization service: [categorization_service/README.md](./categorization_service/README.md)

### Pre-populated Categories

Upon initialization, the system creates the following five default conversation topics:

1. **Visa and Passport Services:** 
    Visa application procedures,
    Passport renewal,
    Required documents for applications,
    Document processing times,
    Visa fees and payments,
    Availability of expedited processing
2. **Diplomatic Inquiries:**
    Political issues between countries,
    Diplomatic exchanges,
    International agreements and treaties,
    Resolution of international conflicts,
    Cooperation in the field of security
3. **Travel Advisories:**
    Security warnings for destination countries,
    Information on natural disasters,
    Updates on epidemic situations,
    Health and vaccination recommendations,
    Local laws and customs guidelines
4. **Consular Assistance:**
    Assistance to citizens abroad,
    Issuance of powers of attorney and documents,
    Support in case of arrest or detention,
    Fine remission and legal assistance,
    Repatriation and emergency return
5. **Trade and Economic Cooperation:**
    Investment opportunities,
    Trade agreements and regulations,
    Cooperation in technology and innovation,
    Support for small and medium enterprises,
    Market analysis and economic trends

These categories can be managed via the CRUD API endpoints.

## Benchmarks

### General information
- **CPU**: 12-Core AMD Ryzen 9 7900X, 5449 MHz
- **RAM**: 64 GB (but for docker I've allocated 32GB)
- GPU was not used in this project.
- **Network speed**: 100 Mbps

### Metrics

- `docker compose build` command execution time: 20 minutes

#### 10 minutes call processing
- **Speech to Text Transcription**: 41 seconds
- **Text Length**: 8698 symbols
- **Name extraction**: less than 1 second
- **Location extraction**: less than 1 second
- **Zero-shot classification**: 52 seconds

#### 1-hour call processing
- **Speech to Text Transcription**: 2 minutes 48 seconds
- **Text Length**: 53173 symbols
- **Name extraction**: 18 seconds
- **Location extraction**: 18 seconds
- **Zero-shot classification**: 59 seconds

#### 2 hours call processing
- **Speech to Text Transcription**: 8 minutes 57 seconds
- **Text Length**: 102091 symbols
- **Name extraction**: 32 seconds
- **Location extraction**: 32 seconds
- **Zero-shot classification**: 62 seconds

## Corner Cases Covered

- **Processing Audio Files**: The system validates audio URLs to ensure they validity of process. Please refer to the [backend documentation](./backend/README.md#post-call) for descriptions of possible responses.
- **Missing Caller Information**: If the caller's name or location cannot be extracted, the respective fields are returned as `null` in the response.
- **Concurrent Category Creates/Updates**: The system can see changes in categories and update call records accordingly.  
  - Current solution sends zero-shot api calls to categorization service for each call if new category was created or points in existing category were updated.
  - The gap between the categorization calls is 20 seconds, that would help to avoid overloading the categorization service and allow to analyse new calls simultaneously.
  - This approach must be enhanced in future if it shall be used in production.
- **Database Integrity**: Ensures that category updates do not leave orphaned references in call records.
- **Service outage**: If some of the services will be broken during the call processing, the system will restart the analyses of the call after the service will be up again.

## Running Tests

To be honest, I don't have much time for writing advanced testing of whole system. But I have prepared some basic tests for backend in Postman collection.  
You can see test descriptions and try them by importing this collection: [Postman Collection](./MFA_Ukraine_Call_Processing_System_Tests.postman_collection.json)

Also, you can see for [Text To Speech Playground](./backend/tts_playground.ipynb) where I've manually tested some of the tts features.
And for [Categorization Playground](./backend/cat_playground.ipynb) where I've manually tested some of the categorization features.

## Disclaimer

1. This project was developed solely for the purpose of the hackathon and adheres to all specified requirements. It is not intended for production use.
2. The project uses pre-trained models from Hugging Face's Transformers library for speech recognition, zero-shot classification and question answering. The accuracy of these models may vary based on the input data.
3. The project can be enhanced in thousands of ways, but due to time constraints, only the core functionalities have been implemented.


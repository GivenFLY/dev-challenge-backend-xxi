# Speech to Text Service
A scalable and efficient Speech to Text service built with FastAPI and powered by Redis for task management. This service transcribes audio files associated with call IDs and is designed to integrate seamlessly into larger systems via webhooks.

## Features
* **Asynchronous Processing:** Utilizes Redis for managing transcription tasks asynchronously.
* **Scalable Worker System:** Built with arq, allowing multiple workers to handle transcription jobs concurrently.
* **Automatic Speech Recognition:** Leverages Hugging Face's Transformers pipeline with Whisper models for accurate transcriptions.
* **Persistent Storage:** Saves transcriptions to specified paths for easy retrieval.
* **Dockerized Setup:** Easy deployment using Docker Compose, ensuring all dependencies are correctly managed.

## Usage
### Running with Docker Compose
```bash
docker-compose up --build speech_to_text speech_to_text_worker
```
This command builds the Docker images and starts all services. The Speech to Text API will be accessible at http://localhost:8001.

## API Endpoint
### Create Transcription Task
#### Endpoint

```bash
POST /transcribe
```

#### Description

Creates a transcription task for a given call ID and audio file path. If a webhook URL is provided, the service will notify the specified URL upon completion.

**Query Parameters**

* `call_id` (string, required): Unique identifier for the call.
* `audio_path` (string, required): Path to the audio file to be transcribed.
* `webhook_url` (string, optional): URL to send the transcription result to.

**Example Request**

```bash
curl -X POST "http://localhost:8001/transcribe?call_id=<your_call_id>&audio_path=<path/to/audio.wav>&webhook_url=http://example.com/webhook"
```

**Example Response**

```json
{
  "message": "Transcription job submitted."
}
```
**Possible Responses**

* **200 OK**
    ```json
    { "message": "Transcription job submitted." }
    ```
    Indicates that the transcription task has been successfully queued.

* **202 Accepted**
    ```json
    { "message": "Transcription is already in progress. Status: processing" }
    ```
    Indicates that a transcription task for the given call_id is already in progress.

* **503 Service Unavailable**
    ```json
    { "detail": "Service temporarily unavailable. Please try again later." }
    ```
    Indicates that the service is currently unavailable, possibly due to Redis connection issues.

#### Webhook Implementation
The webhook will send a POST request with the following payload:

```json
{
  "call_id": "id",
  "transcription_path": "path/to/transcription.txt"
}
```

## Configuration
Configuration is managed via environment variables and a `config.json` file for model settings.

### Environment Variables
The following environment variables are used in the Docker Compose setup:

* **Redis Configuration**
    * `REDIS_HOST`: Hostname for Redis (default: `redis`)
    * `REDIS_PORT`: Port for Redis (default: `6379`)
    * `REDIS_DB`: Redis database number (default: `1`)

* **Worker Configuration**
    * `WORKER_MAX_JOBS`: Maximum number of concurrent jobs (default: `100`)
    * `WORKER_JOB_TIMEOUT`: Job timeout in seconds (default: `3600`)
    * `WORKER_MAX_TRIES`: Maximum retry attempts for failed jobs (default: `20`)
# Categorization Service
A scalable and efficient Categorization service built with FastAPI and powered by Redis for task management.  
This service can perform zero shot classification and question answering actions with the files associated with call IDs and is designed to integrate seamlessly into larger systems via webhooks.

## Features
* **Asynchronous Processing:** Utilizes Redis for managing transcription tasks asynchronously.
* **Scalable Worker System:** Built with arq, allowing multiple workers to handle transcription jobs concurrently.
* **Zero shot classification:** Leverages Hugging Face's Transformers pipeline with a pre-trained model for zero-shot classification.
* **Question Answering:** Utilizes Hugging Face's Transformers pipeline with a pre-trained model for question answering.
* **Webhook Support:** Notifies a specified URL upon completion of transcription tasks.
* **Dockerized Setup:** Easy deployment using Docker Compose, ensuring all dependencies are correctly managed.

## Usage
### Running with Docker Compose
```bash
docker-compose up --build categorization categorization_worker
```
This command builds the Docker images and starts all services. The Speech to Text API will be accessible at http://localhost:8001.

## API Endpoint
### Create Zero Shot Classification Task
#### Endpoint

```bash
POST /classify
```

#### Description

Creates a transcription task for a given call ID and candidate_labels with context or context_file provided.  
If a webhook URL is provided, the service will notify the specified URL upon completion.

**Query Parameters**
* `call_id` (string, required): Unique identifier for the call.

**Body Parameters**

* `context` (string, optional): Context for zero-shot classification.
* `context_path` (string, optional): Path to a file containing the context for zero-shot classification. (One of `context` or `context_path` is required)
* `candidate_labels` (string, required): List of candidate labels for zero-shot classification.
* `webhook_url` (string, optional): URL to send the transcription result to.
**Example Request**

```bash
curl -X POST "http://localhost:8002/classify?call_id=<your_call_id>" \
     -H "Content-Type: application/json" \
     -d '{
           "context": "I have a problem with my iphone that needs to be resolved asap!!",
           "candidate_labels": ["urgent", "not urgent", "phone", "tablet", "computer"],
           "webhook_url": "http://example.com/webhook"
         }'
```

**Example Response**

```json
{
  "message": "Zero shot classification job submitted."
}
```
**Possible Responses**

* **200 OK**
    ```json
    { "message": "Zero shot classification job submitted." }
    ```
    Indicates that the zero shot classification task has been successfully queued.

* **400 Bad Request**
    ```json
    { "detail": "Either context or context_path must be provided." }
    ```
    Indicates that the context or context_path is missing or invalid in the request body.

* **503 Service Unavailable**
    ```json
    { "detail": "Service temporarily unavailable. Please try again later." }
    ```
    Indicates that the service is currently unavailable, possibly due to Redis connection issues.

#### Webhook Implementation
The webhook will send a POST request with the following payload (see example request):

```json
{
  "call_id": "<your_call_id>",
  "result": {
    "urgent": 0.999,
    "phone": 0.995,
    "computer": 0.095,
    "not urgent": 0.0001,
    "tablet": 0.000,
    "finish_time": 1631523980000000000  // Finish time in nanoseconds (time.time_ns()) 
  }
}
```

### Create QA Task
#### Endpoint

```bash
POST /qa
```

#### Description

Creates a qa task for a given call ID and question with context or context_path provided.  
If a webhook URL is provided (future implementation), the service will notify the specified URL upon completion.

**Query Parameters**
* `call_id` (string, required): Unique identifier for the call.

**Body Parameters**

* `context` (string, optional): Context for zero-shot classification.
* `context_path` (string, optional): Path to a file containing the context for zero-shot classification. (One of `context` or `context_path` is required)
* `question` (string, required): Question to ask the model.
* `webhook_url` (string, optional): URL to send the transcription result to.
**Example Request**

```bash
curl -X POST "http://localhost:8002/classify?call_id=<your_call_id>" \
     -H "Content-Type: application/json" \
     -d '{
           "context": "My name is Wolfgang and I live in Berlin",
           "question": "Where do I live?",
           "webhook_url": "http://example.com/webhook"
         }'
```

**Example Response**

```json
{
  "message": "Question answering job submitted."
}
```
**Possible Responses**

* **200 OK**
    ```json
    { "message": "Question answering job submitted." }
    ```
    Indicates that the question answering task has been successfully queued.

* **400 Bad Request**
    ```json
    { "detail": "Either context or context_path must be provided." }
    ```
    Indicates that the context or context_path is missing or invalid in the request body.

* **503 Service Unavailable**
    ```json
    { "detail": "Service temporarily unavailable. Please try again later." }
    ```
    Indicates that the service is currently unavailable, possibly due to Redis connection issues.

#### Webhook Implementation
The webhook will send a POST request with the following payload (see example request):

```json
{
  "call_id": "<your_call_id>",
  "result": {
    "score": 0.919,
    "start": 34,
    "end": 40,
    "answer": "Berlin"
  }
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
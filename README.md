# BirdTag: Serverless Media Storage and Tagging System

## Overview
BirdTag is a full-stack serverless application developed for Monash Birdy Buddies (MBB) to facilitate the storage, processing, and tagging of bird media (images, audio, video). The system uses AWS services to provide a scalable and event-driven backend along with a modern React frontend that supports user interaction and search capabilities. The system integrates AI-powered models (YOLO and BirdNET) for automatic species detection and provides a seamless experience for media search, subscription alerts, and metadata management.

This project was developed as part of the FIT5225 Cloud Computing assignment at Monash University.

## Features
- ✅ Upload media (images, videos, audio) with automatic bird species tagging using ML models.
- ✅ Store media in structured S3 buckets and metadata in DynamoDB.
- ✅ Search for media by bird species or custom tag queries.
- ✅ Query similar media by uploading an example file (QueryByUpload).
- ✅ Modify and delete existing media records and tags.
- ✅ Subscribe to bird species and receive email notifications via SNS when new media is uploaded.
- ✅ React-based frontend with AWS Cognito user authentication.
- ✅ Fully serverless backend using Lambda, API Gateway, S3, DynamoDB, and SNS.

## Technologies Used
- **Frontend:** React.js, TailwindCSS, AWS Cognito, Axios
- **Backend:** AWS Lambda (Python 3.11), API Gateway, S3, DynamoDB, SNS
- **Machine Learning:** YOLOv8 (for image/video detection), BirdNET (for audio tagging)
- **Other Tools:** Vercel (Frontend deployment), Boto3, OpenCV, FFmpeg

## Project Structure
```
.
├── backend
│   └── aws_lambda_codes/       # Contains all Lambda function folders with handler code
├── database/                   # Contains sample data, schema info for DynamoDB
├── infra/                      # Contains scripts or templates for setting up AWS infra (optional)
├── birdtag-frontend/           # React app for BirdTag UI
├── .gitignore
├── requirements.txt            # Python dependencies for backend
├── AI_Acknowledgment.txt
└── README.md
```

## Lambda Functions Summary
- **generate-temp-upload-url:** Generates a temporary pre-signed S3 URL for uploading media.
- **get-all-media:** Fetches all media metadata records from DynamoDB.
- **modify_tags:** Add or remove tags from a given file ID.
- **delete_files:** Deletes a file from S3 and its metadata from DynamoDB.
- **search_by_species:** Fetches media where specified species appear in tags.
- **search_by_tags:** Searches media based on custom tag logic (e.g. pigeon:2).
- **get-original-url:** Converts a thumbnail S3 URL to its corresponding original media URL.
- **get-media-matches-by-upload:** Accepts a query file, uses YOLO/BirdNET, returns matching media.
- **BirdTagQueryByUpload:** Dockerized ML Lambda for temporary upload + inference + delete.
- **tag-notifier:** Triggered via DynamoDB stream to send SNS emails to species subscribers.
- **SNS_subscription:** Allows users to subscribe to bird species topics.
- **get-user-subscriptions:** Retrieves the list of species a user is subscribed to.

## Frontend Pages
- **AllMedia.jsx:** Displays all media from the system with preview, tag info, and actions.
- **UploadMedia.jsx:** Allows authenticated users to upload files, one at a time.
- **SearchMedia.jsx:** Filter media based on selected tags.
- **QueryByUpload.jsx:** Upload a file to find similar media.
- **ModifyTagsModal.jsx:** Modal component to add/remove tags from selected media.

## DynamoDB Schema – `BirdMediaMetadata`
- **file_id (PK)**: Unique identifier (e.g., `video_103.mp4`)
- **file_type**: `image`, `video`, or `audio`
- **original_url**: S3 pre-signed or permanent URL
- **thumbnail_url**: URL to the preview (for image/video)
- **tags**: Map of bird species and detection counts (e.g., `{"owl": 2, "myna": 1}`)
- **uploaded_by** (optional): Cognito user identifier

## S3 Bucket Structure – `birdtag-storage-aus-dev`
- `/images/` – Full-size image uploads
- `/videos/` – Full-size videos
- `/audios/` – Audio files
- `/thumbnails/` – Thumbnail previews for image/video
- `/exports/` – Optional exports for user/download
- `/lambda-zips/` – Zipped Lambda code bundles
- `/models/` – YOLO and BirdNET model files for inference

## SNS Topics and Subscriptions
Each bird species has a dedicated SNS topic (e.g., `species-owl-topic`). When new media is tagged with that species, an alert is published to the topic, and all subscribed users receive an email.

- SNS topic creation and deletion handled by infra or admin manually.
- Subscriptions are managed per user through frontend integration.

## Setup Instructions
### 1. Clone the Repo
```bash
git clone https://github.com/<your-repo-url>.git
cd birdtag
```

### 2. Deploy Backend
- Use AWS Console or SAM/CDK to deploy Lambda functions.
- Upload model files to `s3://birdtag-storage-aus-dev/models/`
- Set IAM roles and permissions appropriately.
- Enable DynamoDB Streams (New Image) on `BirdMediaMetadata`.

### 3. Run Frontend Locally
```bash
cd birdtag-frontend/web-ui
npm install
npm run dev
```
- Create `.env` file for API base URL and Cognito info

### 4. Environment Variables (Frontend)
```
REACT_APP_API_BASE_URL=https://<api-gateway-url>
REACT_APP_COGNITO_USER_POOL_ID=...
REACT_APP_COGNITO_CLIENT_ID=...
```

### 5. Optional: Deploy Frontend
- Use Vercel or Amplify
- Set environment variables in deployment platform

## Team Members
- **Anmol Salwan** – AWS Infrastructure & DevOps: Set up S3, DynamoDB, IAM, Lambda triggers, SNS
- **Glenn Varghese George** – Backend Integration: Lambda logic for thumbnail generation, model integration, tagging, and DB writes
- **Aditya Mehrotra** – API & Query Engine: Developed query and tagging APIs (search, delete, modify), API Gateway integrations
- **Varun Kashyap** – Frontend & Authentication: Cognito setup, login/signup flows, React UI for upload, query, and preview

## AI Acknowledgment
See `AI_Acknowledgment.txt` for details on how AI tools were used ethically and responsibly in support of this project.

---

> This repository was developed for academic purposes as part of the FIT5225 Cloud Computing unit at Monash University, June 2025. All infrastructure was deployed in a cost-efficient and temporary manner for assessment purposes only.
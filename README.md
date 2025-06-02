# 🐦 BirdTag: AWS-Powered Serverless Media Storage & Tagging System

## 📘 Overview
BirdTag is a serverless cloud-based application designed for Monash Birdy Buddies (MBB) to store, tag, and query multimedia files (images, audio, videos) based on bird species detection. Built entirely on AWS, this system allows automatic tagging using machine learning models and provides an intuitive API/UI for querying and managing bird media content.

---

## 🔧 Features
- Secure authentication using **AWS Cognito**
- Upload and store media files in **Amazon S3**
- Auto-tagging of birds using:
  - Image-based model (custom CNN)
  - Audio-based model (BirdNET Analyzer)
- Thumbnail generation for images via **AWS Lambda**
- Metadata storage in **Amazon DynamoDB**
- Query media by tags/species, counts, or thumbnails
- Bulk add/remove tags, file deletion support
- Email notifications via **Amazon SNS**
- Simple web interface (or script-based if UI skipped)

---

## 📁 Project Structure
```
BirdTag-AWS/
├── backend/
│   ├── lambda/
│   ├── model_assets/
├── frontend/
│   ├── web-ui/ or scripts/
├── infra/
├── database/
├── reports/
├── README.md
├── .gitignore
└── requirements.txt
```

---

## 🚀 Deployment (Quick Start)
1. Clone the repo and navigate into the folder:
    ```bash
    git clone <repo-url>
    cd BirdTag-AWS
    ```
2. Install required tools (e.g., AWS CLI, SAM CLI)
3. Deploy via SAM or manually upload Lambda + configure triggers
4. Configure IAM roles, Cognito, and API Gateway endpoints
5. Upload test media and verify detection + tagging

---

## 📦 Models Used
- **Image Model:** `bird_detection/` folder — used to tag bird species in image files
- **Audio Model:** `BirdNET-Analyzer/` — used for bird song/call identification

---

## 📌 API Endpoints
| Feature               | Method | Endpoint                      |
|----------------------|--------|-------------------------------|
| Upload Media         | POST   | /upload                       |
| Search by Tags       | POST   | /search                       |
| Get Full Image       | GET    | /image?thumbUrl=...           |
| Add/Remove Tags      | POST   | /tags/bulk                    |
| Delete Files         | POST   | /delete                       |
| Identify + Find      | POST   | /match                        |

---

## 🔐 Authentication Flow
- Users sign up via Cognito Hosted UI or custom frontend
- Post-login, users receive tokens enabling secure interaction with API Gateway and other services
- IAM roles restrict access to only authorized, verified users

---

## 📚 Reports & Contributions
- Refer to `/reports/team_report_draft.docx` and `/reports/individual_report_<name>.docx` for detailed documentation
- Contributions tracked via Git commits and team table in the final report

---

## 📸 Sample UI Screenshots (if applicable)
_Include after implementation: upload page, search results, login screen, etc._

---

## 👥 Team
| Name | Student ID | Contribution |
|------|------------|--------------|
| ...  | ...        | ...          |

---

## 📄 License
_This project is for educational purposes under Monash University FIT5225 unit._

---

## ✅ Status
> Project Due: **Monday, 9 June 2025 – 11:55PM**

_Last updated: June 2, 2025_

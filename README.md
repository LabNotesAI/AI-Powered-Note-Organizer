# AI-Powered-Note-Organizer
AI Powered Note Organizer – Automates parsing of unstructured notes into structured data with AI, MongoDB, and Linux file watching.

📖 Overview
The AI Powered Note Organizer is a personal knowledge management system designed to bring structure to unstructured notes. By simply dropping files into a shared folder, the system automatically detects new content, parses it with AI, and organizes it into headings, tags, and searchable content.
This project was inspired by the challenge of managing scattered notes with generic filenames — and demonstrates how AI can be applied to solve real world productivity problems.

✨ Features
•	Automated File Detection: Uses Linux file watching to trigger workflows when new files are added to a Samba share.
•	AI Driven Parsing: Extracts headings, tags, and structured content from raw notes.
•	Data Storage: Stores processed notes in MongoDB for fast retrieval and querying.
•	Computer Vision Integration (planned): Extend parsing to include images and screenshots with OCR.
•	URL Handling (planned): Automatically detect URLs in notes and send them to Readeck for archiving.
•	Frontend Dashboard (planned): Build a lightweight web interface for browsing, searching, and managing notes.

🛠️ Tech Stack
•	Linux (file system monitoring)
•	Samba Share (file drop integration)
•	MongoDB (data storage and retrieval)
•	Docker / Containers (service isolation and deployment)
•	AI Engines (multiple frameworks tested for parsing and tagging)
•	Readeck API (planned integration for URL archiving)
	
🚀 Future Improvements
•	Develop a frontend UI (Flask/FastAPI + React or similar).
•	Add semantic search using embeddings for meaning based queries.
•	Expand support for multi format inputs (PDFs, images, voice notes).
•	Enhance tagging and clustering with NLP models.
•	Integrate with open source AI safety/privacy frameworks to ensure responsible handling of personal data.

🎯 Why This Project Matters
This project demonstrates:
•	Practical application of AI + automation to solve everyday problems.
•	Experience with data pipelines, containers, and open source tools.
•	A focus on AI safety, privacy, and responsible use of personal data.
•	The ability to design and iterate on a system from concept to deployment.

# Running with Docker
📂 Project Structure
```
.
├── Dockerfile        # Container build instructions
├── watcher.py        # Main watcher script
├── requirements.txt  # Python dependencies
├── .env.example      # Example environment variables
├── .gitignore        # Ignore cache, logs, secrets
└── README.md         # Project documentation
```

⚙️ Setup
1. Clone the repo
   
```
git clone https://github.com/yourusername/ai-note-watcher.git

cd ai-note-watcher
```


2. Configure environment
Create a .env file (based on .env.example):
```
MONGO_URI=mongodb://localhost:27017/notes
AI_ENDPOINT=http://localhost:11434/api/generate
MODEL_NAME=your-model-name
```

3. Build the Docker image
```
docker build -t ai-watcher .
```

4. Run the container
```
docker run -it --rm \
  -v /path/to/watch:/mnt/storage \
  --env-file .env \
  ai-watcher
```

# Example Workflow
1. Drop a .txt file into /path/to/watch
2. The watcher detects it, sends the text to the AI model
3. The AI returns structured JSON (title, summary, tags, content)
4. The script inserts the structured data into MongoDB

# Dependencies
* Python 3.11 (via python:3.11-slim)
* watchdog
* pymongo
* requests
* python-dotenv

# Notes
* Make sure MongoDB is running and accessible from the container.
* The AI endpoint must support JSON schema enforcement (tested with Ollama).
* Logs are printed to stdout for easy monitoring

Home Page
![Homepage](https://github.com/user-attachments/assets/4960ca01-6a84-4df9-a1f4-84d26ab3eb6d)

Document Detail Page
![Document_Detail](https://github.com/user-attachments/assets/c2d71228-2983-459f-a33d-aeaf4af68b24)


# License
MIT License

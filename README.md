
# Dangerous Object Detection

## Overview

This project is a real-time dangerous object detection system that utilizes machine learning to identify potentially hazardous objects via a camera feed. The system is divided into two main components:
- **Backend:** Handles object detection using a pre-trained model (e.g., YOLOv8) via a FastAPI server.
- **Frontend:** Provides a user interface using Streamlit, allowing users to start detection, view live feeds, and generate a PDF report of detected objects.

## Project Structure

```
final_project/
├── frontend/
│   ├── app.py                # Streamlit frontend application
├── backend/
├── datasets/
│   ├── test
│   |    ├── images/
│   |    └── labels/
│   ├── val
│   |    ├── images/
│   |    └── labels/
│   ├── train
│   |    ├── images/
│   |    └── labels/
│   ├── main.py               # FastAPI backend application
├── saved-pdf/                # Directory for saving generated PDFs
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation (this file)
├── config.py
├── test_dangerous_objects_detection.py
├── best.pt
├── .gitignore
├── paths.json
├── Training_Model/
│   ├── best.py
│   ├── dog.jpeg
│   ├── Training.ipynb
│   ├── yolov8n.pt
├── runs/
│   ├── #files and subfolders that are created after training model
```

## Features

- **Real-time Object Detection:** Uses a camera to detect objects in real-time.
- **PDF Report Generation:** Generates a PDF report with frames where dangerous objects are detected, including timestamps.
- **User-friendly Interface:** Streamlit-based UI for easy interaction.
- **Continuous Detection:** Keeps detecting objects until the user manually stops the process.

## Installation

### Prerequisites

- Python 3.9+
- Git (optional, for cloning the repository)
- A virtual environment (recommended)

### Clone the Repository

```bash
git clone https://github.com/yourusername/dangerous-object-detection.git
cd dangerous-object-detection
```

### Set Up the Environment

1. **Create a virtual environment** (optional but recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scriptsctivate`
    ```

2. **Install the required dependencies**:

    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

## Usage

### Backend (Object Detection)

1. **Run the FastAPI server**:

    Navigate to the `backend` directory and start the server:

    ```bash
    cd backend
    uvicorn main:app --reload
    ```

    The API will be available at `http://localhost:8000`.

### Frontend (Streamlit Application)

1. **Run the Streamlit application**:

    Navigate to the `frontend` directory and start the Streamlit app:

    ```bash
    cd frontend
    streamlit run app.py
    ```

    The application will open in your web browser.

2. **Start Object Detection**:

    - Enter the event name.
    - Click the "Start Detection" button to begin real-time detection.
    - View the live camera feed and detected objects on the Streamlit interface.
    - The detection continues until you manually stop it.

3. **Generate and Save PDF Report**:

    - After stopping the detection, the application will generate a PDF report.
    - The report will include frames with detected objects and corresponding timestamps.
    - PDFs are saved in the `saved-pdf/` directory.

## Testing

### Running Tests

Tests are located within the `backend` and `frontend` directories. To run the tests:

```bash
pytest
```

Ensure that the necessary environment (such as a running FastAPI server) is available if the tests require it.

## Deployment

### Continuous Integration and Continuous Deployment (CI/CD)

This project includes a CI/CD pipeline configured using GitHub Actions. The pipeline performs the following tasks:

1. **Testing:** Runs tests on every push or pull request to the `main` or `develop` branches.
2. **Build:** Builds the application after successful testing.
3. **Deployment:** Deploys the application if the changes are pushed to the `main` branch.

### Deployment Options

For production deployment, especially when GPU resources are required for efficient object detection:

- **Google Colab**: Use Google Colab's free GPU resources to run your model (good for development, not recommended for production).
- **AWS EC2 with GPU**: Deploy on an AWS EC2 instance with GPU, though this may incur costs.
- **Heroku (with limitations)**: Suitable for small-scale deployment, though it doesn't support GPU.

## Contributing

We welcome contributions to this project! If you have any ideas, bug reports, or suggestions, please open an issue or create a pull request.

### Steps to Contribute

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch-name`).
3. Make your changes.
4. Push to your fork and submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any inquiries, you can reach out to:

- **Author:** Manarth Patel
- **Email:** [manarthpatel237@gmail.com](mailto:manarthpatel237@gmail.com)
- **LinkedIn:** [https://www.linkedin.com/in/manarthpatel](https://www.linkedin.com/in/manarthpatel)

---

Thank you for using and contributing to the Dangerous Object Detection project!

## Installation Guide for running the Chatbot locally

For now this _**ONLY**_ works for _**Version 3**_

### Prerequisites
- Python 3.12 or higher
- Cuda 11.8 or higher (if using GPU)
- Ideally an IDE to run the code (e.g., PyCharm, VSCode, IntelliJ)

### HuggingFace Account
- Create a HuggingFace Account (theoretically optional, but recommended for automatically downloading models)
- Request access to the following model: [mistral v0.3](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3)
- Create an access token (Read) name it "chatbot_test_token" and copy it to your clipboard or save it in a text file temporarily

### Installation Steps
1. Install Python 3.12 or higher from the official website: [Python Downloads](https://www.python.org/downloads/)
   - make sure to check the box to add Python to your PATH during installation. 


2. Install the required libraries:
   ```bash
   pip install transformers torch chromadb sentence_transformers huggingface_hub einops
   ```
3. Clone the repository:
   ```bash
   cd <path_to_your_desired_directory>
   git clone https://github.com/unendschlossen2/chatbot_jade_hs_planspiel.git
   ```
4. Open the project in your IDE


**[Ensure that the Python interpreter is set to the version you installed in step 1]**


5. Login to HuggingFace:
   - Put your HuggingFace token in the function login("Your Token")
   - then run huggingface_login.py


6. Run Gui_test00.py


7. Input your question in the GUI and press "generate"

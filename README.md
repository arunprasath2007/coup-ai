# Coup AI Game

This project implements an AI-driven version of the popular board game Coup.

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/arunprasath2007/coup-ai.git
   cd coup-ai
   ```

2. Create and activate a virtual environment:
   
   On Windows:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
   
   On macOS and Linux:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Open the `.env` file and replace `<Your_OPENAI_API_KEY_GOES_HERE>` with your actual OpenAI API key.

5. Run the game:
   ```
   python main.py
   ```
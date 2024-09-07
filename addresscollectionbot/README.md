# Address Collection Bot

This codebase contains implementation for address collection bot

## Instructions

1. Install the dependencies
```bash
pip install -r requirements.txt
```

2. Install Ollama (for linux users only, others may refer to the [website](https://ollama.com/download/) for downloads.)
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

3. Run llama3 
This code will take some time to run as it downloads the entire LLM. Only proceed to next step after it is complete.
```bash
ollama serve llama3
```

4. Run the main file 
```bash
python main.py
```

Note: This will only run the bot locally on server.
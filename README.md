# 🧠 AI Agent Project

Welcome to the **AI Agent Project**! 🎉 This project is a fully functional AI-powered code generator and refactoring assistant designed to help developers write clean, secure, and efficient Python code while keeping your systems safe from risky code execution.

---

## 🚀 What is this Project About?

The **AI Agent** uses the power of `ollama` and a suite of security tools to:

- ✅ Generate secure Python code.
- ✅ Refactor long and complex code for better readability.
- ✅ Check for security vulnerabilities before execution.
- ✅ Cache responses for faster results next time.
- ✅ Use AI for optimized and security-focused code recommendations.

Think of it as your ultra-paranoid coding buddy who *really* hates `eval()` calls and won't let you do risky stuff. 😉

---

## 📦 Project Structure

Your project is neatly organized into the following structure:

```plaintext
📦 AI_Agent
├── 📂 venv                   # Virtual environment (for Python package isolation)
├── 📂 cache/responses        # Cached AI responses to speed up repeated queries
├── 📂 scripts                # (Optional) Scripts for automation
├── 📄 ai_agent.py            # The core AI agent script
├── 📄 requirements.txt       # All project dependencies
├── 📄 README.md              # You're reading it! 📖
└── 📄 .gitignore             # To avoid versioning unwanted files
```

---

## 🛠️ Installation and Setup

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-repo/ai_agent.git
cd ai_agent
```

### Step 2: Set Up a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate    # Mac/Linux
venv\Scripts\activate      # Windows
```

### Step 3: Install Dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Run the AI Agent 🧠
```bash
python ai_agent.py
```

---

## 🤖 How to Use the AI Agent

1. **Run the script.**
2. **Input your coding task.** Example: *"Write a secure Python web scraper."*
3. **The agent generates the code!**
4. **Want it cleaner?** Use the refactor mode: `agent.refactor_code(your_code_here)`

---

## 🔐 Security Features (Because Safety First!)

This AI Agent is built with **security in mind**. Here's how it keeps your code safe:

- 🛡️ **Code Sanitization:** Dangerous patterns like `eval()` and `subprocess` are scrubbed.
- 🛡️ **Security Score:** Every code snippet gets a security score before execution.
- 🛡️ **Caching:** Secure responses are cached for performance.
- 🛡️ **Validation Checks:** Syntax validation and dangerous pattern detection.

> Remember: Safety first. No evals. No `rm -rf`. No `chmod 777`. 🧐

---

## 📦 Dependencies

All required packages are listed in `requirements.txt`. They include:

- `ollama` – The AI engine 🧠
- `httpx` – For secure HTTP requests
- `pydantic` – Data validation and modeling
- `certifi`, `sniffio`, `anyio` – Security support
- **Optional:** `black`, `flake8`, `pytest` (for dev tools and testing)

Install them all using:
```bash
pip install -r requirements.txt
```

---

## ✅ Contributing

Contributions are always welcome! Feel free to:

- **Submit a PR** for bug fixes or improvements.
- **Open an Issue** if you find a bug.
- **Share Feedback** for new features.

---

## 🎯 Roadmap

- [ ] Implement multi-language support.
- [ ] Add GUI for easier interaction.
- [ ] Expand security analysis capabilities.
- [ ] Add support for API integrations (Supabase, GitHub, etc.)

---

## 📖 License

This project is licensed under the **MIT License**. Feel free to use it, modify it, and build cool things!

---

## ✨ A Final Note

Remember, **AI Agents** are powerful, but *you* are the developer with the final say! Use this responsibly, and never blindly trust generated code in production. 💡

Happy coding! 🚀


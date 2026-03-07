# ShellPilot 🚀

### A Self-Learning AI Terminal Debugger

ShellPilot is an AI-powered command-line assistant that diagnoses
terminal errors, suggests fixes, and **learns from previous failures**
to resolve recurring issues instantly.

Run commands with:

    ai-run <command>

Example:

    ai-run python3 -m pip install -e

------------------------------------------------------------------------

# ✨ Key Features

### 🧠 Self-Learning Error Memory

ShellPilot stores previously resolved errors and retrieves them
instantly the next time they occur.

### 🤖 AI-Powered Debugging

Uses Amazon Bedrock LLMs to analyze terminal failures and generate safe
fixes.

### 🔎 Semantic Error Matching

Uses Titan text embeddings to match similar errors even if they aren't
identical.

### ⚡ Instant Fix Retrieval

Once a fix is learned:

    ⚡ Instant fix from ShellPilot memory

### 🛡 Safe Fix Execution

ShellPilot never executes commands automatically. Users confirm before
execution.

### 📊 Learning Statistics

    ai-run stats

Example:

    ShellPilot Stats
    ----------------
    Errors learned: 7

    Top learned fixes:
    • pip install -e .
    • npm install --legacy-peer-deps
    • sudo docker run

------------------------------------------------------------------------

# 🏗 Architecture

    Terminal Error
          │
          ▼
    ShellPilot CLI
          │
          ▼
    Context Builder
          │
          ▼
    API Gateway
          │
          ▼
    AWS Lambda
          │
          ├── Titan Embeddings (semantic search)
          ├── Llama 3 (fix generation)
          └── DynamoDB (persistent memory)

------------------------------------------------------------------------

# ⚙️ Technology Stack

  Component           Technology
  ------------------- --------------------------
  CLI Tool            Python
  AI Models           Amazon Bedrock (Llama 3)
  Embeddings          Titan Text Embeddings
  Backend             AWS Lambda
  API                 API Gateway
  Memory Store        DynamoDB
  Similarity Search   Cosine Similarity

------------------------------------------------------------------------

# 🚀 Installation

Clone the repository:

    git clone https://github.com/Jaydeng75/shellpilot
    cd shellpilot

Install dependencies:

    pip install -e .

------------------------------------------------------------------------

# ▶ Usage

Run commands with AI debugging:

    ai-run <command>

Example:

    ai-run python3 -m pip install -e

------------------------------------------------------------------------

# 📈 Example Workflow

1.  Run a failing command
2.  ShellPilot diagnoses the issue
3.  Suggested fix appears
4.  Apply fix
5.  ShellPilot learns it for future runs

------------------------------------------------------------------------

# 🎯 Why ShellPilot?

Developers repeatedly encounter the same terminal errors. ShellPilot
eliminates repetitive debugging by creating a **persistent knowledge
base of fixes**.

Instead of repeatedly diagnosing the same problems, ShellPilot:

1.  Understands the error
2.  Suggests a fix
3.  Learns the solution
4.  Resolves the issue instantly next time

------------------------------------------------------------------------

# 🧠 Future Improvements

-   Vector database for large-scale error memory
-   Automated fix verification in sandbox environments
-   IDE integration
-   Multi-agent debugging architecture
-   Shared team debugging knowledge bases

------------------------------------------------------------------------

# 👨‍💻 Author

Built as a hackathon project demonstrating how **AI + semantic search +
persistent memory** can transform developer debugging workflows.

------------------------------------------------------------------------

# 🏁 Summary

ShellPilot transforms terminal debugging from:

    search → guess → retry

into:

    AI diagnose → apply fix → learn forever

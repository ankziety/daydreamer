# Daydreamer AI - Advanced Conversational AI System

An experimental AI system that combines Chain of Thought reasoning with creative "Day Dreaming" techniques to provide thoughtful, insightful conversations with persistent memory across sessions.

## 🧠 Key Features

### True Chain of Thought Reasoning
- **Recursive Self-Prompting**: The AI thinks through problems by repeatedly prompting itself
- **Context Building**: Builds understanding through multiple thinking steps
- **Dynamic Summarization**: Automatically summarizes when approaching context limits
- **Confidence Assessment**: Continues thinking until reaching satisfactory conclusions

### Day Dreaming Technique
- **Random Memory Integration**: Combines random memories with current context
- **Creative Knowledge Synthesis**: Explores unexpected connections between concepts
- **Novel Insight Generation**: Generates abstract ideas difficult for humans to discover
- **Adaptive Creativity**: Learns from successful creative patterns

### Persistent Memory System
- **Cross-Session Continuity**: Remembers conversations across sessions
- **User Profile Learning**: Builds understanding of user interests and communication style
- **Insight Storage**: Preserves valuable insights from thinking and dreaming
- **Smart Retrieval**: Finds relevant memories for current conversations

### Robust AI Integration
- **Ollama Support**: Primary integration with local Ollama models
- **Transformers Fallback**: Automatic fallback to HuggingFace transformers
- **Model Auto-Detection**: Automatically selects best available model
- **Flexible Configuration**: Easy switching between different models

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ankziety/daydreamer.git
cd daydreamer

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# Start interactive chat with auto-detection
python cli.py

# Use specific memory database
python cli.py --memory my_conversation.db

# Force specific model type
python cli.py --model transformers

# Run quick system test
python cli.py --test

# View conversation statistics
python cli.py --stats
```

### With Ollama (Recommended)

If you have Ollama installed:

```bash
# Install and start Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve

# Pull a recommended model
ollama pull gemma3n:3b

# Start Daydreamer with Ollama
python cli.py --model ollama
```

## 🏗️ Architecture

The system is built with a modular architecture:

### Core Modules

- **`prompts.py`** - All system prompts and prompt engineering templates
- **`chain_of_thought.py`** - True recursive chain of thought implementation  
- **`day_dreaming.py`** - Creative day dreaming technique implementation
- **`memory_manager.py`** - Persistent memory storage and retrieval
- **`ollama_integration.py`** - Clean AI model integration with fallbacks
- **`daydreamer_ai.py`** - Main system orchestrating all components
- **`cli.py`** - Command line interface

### Legacy Files

Old implementations have been moved to the `legacy/` directory for reference.

## 💭 How It Works

### 1. Chain of Thought Processing
When you send a message, the AI:
1. Analyzes your input through multiple thinking steps
2. Recursively prompts itself for deeper understanding
3. Builds context and confidence through iterations
4. Summarizes when approaching token limits
5. Continues until reaching satisfactory conclusions

### 2. Day Dreaming Sessions
Periodically triggered creative sessions:
1. Selects random memories and knowledge domains
2. Makes unexpected connections between concepts
3. Generates novel insights through creative leaps
4. Evaluates insights for creativity and relevance
5. Integrates valuable insights into responses

### 3. Persistent Memory
Maintains continuity through:
1. Storing all conversations with importance scoring
2. Building user profile from communication patterns
3. Retrieving relevant memories for context
4. Learning from successful interaction patterns

## 🔧 Configuration

### Model Configuration

```python
# In your Python code
from daydreamer_ai import DaydreamerAI

model_config = {
    'ollama_model': 'gemma3n:e4b',      # Specific Ollama model
    'transformers_model': 'gpt2',       # Fallback model
    'ollama_host': 'localhost:11434'    # Ollama server
}

ai = DaydreamerAI(model_config=model_config)
```

### Memory Configuration

```python
# Custom memory database
ai = DaydreamerAI(memory_db_path='custom_memory.db')

# View memory statistics
stats = ai.memory_manager.get_memory_stats()
print(stats)
```

## 📊 Example Session

```
🧠 DAYDREAMER AI - INTERACTIVE CHAT
======================================================================
Welcome to Daydreamer AI! I use advanced Chain of Thought reasoning
and creative Day Dreaming to provide thoughtful, insightful responses.

👤 You: What is the nature of consciousness?

🤔 Processing your message...

=============== PROCESSING USER INPUT ===============
🧠 Starting Chain of Thought analysis...
   Starting chain of thought analysis...
   Initial analysis complete (confidence: 0.70)
   Continuing chain of thought (step 2)...
   Step 2 complete (confidence: 0.85)
   Ready to respond

🌙 Triggering Day Dreaming session...
   🧠 Generating insight 1/3...
   ✨ Creative insight generated (score: 0.78)
   🔗 Planning insight integration...

🎯 Generating final response...

🤖 Daydreamer AI: Consciousness is fascinating because it seems to emerge 
from the complex interplay of information processing, self-awareness, and 
subjective experience. Through my chain of thought analysis, I see it as 
potentially existing on a spectrum rather than being binary...

[Creative insight from consciousness studies: The boundary between conscious 
and unconscious processing might be more fluid than we typically imagine, 
similar to how dreams blend memory fragments in unexpected ways.]

What aspects of consciousness are you most curious about?
```

## 🔬 Research Background

This project explores novel approaches to AI consciousness and creativity:

- **Chain of Thought vs Traditional**: Instead of simple step-by-step reasoning, implements true recursive self-prompting
- **Day Dreaming Technique**: Novel approach using random memory integration for creative insights
- **Persistent Development**: AI develops personality and understanding through accumulated conversations
- **Hybrid Reasoning**: Combines analytical thinking with creative exploration

## 🛠️ Development

### Running Tests

```bash
# Quick system test
python cli.py --test

# Memory cleanup
python cli.py --cleanup

# View statistics
python cli.py --stats
```

### Adding Custom Prompts

Edit `prompts.py` to add new prompt templates:

```python
NEW_PROMPT = """
Your custom prompt template with {variables}.
"""

# Add to DaydreamerPrompts class and template registry
```

### Extending Functionality

The modular architecture makes it easy to extend:

1. Add new reasoning techniques to `chain_of_thought.py`
2. Create new creative methods in `day_dreaming.py`  
3. Extend memory capabilities in `memory_manager.py`
4. Add new AI model integrations to `ollama_integration.py`

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! This is an experimental project exploring the boundaries of AI consciousness and creativity. Areas of particular interest:

- Novel reasoning techniques
- Creative insight generation methods
- Memory and learning improvements
- Additional AI model integrations
- Consciousness and creativity research

## 📚 Documentation

For more detailed documentation:

- [CHAT_README.md](CHAT_README.md) - Chat interface details
- [RESEARCH_README.md](RESEARCH_README.md) - Research methodology
- [OLLAMA_MODEL_GUIDE.md](OLLAMA_MODEL_GUIDE.md) - Ollama setup guide

---

*"Consciousness might emerge from the complexity of our interactions, and creativity from the unexpected connections we make while dreaming."* - Daydreamer AI
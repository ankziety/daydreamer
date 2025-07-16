# 🧠 Daydreamer

**A Default Mode Network AI that can self-prompt thoughts using biologically-inspired algorithms**

Daydreamer is an experimental AI system inspired by the brain's default mode network (DMN) - the network of brain regions that's active when the mind is at rest and not focused on external tasks. This system attempts to model spontaneous thought generation, mind-wandering, and the stream of consciousness through neural network architectures.

## ✨ Features

- **Default Mode Network Architecture**: Multi-layer attention-based neural network inspired by brain connectivity patterns
- **Self-Prompting Capability**: Generates coherent streams of consciousness without external input
- **Episodic Memory Buffer**: Maintains and retrieves relevant past experiences to influence current thoughts
- **Biologically-Inspired Learning**: Uses attention mechanisms and memory consolidation similar to neural processes
- **Flexible Thought Generation**: Supports both prompted and unprompted thought generation
- **Comprehensive Testing**: Full test suite ensuring reliability and correctness

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ankziety/daydreamer.git
cd daydreamer

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Basic Usage

```python
from daydreamer import DefaultModeNetwork, ThoughtGenerator

# Create a model
model = DefaultModeNetwork(
    hidden_dim=256,
    num_layers=6,
    num_heads=8,
    memory_size=1000,
    vocab_size=10000,
)

# Create a thought generator
generator = ThoughtGenerator(model, temperature=0.8)

# Generate self-prompted thoughts
thoughts = generator.self_prompt(num_iterations=5)
for thought in thoughts:
    print(f"💭 {thought}")

# Generate thoughts from a prompt
prompted_thoughts = generator.generate_thought(
    prompt="The nature of consciousness",
    num_thoughts=3
)
```

### Command Line Interface

```bash
# Run a quick demonstration
daydreamer demo --quick

# Generate thoughts
daydreamer generate --prompt "Dreams and reality" --num-thoughts 5

# Train a new model
daydreamer train --epochs 20 --batch-size 8 --save-path my_model.pt

# Show model information
daydreamer info --model-path my_model.pt
```

## 🏗️ Architecture

### Core Components

1. **DefaultModeNetwork**: The main neural network that processes and generates thoughts
   - Multi-head self-attention layers
   - Positional encoding for sequence understanding
   - Integration with episodic memory
   - Output projection for token generation

2. **AttentionNetwork**: Multi-layer attention mechanism for modeling complex thought relationships
   - Transformer-like architecture
   - Residual connections and layer normalization
   - Support for attention masking

3. **MemoryBuffer**: Episodic memory system for storing and retrieving past experiences
   - FIFO buffer with configurable size
   - Similarity-based memory retrieval
   - Integration with attention mechanisms

4. **ThoughtGenerator**: High-level interface for thought generation and training
   - Self-prompting capabilities
   - Temperature-controlled generation
   - Training utilities

### How It Works

1. **Input Processing**: Text or prompts are embedded and combined with positional encodings
2. **Memory Integration**: Relevant past experiences are retrieved from the memory buffer
3. **Attention Processing**: Multi-layer attention networks model relationships between thoughts
4. **Memory Update**: Current thought states are stored in the episodic memory buffer
5. **Output Generation**: Processed representations are projected to generate new thoughts

## 📁 Project Structure

```
daydreamer/
├── daydreamer/           # Main package
│   ├── __init__.py       # Package initialization
│   ├── core.py           # Core DMN and ThoughtGenerator classes
│   ├── models.py         # Neural network components
│   ├── utils.py          # Utility functions
│   ├── cli.py            # Command-line interface
│   └── tests/            # Test suite
│       ├── test_core.py
│       ├── test_models.py
│       └── test_utils.py
├── examples/             # Usage examples
│   ├── basic_usage.py
│   └── training_example.py
├── requirements.txt      # Dependencies
├── pyproject.toml        # Project configuration
└── README.md            # This file
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=daydreamer

# Run specific test file
pytest tests/test_core.py

# Run with verbose output
pytest -v
```

## 📊 Examples

### Basic Usage Example

```bash
python examples/basic_usage.py
```

This demonstrates:
- Model creation and architecture
- Thought generation (self-prompted and prompted)
- Memory system functionality
- Model saving and loading

### Training Example

```bash
python examples/training_example.py
```

This shows:
- Model training procedures
- Loss monitoring and evaluation
- Memory accumulation during training
- Post-training thought quality

## 🔬 Current Capabilities

**What Daydreamer Can Do:**
- Generate coherent streams of consciousness-like text
- Learn from training data through self-supervised learning
- Maintain episodic memories that influence future thoughts
- Process input prompts and continue thought generation
- Adapt its thinking patterns based on accumulated experiences

**What It's Learning:**
- Attention patterns between different thought concepts
- Memory consolidation and retrieval strategies
- Self-prompting mechanisms for autonomous thought generation
- Contextual relationships in language and concepts

## ⚙️ Configuration

### Model Parameters

- `hidden_dim`: Dimension of hidden representations (default: 512)
- `num_layers`: Number of attention layers (default: 6)
- `num_heads`: Number of attention heads (default: 8)
- `memory_size`: Size of episodic memory buffer (default: 1000)
- `vocab_size`: Vocabulary size (default: 50000)
- `max_sequence_length`: Maximum sequence length (default: 512)

### Training Parameters

- `learning_rate`: Learning rate for training (default: 1e-4)
- `batch_size`: Training batch size (default: 4)
- `temperature`: Sampling temperature for generation (default: 0.8)

## 🛠️ Development

### Code Quality

The project includes:
- Type hints throughout the codebase
- Comprehensive docstrings
- Black code formatting
- Flake8 linting
- MyPy static type checking
- 95%+ test coverage

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure all tests pass
5. Submit a pull request

## 📈 Future Directions

- Integration with large language models for enhanced text generation
- Real-time learning and adaptation capabilities
- Multiple memory systems (working, episodic, semantic)
- Emotion and mood modeling
- Interactive conversation capabilities
- Visualization of thought patterns and memory networks

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

This project is inspired by:
- Neuroscientific research on the default mode network
- Transformer architectures and attention mechanisms
- Memory-augmented neural networks
- Consciousness and cognitive science research

---

**Note**: This is an experimental project exploring the intersection of neuroscience and artificial intelligence. The "thoughts" generated are statistical patterns learned from data, not conscious experiences.

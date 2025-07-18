# Ollama Model Selection Guide

The Daydreamer research chat system now supports automatic detection and selection of available Ollama models, including support for alternative model variants like `gemma3n:e4b`.

## Automatic Model Detection

By default, the system is now configured with `ollama_model = auto` in `research_config.ini`. This enables:

- **Automatic detection** of all available Ollama models using `ollama list`
- **Smart selection** of the best available model based on preferences
- **Priority support** for `gemma3n:e4b` and other high-end variants

## Model Priority Order

When auto-detection is enabled, the system prioritizes models in this order:

1. `gemma3n:e4b` - High-end variant (specifically requested by users)
2. `gemma3n:latest` - Latest Gemma3N version
3. `gemma3n:8b` - Larger Gemma3N model
4. `gemma3n:3b` - Standard Gemma3N model
5. `gemma:7b` - Gemma family models
6. `llama3.2:latest` - Llama family models
7. `phi3:latest` - Phi family models

## Configuration Options

### Option 1: Automatic Detection (Recommended)
```ini
[ai_models]
ollama_model = auto
```

### Option 2: Specific Model
```ini
[ai_models]
ollama_model = gemma3n:e4b
```

### Option 3: Fallback with Auto-Selection
If you specify a specific model but it's not available, the system will automatically fall back to the best available option.

## Usage Examples

### Check Available Models
```bash
python check_ollama.py
```

### Run Research Chat with Auto-Detection
```bash
python research_chat.py
```

### Test Model Selection Logic
```bash
python test_model_selection.py
```

## Sample Output

When you have `gemma3n:e4b` available, you'll see:

```
--- CONFIGURATION LOADING ---
✅ Configuration loaded from research_config.ini
   Auto-detect mode enabled
   Model preference: auto

--- AI MODEL INITIALIZATION ---
📋 Available Ollama models: gemma3n:e4b, gemma:7b, llama3.2:latest
🎯 Selected model: gemma3n:e4b
✅ Primary Model: gemma3n:e4b via Ollama
```

## Troubleshooting

1. **No models detected**: Ensure Ollama is running (`ollama serve`) and models are installed (`ollama list`)
2. **Specific model not selected**: Check that the model name matches exactly (case-sensitive)
3. **Fallback behavior**: The system will automatically fall back to transformers or minimal generator if Ollama is unavailable

## API Reference

The Ollama API documentation is available at: https://github.com/ollama/ollama/blob/main/docs/api.md
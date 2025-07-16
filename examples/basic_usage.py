"""
Basic example of using the Daydreamer AI system.

This script demonstrates how to create a model, generate thoughts,
and save/load the model.
"""

import torch
from daydreamer import DefaultModeNetwork, ThoughtGenerator
from daydreamer.utils import print_model_summary, save_model, load_model


def main():
    print("🧠 Daydreamer Basic Example")
    print("=" * 40)
    
    # Create a small model for demonstration
    model = DefaultModeNetwork(
        hidden_dim=128,
        num_layers=3,
        num_heads=8,
        memory_size=100,
        vocab_size=5000,
        max_sequence_length=256,
    )
    
    # Print model information
    print("\nModel Architecture:")
    print_model_summary(model)
    
    # Create a thought generator
    generator = ThoughtGenerator(
        model=model,
        temperature=0.8,
        max_length=100,
    )
    
    # Generate some thoughts
    print("\n💭 Generating Thoughts:")
    print("-" * 30)
    
    # Generate thoughts without a prompt (self-prompting)
    print("Self-prompted thoughts:")
    self_thoughts = generator.self_prompt(num_iterations=3)
    for i, thought in enumerate(self_thoughts, 1):
        print(f"{i}. {thought}")
    
    print()
    
    # Generate thoughts with a prompt
    prompt = "The nature of consciousness"
    print(f"Thoughts continuing from '{prompt}':")
    prompted_thoughts = generator.generate_thought(
        prompt=prompt,
        num_thoughts=3,
        use_memory=True,
    )
    for i, thought in enumerate(prompted_thoughts, 1):
        print(f"{i}. {thought}")
    
    # Demonstrate memory functionality
    print("\n🧠 Memory System Demonstration:")
    print("-" * 40)
    
    # Create some dummy input to populate memory
    dummy_input = torch.randint(0, model.vocab_size, (2, 20))
    
    # Run forward passes to build up memory
    print("Building up memory through thought processing...")
    with torch.no_grad():
        for i in range(5):
            outputs = model(dummy_input, use_memory=True)
            print(f"Memory size after pass {i+1}: {model.memory_buffer.size()}")
    
    # Show memory statistics
    memory_stats = model.memory_buffer.get_memory_summary()
    print(f"\nMemory Statistics:")
    print(f"  Total memories: {memory_stats['size']}")
    print(f"  Mean norm: {memory_stats['mean_norm']:.4f}")
    print(f"  Std norm: {memory_stats['std_norm']:.4f}")
    
    # Demonstrate memory retrieval
    query = torch.randn(1, model.hidden_dim)
    retrieved_memory = model.memory_buffer.retrieve_relevant_memories(query, top_k=3)
    if retrieved_memory is not None:
        print(f"Retrieved memory shape: {retrieved_memory.shape}")
        print(f"Retrieved memory norm: {retrieved_memory.norm().item():.4f}")
    
    # Save the model
    print("\n💾 Saving Model:")
    print("-" * 20)
    model_path = "example_model.pt"
    save_model(model, model_path, metadata={
        'example': 'basic_usage',
        'memory_size': memory_stats['size'],
    })
    
    # Load the model back
    print("\n📂 Loading Model:")
    print("-" * 20)
    loaded_model = load_model(model_path)
    
    # Verify the loaded model works
    loaded_generator = ThoughtGenerator(loaded_model)
    verification_thought = loaded_generator.generate_thought(
        prompt="Verification test",
        num_thoughts=1,
    )
    print(f"Verification thought: {verification_thought[0]}")
    
    print("\n✨ Example completed successfully!")


if __name__ == "__main__":
    main()
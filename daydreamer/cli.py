"""
Command-line interface for the Daydreamer AI system.

This module provides a CLI for training, generating thoughts, and
interacting with the default mode network.
"""

import argparse
import torch
import sys
from typing import Optional

from .core import DefaultModeNetwork, ThoughtGenerator
from .utils import save_model, load_model, print_model_summary, generate_dummy_data


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        description="Daydreamer: A Default Mode Network AI"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate command
    generate_parser = subparsers.add_parser(
        'generate', help='Generate thoughts using the model'
    )
    generate_parser.add_argument(
        '--model-path', type=str, help='Path to trained model'
    )
    generate_parser.add_argument(
        '--prompt', type=str, help='Starting prompt for thought generation'
    )
    generate_parser.add_argument(
        '--num-thoughts', type=int, default=5, help='Number of thoughts to generate'
    )
    generate_parser.add_argument(
        '--temperature', type=float, default=0.8, help='Sampling temperature'
    )
    
    # Train command
    train_parser = subparsers.add_parser(
        'train', help='Train the default mode network'
    )
    train_parser.add_argument(
        '--epochs', type=int, default=10, help='Number of training epochs'
    )
    train_parser.add_argument(
        '--batch-size', type=int, default=4, help='Training batch size'
    )
    train_parser.add_argument(
        '--learning-rate', type=float, default=1e-4, help='Learning rate'
    )
    train_parser.add_argument(
        '--save-path', type=str, default='model.pt', help='Path to save trained model'
    )
    
    # Demo command
    demo_parser = subparsers.add_parser(
        'demo', help='Run a demonstration of the system'
    )
    demo_parser.add_argument(
        '--quick', action='store_true', help='Run a quick demo'
    )
    
    # Info command
    info_parser = subparsers.add_parser(
        'info', help='Display model information'
    )
    info_parser.add_argument(
        '--model-path', type=str, help='Path to model file'
    )
    
    return parser


def generate_thoughts(args):
    """Generate thoughts using a trained model."""
    print("🧠 Daydreamer - Thought Generation")
    print("=" * 40)
    
    if args.model_path:
        try:
            model = load_model(args.model_path)
            print(f"Loaded model from {args.model_path}")
        except Exception as e:
            print(f"Error loading model: {e}")
            return
    else:
        print("Creating new model for demonstration...")
        model = DefaultModeNetwork(
            hidden_dim=256,
            num_layers=4,
            num_heads=8,
            memory_size=100,
            vocab_size=1000,
        )
    
    generator = ThoughtGenerator(
        model=model,
        temperature=args.temperature,
    )
    
    if args.prompt:
        print(f"\nPrompt: '{args.prompt}'")
        thoughts = generator.generate_thought(
            prompt=args.prompt,
            num_thoughts=args.num_thoughts,
        )
    else:
        print("\nGenerating self-prompted thoughts...")
        thoughts = generator.self_prompt(num_iterations=args.num_thoughts)
    
    print("\nGenerated Thoughts:")
    print("-" * 20)
    for i, thought in enumerate(thoughts, 1):
        print(f"{i}. {thought}")
    print()


def train_model(args):
    """Train a new default mode network."""
    print("🎓 Daydreamer - Training Mode")
    print("=" * 40)
    
    # Create model
    model = DefaultModeNetwork(
        hidden_dim=512,
        num_layers=6,
        num_heads=8,
        memory_size=1000,
        vocab_size=10000,
    )
    
    print_model_summary(model)
    
    # Setup training
    optimizer = torch.optim.Adam(model.parameters(), lr=args.learning_rate)
    generator = ThoughtGenerator(model)
    
    print(f"\nStarting training for {args.epochs} epochs...")
    
    for epoch in range(args.epochs):
        # Generate dummy training data
        dummy_data = generate_dummy_data(
            batch_size=args.batch_size,
            sequence_length=50,
            vocab_size=model.vocab_size,
        )
        
        # Training step
        loss = generator.train_step(
            input_ids=dummy_data['input_ids'],
            target_ids=dummy_data['input_ids'],  # Self-supervised
            optimizer=optimizer,
        )
        
        if epoch % max(1, args.epochs // 10) == 0:
            print(f"Epoch {epoch+1}/{args.epochs}, Loss: {loss:.4f}")
    
    # Save model
    save_model(model, args.save_path, metadata={
        'epochs': args.epochs,
        'final_loss': loss,
        'batch_size': args.batch_size,
        'learning_rate': args.learning_rate,
    })
    
    print(f"\nTraining completed! Model saved to {args.save_path}")


def run_demo(args):
    """Run a demonstration of the system."""
    print("🌟 Daydreamer - Demo Mode")
    print("=" * 40)
    
    # Create a small model for demo
    model = DefaultModeNetwork(
        hidden_dim=128 if args.quick else 256,
        num_layers=2 if args.quick else 4,
        num_heads=4 if args.quick else 8,
        memory_size=50 if args.quick else 200,
        vocab_size=1000,
    )
    
    print("Model Architecture:")
    print_model_summary(model)
    
    # Demonstrate memory buffer
    print("\n📚 Memory Buffer Demo:")
    memory = model.memory_buffer
    
    # Add some dummy memories
    dummy_states = torch.randn(5, model.hidden_dim)
    memory.update(dummy_states)
    print(f"Added 5 memories. Buffer size: {memory.size()}")
    
    # Retrieve memories
    query = torch.randn(1, model.hidden_dim)
    retrieved = memory.retrieve_relevant_memories(query)
    print(f"Retrieved memory shape: {retrieved.shape if retrieved is not None else 'None'}")
    
    # Demonstrate thought generation
    print("\n💭 Thought Generation Demo:")
    generator = ThoughtGenerator(model, temperature=0.9)
    
    # Self-prompted thoughts
    thoughts = generator.self_prompt(num_iterations=3)
    for i, thought in enumerate(thoughts, 1):
        print(f"  {i}. {thought}")
    
    # Test model forward pass
    print("\n🔧 Model Forward Pass Demo:")
    dummy_data = generate_dummy_data(
        batch_size=2,
        sequence_length=10,
        vocab_size=model.vocab_size,
    )
    
    with torch.no_grad():
        outputs = model(dummy_data['input_ids'])
        print(f"Input shape: {dummy_data['input_ids'].shape}")
        print(f"Output logits shape: {outputs['logits'].shape}")
        print(f"Number of attention layers: {len(outputs['attention_weights'])}")
    
    print("\n✨ Demo completed successfully!")


def show_model_info(args):
    """Display information about a model."""
    if not args.model_path:
        print("Please provide a model path with --model-path")
        return
    
    try:
        model = load_model(args.model_path)
        print_model_summary(model)
        
        # Show memory buffer info if available
        memory_info = model.memory_buffer.get_memory_summary()
        print("\nMemory Buffer Status:")
        print(f"  Memories stored: {memory_info['size']}")
        print(f"  Mean norm: {memory_info['mean_norm']:.4f}")
        print(f"  Std norm: {memory_info['std_norm']:.4f}")
        
    except Exception as e:
        print(f"Error loading model: {e}")


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'generate':
            generate_thoughts(args)
        elif args.command == 'train':
            train_model(args)
        elif args.command == 'demo':
            run_demo(args)
        elif args.command == 'info':
            show_model_info(args)
        else:
            print(f"Unknown command: {args.command}")
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
"""
Training example for the Daydreamer AI system.

This script demonstrates how to train the default mode network
using dummy data and basic training procedures.
"""

import torch
import torch.optim as optim
from daydreamer import DefaultModeNetwork, ThoughtGenerator
from daydreamer.utils import generate_dummy_data, print_model_summary, save_model


def create_training_data(num_batches, batch_size, sequence_length, vocab_size):
    """Generate dummy training data."""
    training_data = []
    for _ in range(num_batches):
        data = generate_dummy_data(batch_size, sequence_length, vocab_size)
        training_data.append(data)
    return training_data


def train_model(
    model,
    training_data,
    optimizer,
    num_epochs=5,
    print_every=1,
):
    """Train the model on the provided data."""
    generator = ThoughtGenerator(model)
    total_loss = 0.0
    num_batches = len(training_data)
    
    print(f"Starting training for {num_epochs} epochs...")
    print(f"Training data: {num_batches} batches")
    
    model.train()
    
    for epoch in range(num_epochs):
        epoch_loss = 0.0
        
        for batch_idx, batch_data in enumerate(training_data):
            input_ids = batch_data['input_ids']
            target_ids = input_ids.clone()  # Self-supervised learning
            
            # Training step
            loss = generator.train_step(input_ids, target_ids, optimizer)
            epoch_loss += loss
            total_loss += loss
        
        avg_epoch_loss = epoch_loss / num_batches
        
        if epoch % print_every == 0:
            print(f"Epoch {epoch+1}/{num_epochs}, Average Loss: {avg_epoch_loss:.4f}")
            
            # Generate a sample thought to see progress
            with torch.no_grad():
                model.eval()
                sample_thoughts = generator.generate_thought(num_thoughts=1)
                print(f"  Sample thought: {sample_thoughts[0][:100]}...")
                model.train()
    
    avg_total_loss = total_loss / (num_epochs * num_batches)
    print(f"\nTraining completed! Average loss: {avg_total_loss:.4f}")
    
    return avg_total_loss


def evaluate_model(model, test_data):
    """Evaluate the model on test data."""
    model.eval()
    total_loss = 0.0
    num_batches = len(test_data)
    
    print("Evaluating model...")
    
    with torch.no_grad():
        for batch_data in test_data:
            input_ids = batch_data['input_ids']
            
            outputs = model(input_ids)
            # Calculate loss (simplified evaluation)
            loss = torch.nn.functional.cross_entropy(
                outputs['logits'].view(-1, outputs['logits'].size(-1)),
                input_ids.view(-1),
                ignore_index=-100,
            )
            total_loss += loss.item()
    
    avg_loss = total_loss / num_batches
    print(f"Evaluation loss: {avg_loss:.4f}")
    
    return avg_loss


def main():
    print("🎓 Daydreamer Training Example")
    print("=" * 40)
    
    # Set random seed for reproducibility
    torch.manual_seed(42)
    
    # Model configuration
    config = {
        'hidden_dim': 256,
        'num_layers': 4,
        'num_heads': 8,
        'memory_size': 200,
        'vocab_size': 2000,
        'max_sequence_length': 128,
    }
    
    # Create model
    print("Creating model...")
    model = DefaultModeNetwork(**config)
    print_model_summary(model)
    
    # Training configuration
    training_config = {
        'num_epochs': 10,
        'batch_size': 4,
        'sequence_length': 32,
        'learning_rate': 1e-4,
        'num_train_batches': 50,
        'num_test_batches': 10,
    }
    
    print(f"\nTraining configuration:")
    for key, value in training_config.items():
        print(f"  {key}: {value}")
    
    # Create optimizer
    optimizer = optim.Adam(model.parameters(), lr=training_config['learning_rate'])
    
    # Generate training and test data
    print("\nGenerating training data...")
    training_data = create_training_data(
        num_batches=training_config['num_train_batches'],
        batch_size=training_config['batch_size'],
        sequence_length=training_config['sequence_length'],
        vocab_size=config['vocab_size'],
    )
    
    print("Generating test data...")
    test_data = create_training_data(
        num_batches=training_config['num_test_batches'],
        batch_size=training_config['batch_size'],
        sequence_length=training_config['sequence_length'],
        vocab_size=config['vocab_size'],
    )
    
    # Pre-training evaluation
    print("\n📊 Pre-training Evaluation:")
    pre_train_loss = evaluate_model(model, test_data)
    
    # Train the model
    print("\n🏋️ Training Phase:")
    print("-" * 30)
    final_loss = train_model(
        model=model,
        training_data=training_data,
        optimizer=optimizer,
        num_epochs=training_config['num_epochs'],
        print_every=2,
    )
    
    # Post-training evaluation
    print("\n📊 Post-training Evaluation:")
    post_train_loss = evaluate_model(model, test_data)
    
    print(f"\nTraining Results:")
    print(f"  Pre-training loss: {pre_train_loss:.4f}")
    print(f"  Post-training loss: {post_train_loss:.4f}")
    print(f"  Improvement: {((pre_train_loss - post_train_loss) / pre_train_loss * 100):.2f}%")
    
    # Generate sample thoughts with the trained model
    print("\n💭 Sample Thoughts from Trained Model:")
    print("-" * 45)
    model.eval()
    generator = ThoughtGenerator(model, temperature=0.7)
    
    # Self-prompted thoughts
    thoughts = generator.self_prompt(num_iterations=5)
    for i, thought in enumerate(thoughts, 1):
        print(f"{i}. {thought}")
    
    # Memory analysis
    print("\n🧠 Memory System Analysis:")
    print("-" * 30)
    memory_stats = model.memory_buffer.get_memory_summary()
    print(f"Memories accumulated during training: {memory_stats['size']}")
    print(f"Memory diversity (std norm): {memory_stats['std_norm']:.4f}")
    
    # Save the trained model
    print("\n💾 Saving Trained Model:")
    print("-" * 25)
    model_path = "trained_daydreamer_model.pt"
    metadata = {
        'training_config': training_config,
        'model_config': config,
        'final_loss': final_loss,
        'pre_train_loss': pre_train_loss,
        'post_train_loss': post_train_loss,
        'memory_size': memory_stats['size'],
    }
    
    save_model(model, model_path, metadata=metadata)
    
    print(f"\n✨ Training example completed successfully!")
    print(f"Trained model saved as: {model_path}")


if __name__ == "__main__":
    main()
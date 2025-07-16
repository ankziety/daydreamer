"""
Utility functions for the Daydreamer AI system.

This module provides helper functions for model management, data processing,
and other common operations.
"""

import torch
import json
import os
from typing import Dict, Any, Optional
from .core import DefaultModeNetwork


def save_model(
    model: DefaultModeNetwork,
    filepath: str,
    metadata: Optional[Dict[str, Any]] = None,
):
    """
    Save a trained model to disk.
    
    Args:
        model: The model to save
        filepath: Path where to save the model
        metadata: Optional metadata to save with the model
    """
    directory = os.path.dirname(filepath)
    if directory:  # Only create directory if filepath has a directory component
        os.makedirs(directory, exist_ok=True)
    
    save_dict = {
        'model_state_dict': model.state_dict(),
        'model_config': {
            'hidden_dim': model.hidden_dim,
            'num_layers': model.num_layers,
            'num_heads': model.num_heads,
            'memory_size': model.memory_size,
            'vocab_size': model.vocab_size,
            'max_sequence_length': model.max_sequence_length,
        },
        'metadata': metadata or {},
    }
    
    torch.save(save_dict, filepath)
    print(f"Model saved to {filepath}")


def load_model(filepath: str, device: str = 'cpu') -> DefaultModeNetwork:
    """
    Load a model from disk.
    
    Args:
        filepath: Path to the saved model
        device: Device to load the model on
        
    Returns:
        Loaded model instance
    """
    checkpoint = torch.load(filepath, map_location=device)
    config = checkpoint['model_config']
    
    model = DefaultModeNetwork(
        hidden_dim=config['hidden_dim'],
        num_layers=config['num_layers'],
        num_heads=config['num_heads'],
        memory_size=config['memory_size'],
        vocab_size=config['vocab_size'],
        max_sequence_length=config['max_sequence_length'],
    )
    
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    
    print(f"Model loaded from {filepath}")
    if 'metadata' in checkpoint:
        print(f"Metadata: {checkpoint['metadata']}")
    
    return model


def count_parameters(model: torch.nn.Module) -> Dict[str, int]:
    """
    Count the number of parameters in a model.
    
    Args:
        model: PyTorch model
        
    Returns:
        Dictionary with parameter counts
    """
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    return {
        'total': total_params,
        'trainable': trainable_params,
        'non_trainable': total_params - trainable_params,
    }


def create_attention_mask(sequence_lengths: torch.Tensor, max_length: int) -> torch.Tensor:
    """
    Create attention mask from sequence lengths.
    
    Args:
        sequence_lengths: Tensor of sequence lengths
        max_length: Maximum sequence length
        
    Returns:
        Attention mask tensor
    """
    batch_size = sequence_lengths.size(0)
    mask = torch.arange(max_length).expand(batch_size, max_length) < sequence_lengths.unsqueeze(1)
    return mask.float()


def generate_dummy_data(
    batch_size: int,
    sequence_length: int,
    vocab_size: int,
    device: str = 'cpu',
) -> Dict[str, torch.Tensor]:
    """
    Generate dummy data for testing purposes.
    
    Args:
        batch_size: Number of sequences
        sequence_length: Length of each sequence
        vocab_size: Size of vocabulary
        device: Device to create tensors on
        
    Returns:
        Dictionary with input_ids and attention_mask
    """
    input_ids = torch.randint(
        0, vocab_size, (batch_size, sequence_length), device=device
    )
    attention_mask = torch.ones(
        (batch_size, sequence_length), device=device, dtype=torch.float
    )
    
    return {
        'input_ids': input_ids,
        'attention_mask': attention_mask,
    }


def print_model_summary(model: DefaultModeNetwork):
    """
    Print a summary of the model architecture.
    
    Args:
        model: The model to summarize
    """
    param_counts = count_parameters(model)
    
    print("=" * 50)
    print("Daydreamer Model Summary")
    print("=" * 50)
    print(f"Hidden dimension: {model.hidden_dim}")
    print(f"Number of layers: {model.num_layers}")
    print(f"Number of attention heads: {model.num_heads}")
    print(f"Memory buffer size: {model.memory_size}")
    print(f"Vocabulary size: {model.vocab_size}")
    print(f"Max sequence length: {model.max_sequence_length}")
    print("-" * 30)
    print(f"Total parameters: {param_counts['total']:,}")
    print(f"Trainable parameters: {param_counts['trainable']:,}")
    print(f"Non-trainable parameters: {param_counts['non_trainable']:,}")
    print("=" * 50)


def setup_logging(log_level: str = 'INFO', log_file: Optional[str] = None):
    """
    Setup logging configuration.
    
    Args:
        log_level: Logging level
        log_file: Optional log file path
    """
    import logging
    
    # Configure logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Set up handlers
    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=handlers,
    )
    
    # Get logger for this module
    logger = logging.getLogger('daydreamer')
    logger.info("Logging configured successfully")
    
    return logger
"""
Core components of the Daydreamer AI system.

This module implements the main DefaultModeNetwork and ThoughtGenerator classes
that form the foundation of the self-prompting AI system.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List, Dict, Optional, Tuple
import numpy as np
from .models import AttentionNetwork, MemoryBuffer


class DefaultModeNetwork(nn.Module):
    """
    A neural network architecture inspired by the brain's default mode network.
    
    The default mode network is active when the mind is at rest and not focused
    on external tasks. This implementation attempts to model this through
    self-attention mechanisms and memory-driven thought generation.
    """
    
    def __init__(
        self,
        hidden_dim: int = 512,
        num_layers: int = 6,
        num_heads: int = 8,
        memory_size: int = 1000,
        vocab_size: int = 50000,
        max_sequence_length: int = 512,
    ):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.num_heads = num_heads
        self.memory_size = memory_size
        self.vocab_size = vocab_size
        self.max_sequence_length = max_sequence_length
        
        # Core components
        self.embedding = nn.Embedding(vocab_size, hidden_dim)
        self.positional_encoding = self._create_positional_encoding()
        self.attention_network = AttentionNetwork(
            hidden_dim, num_heads, num_layers
        )
        self.memory_buffer = MemoryBuffer(memory_size, hidden_dim)
        
        # Output projection
        self.output_projection = nn.Linear(hidden_dim, vocab_size)
        self.dropout = nn.Dropout(0.1)
        
        # Initialize weights
        self._init_weights()
    
    def _create_positional_encoding(self) -> torch.Tensor:
        """Create sinusoidal positional encodings."""
        pe = torch.zeros(self.max_sequence_length, self.hidden_dim)
        position = torch.arange(0, self.max_sequence_length, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(
            torch.arange(0, self.hidden_dim, 2).float() * 
            (-np.log(10000.0) / self.hidden_dim)
        )
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        return pe.unsqueeze(0)
    
    def _init_weights(self):
        """Initialize model weights using Xavier initialization."""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
            elif isinstance(module, nn.Embedding):
                nn.init.normal_(module.weight, mean=0, std=0.02)
    
    def forward(
        self, 
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        use_memory: bool = True,
    ) -> Dict[str, torch.Tensor]:
        """
        Forward pass through the default mode network.
        
        Args:
            input_ids: Token IDs of shape (batch_size, sequence_length)
            attention_mask: Attention mask of shape (batch_size, sequence_length)
            use_memory: Whether to incorporate memory buffer
            
        Returns:
            Dictionary containing logits, hidden_states, and attention_weights
        """
        batch_size, seq_len = input_ids.shape
        device = input_ids.device
        
        # Embedding and positional encoding
        embeddings = self.embedding(input_ids)
        pos_encoding = self.positional_encoding[:, :seq_len, :].to(device)
        hidden_states = self.dropout(embeddings + pos_encoding)
        
        # Incorporate memory if requested
        if use_memory:
            memory_context = self.memory_buffer.retrieve_relevant_memories(
                hidden_states.mean(dim=1)  # Use mean pooled representation as query
            )
            if memory_context is not None:
                # Concatenate memory context to hidden states
                memory_context = memory_context.unsqueeze(1).expand(-1, seq_len, -1)
                hidden_states = hidden_states + 0.1 * memory_context
        
        # Apply attention network
        attention_output = self.attention_network(
            hidden_states, attention_mask=attention_mask
        )
        
        # Generate output logits
        logits = self.output_projection(attention_output['hidden_states'])
        
        # Update memory buffer with current hidden states
        if use_memory:
            self.memory_buffer.update(hidden_states.mean(dim=1).detach())
        
        return {
            'logits': logits,
            'hidden_states': attention_output['hidden_states'],
            'attention_weights': attention_output['attention_weights'],
        }


class ThoughtGenerator:
    """
    High-level interface for generating thoughts using the DefaultModeNetwork.
    
    This class provides methods for generating coherent streams of consciousness,
    self-prompting, and managing the thought generation process.
    """
    
    def __init__(
        self,
        model: DefaultModeNetwork,
        tokenizer=None,  # Will be imported when needed
        temperature: float = 0.8,
        max_length: int = 200,
    ):
        self.model = model
        self.tokenizer = tokenizer
        self.temperature = temperature
        self.max_length = max_length
        self.model.eval()
    
    def generate_thought(
        self,
        prompt: Optional[str] = None,
        num_thoughts: int = 1,
        use_memory: bool = True,
    ) -> List[str]:
        """
        Generate thoughts based on a prompt or from the default mode.
        
        Args:
            prompt: Optional starting prompt
            num_thoughts: Number of thoughts to generate
            use_memory: Whether to use memory buffer
            
        Returns:
            List of generated thought strings
        """
        if self.tokenizer is None:
            # Return placeholder thoughts for now
            thoughts = []
            for i in range(num_thoughts):
                if prompt:
                    thought = f"Continuing from '{prompt}': Generated thought {i+1} using default mode network..."
                else:
                    thought = f"Self-prompted thought {i+1}: The mind wanders through interconnected patterns..."
                thoughts.append(thought)
            return thoughts
        
        # TODO: Implement actual tokenizer-based generation
        # This would involve tokenizing the prompt, running through the model,
        # and decoding the output tokens back to text
        pass
    
    def self_prompt(self, num_iterations: int = 5) -> List[str]:
        """
        Generate a stream of self-prompted thoughts.
        
        This method starts without any external prompt and generates
        thoughts that build upon each other, simulating the natural
        flow of consciousness.
        
        Args:
            num_iterations: Number of thought iterations
            
        Returns:
            List of self-prompted thoughts
        """
        thoughts = []
        current_prompt = None
        
        for i in range(num_iterations):
            new_thoughts = self.generate_thought(
                prompt=current_prompt,
                num_thoughts=1,
                use_memory=True,
            )
            thoughts.extend(new_thoughts)
            # Use the last generated thought as the next prompt
            current_prompt = new_thoughts[-1][-50:]  # Use last 50 chars as prompt
        
        return thoughts
    
    def train_step(
        self,
        input_ids: torch.Tensor,
        target_ids: torch.Tensor,
        optimizer: torch.optim.Optimizer,
    ) -> float:
        """
        Perform a single training step.
        
        Args:
            input_ids: Input token sequences
            target_ids: Target token sequences  
            optimizer: Optimizer instance
            
        Returns:
            Training loss value
        """
        self.model.train()
        optimizer.zero_grad()
        
        outputs = self.model(input_ids)
        loss = F.cross_entropy(
            outputs['logits'].view(-1, outputs['logits'].size(-1)),
            target_ids.view(-1),
            ignore_index=-100,
        )
        
        loss.backward()
        optimizer.step()
        
        return loss.item()
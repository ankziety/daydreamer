"""
Neural network models and components for the Daydreamer AI system.

This module contains the AttentionNetwork and MemoryBuffer classes that
support the core DefaultModeNetwork functionality.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Dict, List
import math
import numpy as np


class MultiHeadAttention(nn.Module):
    """Multi-head attention mechanism."""
    
    def __init__(self, hidden_dim: int, num_heads: int):
        super().__init__()
        assert hidden_dim % num_heads == 0
        
        self.hidden_dim = hidden_dim
        self.num_heads = num_heads
        self.head_dim = hidden_dim // num_heads
        
        self.q_linear = nn.Linear(hidden_dim, hidden_dim)
        self.k_linear = nn.Linear(hidden_dim, hidden_dim)
        self.v_linear = nn.Linear(hidden_dim, hidden_dim)
        self.out_linear = nn.Linear(hidden_dim, hidden_dim)
        
        self.dropout = nn.Dropout(0.1)
    
    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Dict[str, torch.Tensor]:
        batch_size, seq_len, _ = query.shape
        
        # Linear projections
        Q = self.q_linear(query).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        K = self.k_linear(key).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        V = self.v_linear(value).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        
        # Scaled dot-product attention
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.head_dim)
        
        if attention_mask is not None:
            # Apply attention mask
            attention_mask = attention_mask.unsqueeze(1).unsqueeze(1)
            scores = scores.masked_fill(attention_mask == 0, -1e9)
        
        attention_weights = F.softmax(scores, dim=-1)
        attention_weights = self.dropout(attention_weights)
        
        context = torch.matmul(attention_weights, V)
        
        # Concatenate heads
        context = context.transpose(1, 2).contiguous().view(
            batch_size, seq_len, self.hidden_dim
        )
        
        output = self.out_linear(context)
        
        return {
            'output': output,
            'attention_weights': attention_weights,
        }


class FeedForward(nn.Module):
    """Position-wise feed-forward network."""
    
    def __init__(self, hidden_dim: int, ff_dim: int = None):
        super().__init__()
        if ff_dim is None:
            ff_dim = hidden_dim * 4
        
        self.linear1 = nn.Linear(hidden_dim, ff_dim)
        self.linear2 = nn.Linear(ff_dim, hidden_dim)
        self.dropout = nn.Dropout(0.1)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.linear2(self.dropout(F.gelu(self.linear1(x))))


class AttentionLayer(nn.Module):
    """Single transformer-like attention layer."""
    
    def __init__(self, hidden_dim: int, num_heads: int):
        super().__init__()
        self.attention = MultiHeadAttention(hidden_dim, num_heads)
        self.feed_forward = FeedForward(hidden_dim)
        self.norm1 = nn.LayerNorm(hidden_dim)
        self.norm2 = nn.LayerNorm(hidden_dim)
        self.dropout = nn.Dropout(0.1)
    
    def forward(
        self,
        x: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Dict[str, torch.Tensor]:
        # Self-attention with residual connection
        attn_output = self.attention(x, x, x, attention_mask)
        x = self.norm1(x + self.dropout(attn_output['output']))
        
        # Feed-forward with residual connection
        ff_output = self.feed_forward(x)
        x = self.norm2(x + self.dropout(ff_output))
        
        return {
            'output': x,
            'attention_weights': attn_output['attention_weights'],
        }


class AttentionNetwork(nn.Module):
    """
    Multi-layer attention network for processing thought representations.
    
    This network applies multiple layers of self-attention to model
    complex relationships within and between thoughts.
    """
    
    def __init__(self, hidden_dim: int, num_heads: int, num_layers: int):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.num_heads = num_heads
        self.num_layers = num_layers
        
        self.layers = nn.ModuleList([
            AttentionLayer(hidden_dim, num_heads)
            for _ in range(num_layers)
        ])
    
    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Dict[str, torch.Tensor]:
        """
        Forward pass through the attention network.
        
        Args:
            hidden_states: Input hidden states of shape (batch_size, seq_len, hidden_dim)
            attention_mask: Optional attention mask
            
        Returns:
            Dictionary containing processed hidden states and attention weights
        """
        all_attention_weights = []
        
        for layer in self.layers:
            layer_output = layer(hidden_states, attention_mask)
            hidden_states = layer_output['output']
            all_attention_weights.append(layer_output['attention_weights'])
        
        return {
            'hidden_states': hidden_states,
            'attention_weights': all_attention_weights,
        }


class MemoryBuffer:
    """
    A memory buffer that stores and retrieves relevant past experiences.
    
    This component simulates long-term memory by maintaining a buffer
    of past hidden states and providing mechanisms to retrieve
    contextually relevant memories.
    """
    
    def __init__(self, memory_size: int, hidden_dim: int):
        self.memory_size = memory_size
        self.hidden_dim = hidden_dim
        self.memory_bank = []
        self.memory_embeddings = None
        self.current_size = 0
    
    def update(self, hidden_states: torch.Tensor):
        """
        Update the memory buffer with new hidden states.
        
        Args:
            hidden_states: New hidden states to store (batch_size, hidden_dim)
        """
        batch_size = hidden_states.shape[0]
        
        for i in range(batch_size):
            state = hidden_states[i].detach().cpu().numpy()
            
            if self.current_size < self.memory_size:
                self.memory_bank.append(state)
                self.current_size += 1
            else:
                # Replace oldest memory (FIFO)
                self.memory_bank[self.current_size % self.memory_size] = state
                self.current_size += 1
        
        # Update embeddings tensor
        if self.memory_bank:
            memory_array = np.array(self.memory_bank[:min(len(self.memory_bank), self.memory_size)])
            self.memory_embeddings = torch.tensor(
                memory_array,
                dtype=torch.float32,
            )
    
    def retrieve_relevant_memories(
        self,
        query: torch.Tensor,
        top_k: int = 5,
    ) -> Optional[torch.Tensor]:
        """
        Retrieve the most relevant memories based on the query.
        
        Args:
            query: Query hidden state (batch_size, hidden_dim)
            top_k: Number of top memories to retrieve
            
        Returns:
            Retrieved memory representations or None if no memories exist
        """
        if self.memory_embeddings is None or len(self.memory_bank) == 0:
            return None
        
        device = query.device
        batch_size = query.shape[0]
        
        # Move memory embeddings to the same device as query
        memory_embeddings = self.memory_embeddings.to(device)
        
        # Calculate similarities between query and all memories
        similarities = torch.matmul(query, memory_embeddings.T)  # (batch_size, memory_size)
        
        # Get top-k most similar memories
        top_k = min(top_k, memory_embeddings.shape[0])
        _, top_indices = torch.topk(similarities, k=top_k, dim=-1)
        
        # Retrieve and average the top memories for each query
        retrieved_memories = []
        for i in range(batch_size):
            batch_memories = memory_embeddings[top_indices[i]]  # (top_k, hidden_dim)
            avg_memory = batch_memories.mean(dim=0)  # (hidden_dim,)
            retrieved_memories.append(avg_memory)
        
        return torch.stack(retrieved_memories)  # (batch_size, hidden_dim)
    
    def clear(self):
        """Clear all memories from the buffer."""
        self.memory_bank = []
        self.memory_embeddings = None
        self.current_size = 0
    
    def size(self) -> int:
        """Return the current number of memories stored."""
        return len(self.memory_bank)
    
    def get_memory_summary(self) -> Dict[str, float]:
        """Get summary statistics about the memory buffer."""
        if not self.memory_bank:
            return {'size': 0, 'mean_norm': 0.0, 'std_norm': 0.0}
        
        norms = [torch.tensor(mem).norm().item() for mem in self.memory_bank]
        return {
            'size': len(self.memory_bank),
            'mean_norm': sum(norms) / len(norms),
            'std_norm': torch.tensor(norms).std().item(),
        }
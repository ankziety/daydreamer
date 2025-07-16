"""
Tests for the models module.
"""

import pytest
import torch
import numpy as np
from daydreamer.models import (
    MultiHeadAttention,
    FeedForward,
    AttentionLayer,
    AttentionNetwork,
    MemoryBuffer,
)


class TestMultiHeadAttention:
    """Test cases for MultiHeadAttention."""
    
    @pytest.fixture
    def attention(self):
        """Create attention module for testing."""
        return MultiHeadAttention(hidden_dim=64, num_heads=8)
    
    def test_initialization(self, attention):
        """Test attention module initialization."""
        assert attention.hidden_dim == 64
        assert attention.num_heads == 8
        assert attention.head_dim == 8
    
    def test_forward_pass(self, attention):
        """Test forward pass through attention."""
        batch_size, seq_len, hidden_dim = 2, 10, 64
        x = torch.randn(batch_size, seq_len, hidden_dim)
        
        output = attention(x, x, x)
        
        assert 'output' in output
        assert 'attention_weights' in output
        assert output['output'].shape == (batch_size, seq_len, hidden_dim)
        assert output['attention_weights'].shape == (batch_size, 8, seq_len, seq_len)
    
    def test_with_attention_mask(self, attention):
        """Test attention with mask."""
        batch_size, seq_len, hidden_dim = 2, 10, 64
        x = torch.randn(batch_size, seq_len, hidden_dim)
        mask = torch.ones(batch_size, seq_len)
        mask[0, 5:] = 0  # Mask second half of first sequence
        
        output = attention(x, x, x, attention_mask=mask)
        
        assert output['output'].shape == (batch_size, seq_len, hidden_dim)
        assert not torch.isnan(output['output']).any()


class TestFeedForward:
    """Test cases for FeedForward network."""
    
    @pytest.fixture
    def ff(self):
        """Create feed-forward module for testing."""
        return FeedForward(hidden_dim=64, ff_dim=256)
    
    def test_initialization(self, ff):
        """Test feed-forward initialization."""
        assert ff.linear1.in_features == 64
        assert ff.linear1.out_features == 256
        assert ff.linear2.in_features == 256
        assert ff.linear2.out_features == 64
    
    def test_forward_pass(self, ff):
        """Test forward pass through feed-forward network."""
        batch_size, seq_len, hidden_dim = 2, 10, 64
        x = torch.randn(batch_size, seq_len, hidden_dim)
        
        output = ff(x)
        
        assert output.shape == (batch_size, seq_len, hidden_dim)
        assert not torch.isnan(output).any()
    
    def test_default_ff_dim(self):
        """Test default feed-forward dimension."""
        ff = FeedForward(hidden_dim=64)
        assert ff.linear1.out_features == 256  # 64 * 4


class TestAttentionLayer:
    """Test cases for AttentionLayer."""
    
    @pytest.fixture
    def layer(self):
        """Create attention layer for testing."""
        return AttentionLayer(hidden_dim=64, num_heads=8)
    
    def test_forward_pass(self, layer):
        """Test forward pass through attention layer."""
        batch_size, seq_len, hidden_dim = 2, 10, 64
        x = torch.randn(batch_size, seq_len, hidden_dim)
        
        output = layer(x)
        
        assert 'output' in output
        assert 'attention_weights' in output
        assert output['output'].shape == (batch_size, seq_len, hidden_dim)
    
    def test_residual_connections(self, layer):
        """Test that residual connections work properly."""
        batch_size, seq_len, hidden_dim = 1, 5, 64
        x = torch.randn(batch_size, seq_len, hidden_dim)
        
        # Store original input
        original_norm = x.norm()
        
        output = layer(x)
        
        # Output should be different from input due to processing
        assert not torch.allclose(output['output'], x, atol=1e-6)
        
        # But not completely different due to residual connections
        output_norm = output['output'].norm()
        assert abs(output_norm - original_norm) < original_norm  # Should be reasonably close


class TestAttentionNetwork:
    """Test cases for AttentionNetwork."""
    
    @pytest.fixture
    def network(self):
        """Create attention network for testing."""
        return AttentionNetwork(hidden_dim=64, num_heads=8, num_layers=3)
    
    def test_initialization(self, network):
        """Test network initialization."""
        assert network.hidden_dim == 64
        assert network.num_heads == 8
        assert network.num_layers == 3
        assert len(network.layers) == 3
    
    def test_forward_pass(self, network):
        """Test forward pass through the network."""
        batch_size, seq_len, hidden_dim = 2, 10, 64
        x = torch.randn(batch_size, seq_len, hidden_dim)
        
        output = network(x)
        
        assert 'hidden_states' in output
        assert 'attention_weights' in output
        assert output['hidden_states'].shape == (batch_size, seq_len, hidden_dim)
        assert len(output['attention_weights']) == 3  # One per layer
    
    def test_with_attention_mask(self, network):
        """Test network with attention mask."""
        batch_size, seq_len, hidden_dim = 2, 10, 64
        x = torch.randn(batch_size, seq_len, hidden_dim)
        mask = torch.ones(batch_size, seq_len)
        
        output = network(x, attention_mask=mask)
        
        assert output['hidden_states'].shape == (batch_size, seq_len, hidden_dim)
        assert not torch.isnan(output['hidden_states']).any()


class TestMemoryBuffer:
    """Test cases for MemoryBuffer."""
    
    @pytest.fixture
    def memory(self):
        """Create memory buffer for testing."""
        return MemoryBuffer(memory_size=5, hidden_dim=32)
    
    def test_initialization(self, memory):
        """Test memory buffer initialization."""
        assert memory.memory_size == 5
        assert memory.hidden_dim == 32
        assert memory.current_size == 0
        assert len(memory.memory_bank) == 0
        assert memory.memory_embeddings is None
    
    def test_update_memory(self, memory):
        """Test updating memory with new states."""
        batch_size, hidden_dim = 3, 32
        states = torch.randn(batch_size, hidden_dim)
        
        memory.update(states)
        
        assert memory.current_size == batch_size
        assert len(memory.memory_bank) == batch_size
        assert memory.memory_embeddings is not None
        assert memory.memory_embeddings.shape == (batch_size, hidden_dim)
    
    def test_memory_overflow(self, memory):
        """Test memory buffer behavior when it overflows."""
        hidden_dim = 32
        
        # Add more memories than the buffer size
        for _ in range(3):
            states = torch.randn(2, hidden_dim)
            memory.update(states)
        
        # Should only keep the most recent 5 memories
        assert len(memory.memory_bank) == memory.memory_size
        assert memory.memory_embeddings.shape[0] == memory.memory_size
    
    def test_retrieve_memories_empty(self, memory):
        """Test retrieving memories from empty buffer."""
        query = torch.randn(2, 32)
        retrieved = memory.retrieve_relevant_memories(query)
        
        assert retrieved is None
    
    def test_retrieve_memories_with_data(self, memory):
        """Test retrieving memories with data in buffer."""
        # Add some memories
        states = torch.randn(3, 32)
        memory.update(states)
        
        # Query for memories
        query = torch.randn(2, 32)
        retrieved = memory.retrieve_relevant_memories(query, top_k=2)
        
        assert retrieved is not None
        assert retrieved.shape == (2, 32)  # batch_size x hidden_dim
    
    def test_retrieve_top_k_larger_than_memory(self, memory):
        """Test retrieving more memories than available."""
        # Add 2 memories
        states = torch.randn(2, 32)
        memory.update(states)
        
        # Request 5 memories (more than available)
        query = torch.randn(1, 32)
        retrieved = memory.retrieve_relevant_memories(query, top_k=5)
        
        assert retrieved is not None
        assert retrieved.shape == (1, 32)
    
    def test_clear_memory(self, memory):
        """Test clearing memory buffer."""
        # Add some memories
        states = torch.randn(3, 32)
        memory.update(states)
        
        assert memory.size() > 0
        
        # Clear memories
        memory.clear()
        
        assert memory.size() == 0
        assert len(memory.memory_bank) == 0
        assert memory.memory_embeddings is None
        assert memory.current_size == 0
    
    def test_memory_summary(self, memory):
        """Test getting memory summary statistics."""
        # Empty memory summary
        summary = memory.get_memory_summary()
        assert summary['size'] == 0
        assert summary['mean_norm'] == 0.0
        assert summary['std_norm'] == 0.0
        
        # Add some memories
        states = torch.randn(3, 32)
        memory.update(states)
        
        summary = memory.get_memory_summary()
        assert summary['size'] == 3
        assert summary['mean_norm'] > 0
        assert summary['std_norm'] >= 0
    
    def test_size_method(self, memory):
        """Test size method."""
        assert memory.size() == 0
        
        states = torch.randn(2, 32)
        memory.update(states)
        
        assert memory.size() == 2
    
    def test_device_consistency(self, memory):
        """Test that memory works with different devices."""
        # Test with CPU tensors
        states_cpu = torch.randn(2, 32)
        memory.update(states_cpu)
        
        query_cpu = torch.randn(1, 32)
        retrieved = memory.retrieve_relevant_memories(query_cpu)
        
        assert retrieved is not None
        assert retrieved.device == query_cpu.device
        
        # Test with GPU tensors if available
        if torch.cuda.is_available():
            query_gpu = query_cpu.cuda()
            retrieved_gpu = memory.retrieve_relevant_memories(query_gpu)
            
            assert retrieved_gpu is not None
            assert retrieved_gpu.device == query_gpu.device


class TestModelIntegration:
    """Integration tests for model components."""
    
    def test_attention_network_with_memory(self):
        """Test attention network working with memory buffer."""
        # Create components
        attention_net = AttentionNetwork(hidden_dim=32, num_heads=4, num_layers=2)
        memory_buffer = MemoryBuffer(memory_size=10, hidden_dim=32)
        
        # Generate some input
        batch_size, seq_len = 2, 8
        x = torch.randn(batch_size, seq_len, 32)
        
        # Process through attention network
        attn_output = attention_net(x)
        
        # Update memory with processed states
        memory_buffer.update(attn_output['hidden_states'].mean(dim=1))
        
        # Retrieve memories
        query = attn_output['hidden_states'][:, 0, :]  # Use first token as query
        retrieved = memory_buffer.retrieve_relevant_memories(query)
        
        assert retrieved is not None
        assert retrieved.shape == (batch_size, 32)
    
    def test_full_forward_pipeline(self):
        """Test the complete forward pipeline of model components."""
        hidden_dim = 64
        
        # Create all components
        attention = MultiHeadAttention(hidden_dim=hidden_dim, num_heads=8)
        feed_forward = FeedForward(hidden_dim=hidden_dim)
        attention_layer = AttentionLayer(hidden_dim=hidden_dim, num_heads=8)
        attention_network = AttentionNetwork(hidden_dim=hidden_dim, num_heads=8, num_layers=2)
        memory_buffer = MemoryBuffer(memory_size=20, hidden_dim=hidden_dim)
        
        # Input data
        batch_size, seq_len = 3, 12
        x = torch.randn(batch_size, seq_len, hidden_dim)
        
        # Pass through each component
        attn_out = attention(x, x, x)
        ff_out = feed_forward(attn_out['output'])
        layer_out = attention_layer(ff_out)
        network_out = attention_network(layer_out['output'])
        
        # Update memory
        memory_buffer.update(network_out['hidden_states'].mean(dim=1))
        
        # All outputs should have correct shapes
        assert attn_out['output'].shape == (batch_size, seq_len, hidden_dim)
        assert ff_out.shape == (batch_size, seq_len, hidden_dim)
        assert layer_out['output'].shape == (batch_size, seq_len, hidden_dim)
        assert network_out['hidden_states'].shape == (batch_size, seq_len, hidden_dim)
        assert memory_buffer.size() == batch_size
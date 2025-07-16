"""
Tests for the core Daydreamer functionality.
"""

import pytest
import torch
import numpy as np
from daydreamer.core import DefaultModeNetwork, ThoughtGenerator
from daydreamer.utils import generate_dummy_data, count_parameters


class TestDefaultModeNetwork:
    """Test cases for the DefaultModeNetwork class."""
    
    @pytest.fixture
    def small_model(self):
        """Create a small model for testing."""
        return DefaultModeNetwork(
            hidden_dim=64,
            num_layers=2,
            num_heads=4,
            memory_size=10,
            vocab_size=100,
            max_sequence_length=20,
        )
    
    def test_model_initialization(self, small_model):
        """Test that the model initializes correctly."""
        assert small_model.hidden_dim == 64
        assert small_model.num_layers == 2
        assert small_model.num_heads == 4
        assert small_model.memory_size == 10
        assert small_model.vocab_size == 100
        assert small_model.max_sequence_length == 20
    
    def test_model_forward_pass(self, small_model):
        """Test a forward pass through the model."""
        batch_size, seq_len = 2, 10
        input_ids = torch.randint(0, small_model.vocab_size, (batch_size, seq_len))
        
        outputs = small_model(input_ids)
        
        # Check output shapes
        assert 'logits' in outputs
        assert 'hidden_states' in outputs
        assert 'attention_weights' in outputs
        
        assert outputs['logits'].shape == (batch_size, seq_len, small_model.vocab_size)
        assert outputs['hidden_states'].shape == (batch_size, seq_len, small_model.hidden_dim)
        assert len(outputs['attention_weights']) == small_model.num_layers
    
    def test_model_with_attention_mask(self, small_model):
        """Test model with attention mask."""
        batch_size, seq_len = 2, 10
        input_ids = torch.randint(0, small_model.vocab_size, (batch_size, seq_len))
        attention_mask = torch.ones((batch_size, seq_len), dtype=torch.float)
        attention_mask[0, 5:] = 0  # Mask out second half of first sequence
        
        outputs = small_model(input_ids, attention_mask=attention_mask)
        
        # Should still produce valid outputs
        assert outputs['logits'].shape == (batch_size, seq_len, small_model.vocab_size)
        assert not torch.isnan(outputs['logits']).any()
    
    def test_model_without_memory(self, small_model):
        """Test model with memory disabled."""
        batch_size, seq_len = 2, 10
        input_ids = torch.randint(0, small_model.vocab_size, (batch_size, seq_len))
        
        outputs = small_model(input_ids, use_memory=False)
        
        assert outputs['logits'].shape == (batch_size, seq_len, small_model.vocab_size)
        assert not torch.isnan(outputs['logits']).any()
    
    def test_parameter_count(self, small_model):
        """Test that parameter counting works."""
        param_counts = count_parameters(small_model)
        
        assert 'total' in param_counts
        assert 'trainable' in param_counts
        assert 'non_trainable' in param_counts
        assert param_counts['total'] > 0
        assert param_counts['trainable'] > 0
    
    def test_positional_encoding_shape(self, small_model):
        """Test positional encoding has correct shape."""
        pe = small_model.positional_encoding
        expected_shape = (1, small_model.max_sequence_length, small_model.hidden_dim)
        assert pe.shape == expected_shape
    
    def test_memory_integration(self, small_model):
        """Test that memory buffer integrates properly."""
        batch_size, seq_len = 2, 10
        input_ids = torch.randint(0, small_model.vocab_size, (batch_size, seq_len))
        
        # First forward pass - should add to memory
        outputs1 = small_model(input_ids, use_memory=True)
        memory_size_after_first = small_model.memory_buffer.size()
        
        # Second forward pass - should use memory
        outputs2 = small_model(input_ids, use_memory=True)
        memory_size_after_second = small_model.memory_buffer.size()
        
        assert memory_size_after_first > 0
        assert memory_size_after_second >= memory_size_after_first


class TestThoughtGenerator:
    """Test cases for the ThoughtGenerator class."""
    
    @pytest.fixture
    def small_model(self):
        """Create a small model for testing."""
        return DefaultModeNetwork(
            hidden_dim=64,
            num_layers=2,
            num_heads=4,
            memory_size=10,
            vocab_size=100,
        )
    
    @pytest.fixture
    def generator(self, small_model):
        """Create a thought generator for testing."""
        return ThoughtGenerator(
            model=small_model,
            temperature=0.8,
            max_length=50,
        )
    
    def test_generator_initialization(self, generator, small_model):
        """Test that the generator initializes correctly."""
        assert generator.model is small_model
        assert generator.temperature == 0.8
        assert generator.max_length == 50
        assert generator.tokenizer is None
    
    def test_generate_thought_without_prompt(self, generator):
        """Test thought generation without a prompt."""
        thoughts = generator.generate_thought(num_thoughts=3)
        
        assert len(thoughts) == 3
        assert all(isinstance(thought, str) for thought in thoughts)
        assert all(len(thought) > 0 for thought in thoughts)
    
    def test_generate_thought_with_prompt(self, generator):
        """Test thought generation with a prompt."""
        prompt = "The mind wanders"
        thoughts = generator.generate_thought(prompt=prompt, num_thoughts=2)
        
        assert len(thoughts) == 2
        assert all(isinstance(thought, str) for thought in thoughts)
        assert all(prompt in thought for thought in thoughts)
    
    def test_self_prompt(self, generator):
        """Test self-prompting functionality."""
        thoughts = generator.self_prompt(num_iterations=3)
        
        assert len(thoughts) == 3
        assert all(isinstance(thought, str) for thought in thoughts)
        assert all(len(thought) > 0 for thought in thoughts)
    
    def test_train_step(self, generator):
        """Test a single training step."""
        batch_size, seq_len = 2, 10
        input_ids = torch.randint(0, generator.model.vocab_size, (batch_size, seq_len))
        target_ids = torch.randint(0, generator.model.vocab_size, (batch_size, seq_len))
        
        optimizer = torch.optim.Adam(generator.model.parameters(), lr=1e-4)
        
        loss = generator.train_step(input_ids, target_ids, optimizer)
        
        assert isinstance(loss, float)
        assert loss >= 0  # Loss should be non-negative
        assert not np.isnan(loss)


class TestModelIntegration:
    """Integration tests for the complete system."""
    
    def test_end_to_end_pipeline(self):
        """Test the complete pipeline from model creation to thought generation."""
        # Create model
        model = DefaultModeNetwork(
            hidden_dim=32,
            num_layers=2,
            num_heads=2,
            memory_size=5,
            vocab_size=50,
        )
        
        # Create generator
        generator = ThoughtGenerator(model, temperature=1.0)
        
        # Generate some dummy training data
        dummy_data = generate_dummy_data(
            batch_size=2,
            sequence_length=8,
            vocab_size=model.vocab_size,
        )
        
        # Run a forward pass
        outputs = model(dummy_data['input_ids'])
        assert 'logits' in outputs
        
        # Train for one step
        optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
        loss = generator.train_step(
            dummy_data['input_ids'],
            dummy_data['input_ids'],
            optimizer,
        )
        assert loss >= 0
        
        # Generate thoughts
        thoughts = generator.generate_thought(num_thoughts=2)
        assert len(thoughts) == 2
        
        # Test memory functionality
        memory_summary = model.memory_buffer.get_memory_summary()
        assert memory_summary['size'] >= 0
    
    def test_memory_persistence_across_generations(self):
        """Test that memory persists across multiple generations."""
        model = DefaultModeNetwork(
            hidden_dim=32,
            num_layers=1,
            num_heads=2,
            memory_size=10,
            vocab_size=50,
        )
        
        generator = ThoughtGenerator(model)
        
        # Generate thoughts multiple times to build up memory
        for _ in range(3):
            dummy_data = generate_dummy_data(
                batch_size=1,
                sequence_length=5,
                vocab_size=model.vocab_size,
            )
            model(dummy_data['input_ids'], use_memory=True)
        
        # Memory should have accumulated
        assert model.memory_buffer.size() > 0
        
        # Retrieve memories
        query = torch.randn(1, model.hidden_dim)
        memories = model.memory_buffer.retrieve_relevant_memories(query)
        assert memories is not None
        assert memories.shape == (1, model.hidden_dim)
    
    def test_model_evaluation_mode(self):
        """Test that model can be switched to evaluation mode."""
        model = DefaultModeNetwork(
            hidden_dim=32,
            num_layers=1,
            num_heads=2,
            memory_size=5,
            vocab_size=50,
        )
        
        # Test training mode
        model.train()
        assert model.training
        
        # Test evaluation mode
        model.eval()
        assert not model.training
        
        # Forward pass in eval mode should work
        dummy_data = generate_dummy_data(
            batch_size=1,
            sequence_length=5,
            vocab_size=model.vocab_size,
        )
        
        with torch.no_grad():
            outputs = model(dummy_data['input_ids'])
            assert 'logits' in outputs
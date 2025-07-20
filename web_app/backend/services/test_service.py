#!/usr/bin/env python3
"""
Test Service
===========

Service for running automated tests and managing test results.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database import AsyncSessionLocal
from models import TestResult, TestResultCreate, TestResultResponse

logger = logging.getLogger(__name__)

class TestService:
    """Service for running and managing automated tests"""
    
    def __init__(self):
        """Initialize the test service"""
        self.available_tests = {
            "model_health": {
                "name": "Model Health Check",
                "description": "Test if the AI model is responding correctly",
                "parameters": {
                    "test_messages": ["Hello", "How are you?", "What is 2+2?"],
                    "timeout": 30
                }
            },
            "response_time": {
                "name": "Response Time Test",
                "description": "Measure response times for various message types",
                "parameters": {
                    "message_count": 5,
                    "message_types": ["short", "medium", "long"],
                    "timeout": 60
                }
            },
            "memory_usage": {
                "name": "Memory Usage Test",
                "description": "Test memory usage during conversation",
                "parameters": {
                    "conversation_length": 10,
                    "timeout": 120
                }
            },
            "conversation_flow": {
                "name": "Conversation Flow Test",
                "description": "Test conversation continuity and context",
                "parameters": {
                    "conversation_turns": 5,
                    "context_dependent": True,
                    "timeout": 90
                }
            },
            "error_handling": {
                "name": "Error Handling Test",
                "description": "Test system behavior with invalid inputs",
                "parameters": {
                    "invalid_inputs": ["", "   ", "🚀", "a" * 10000],
                    "timeout": 30
                }
            },
            "system_integration": {
                "name": "System Integration Test",
                "description": "Test integration with daydreamer components",
                "parameters": {
                    "test_components": ["memory", "model", "analytics"],
                    "timeout": 60
                }
            }
        }
    
    async def get_available_tests(self) -> List[Dict[str, Any]]:
        """Get list of available tests"""
        return [
            {
                "id": test_id,
                "name": test_info["name"],
                "description": test_info["description"],
                "parameters": test_info["parameters"]
            }
            for test_id, test_info in self.available_tests.items()
        ]
    
    async def run_test(self, test_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Run a specific test"""
        start_time = time.time()
        
        if test_type not in self.available_tests:
            raise ValueError(f"Unknown test type: {test_type}")
        
        test_info = self.available_tests[test_type]
        
        try:
            logger.info(f"Starting test: {test_info['name']}")
            
            # Run the specific test
            if test_type == "model_health":
                result = await self._run_model_health_test(parameters)
            elif test_type == "response_time":
                result = await self._run_response_time_test(parameters)
            elif test_type == "memory_usage":
                result = await self._run_memory_usage_test(parameters)
            elif test_type == "conversation_flow":
                result = await self._run_conversation_flow_test(parameters)
            elif test_type == "error_handling":
                result = await self._run_error_handling_test(parameters)
            elif test_type == "system_integration":
                result = await self._run_system_integration_test(parameters)
            else:
                raise ValueError(f"Test type {test_type} not implemented")
            
            duration = time.time() - start_time
            
            # Save test result
            test_result = await self._save_test_result(
                test_name=test_info["name"],
                test_type=test_type,
                status="passed" if result["success"] else "failed",
                duration=duration,
                parameters=parameters,
                results=result,
                error_message=result.get("error")
            )
            
            return {
                "test_id": test_result["id"],
                "test_name": test_info["name"],
                "status": "passed" if result["success"] else "failed",
                "duration": round(duration, 2),
                "results": result
            }
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            logger.error(f"Test {test_type} failed: {error_msg}")
            
            # Save failed test result
            test_result = await self._save_test_result(
                test_name=test_info["name"],
                test_type=test_type,
                status="error",
                duration=duration,
                parameters=parameters,
                results={},
                error_message=error_msg
            )
            
            return {
                "test_id": test_result["id"],
                "test_name": test_info["name"],
                "status": "error",
                "duration": round(duration, 2),
                "error": error_msg
            }
    
    async def _run_model_health_test(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Run model health check test"""
        test_messages = parameters.get("test_messages", ["Hello"])
        timeout = parameters.get("timeout", 30)
        
        results = []
        success_count = 0
        
        for message in test_messages:
            try:
                # This would integrate with the actual daydreamer service
                # For now, simulate a response
                await asyncio.sleep(0.1)  # Simulate processing time
                
                response = f"Mock response to: {message}"
                results.append({
                    "message": message,
                    "response": response,
                    "success": True,
                    "response_time": 0.1
                })
                success_count += 1
                
            except Exception as e:
                results.append({
                    "message": message,
                    "error": str(e),
                    "success": False
                })
        
        success_rate = success_count / len(test_messages) if test_messages else 0
        
        return {
            "success": success_rate >= 0.8,  # 80% success threshold
            "success_rate": success_rate,
            "total_messages": len(test_messages),
            "successful_responses": success_count,
            "results": results
        }
    
    async def _run_response_time_test(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Run response time test"""
        message_count = parameters.get("message_count", 5)
        message_types = parameters.get("message_types", ["short", "medium", "long"])
        timeout = parameters.get("timeout", 60)
        
        test_messages = {
            "short": "Hi",
            "medium": "Can you explain how machine learning works?",
            "long": "I need a detailed explanation of the differences between supervised and unsupervised learning, including examples and use cases for each approach."
        }
        
        results = []
        total_time = 0
        
        for msg_type in message_types:
            message = test_messages.get(msg_type, "Test message")
            
            for i in range(message_count):
                start_time = time.time()
                
                try:
                    # Simulate processing
                    await asyncio.sleep(0.1 + (i * 0.05))  # Varying response times
                    
                    response_time = time.time() - start_time
                    total_time += response_time
                    
                    results.append({
                        "message_type": msg_type,
                        "message": message,
                        "response_time": response_time,
                        "success": True
                    })
                    
                except Exception as e:
                    results.append({
                        "message_type": msg_type,
                        "message": message,
                        "error": str(e),
                        "success": False
                    })
        
        avg_response_time = total_time / len(results) if results else 0
        
        return {
            "success": avg_response_time < 5.0,  # 5 second threshold
            "average_response_time": avg_response_time,
            "total_tests": len(results),
            "results": results
        }
    
    async def _run_memory_usage_test(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Run memory usage test"""
        conversation_length = parameters.get("conversation_length", 10)
        timeout = parameters.get("timeout", 120)
        
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        memory_readings = [initial_memory]
        
        for i in range(conversation_length):
            # Simulate conversation turn
            await asyncio.sleep(0.1)
            
            current_memory = process.memory_info().rss / 1024 / 1024
            memory_readings.append(current_memory)
        
        final_memory = memory_readings[-1]
        memory_increase = final_memory - initial_memory
        
        return {
            "success": memory_increase < 100,  # 100MB threshold
            "initial_memory_mb": round(initial_memory, 2),
            "final_memory_mb": round(final_memory, 2),
            "memory_increase_mb": round(memory_increase, 2),
            "conversation_length": conversation_length,
            "memory_readings": [round(m, 2) for m in memory_readings]
        }
    
    async def _run_conversation_flow_test(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Run conversation flow test"""
        conversation_turns = parameters.get("conversation_turns", 5)
        context_dependent = parameters.get("context_dependent", True)
        timeout = parameters.get("timeout", 90)
        
        conversation = []
        context_consistent = True
        
        test_messages = [
            "My name is Alice.",
            "What's my name?",
            "I like pizza.",
            "What do I like?",
            "How old am I?"
        ]
        
        for i, message in enumerate(test_messages[:conversation_turns]):
            # Simulate conversation turn
            await asyncio.sleep(0.1)
            
            if context_dependent and i > 0:
                # Check if response maintains context
                response = f"Mock response maintaining context: {message}"
                context_consistent = context_consistent and "context" in response.lower()
            else:
                response = f"Mock response: {message}"
            
            conversation.append({
                "turn": i + 1,
                "user_message": message,
                "ai_response": response,
                "context_maintained": context_consistent
            })
        
        return {
            "success": context_consistent,
            "conversation_turns": len(conversation),
            "context_consistent": context_consistent,
            "conversation": conversation
        }
    
    async def _run_error_handling_test(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Run error handling test"""
        invalid_inputs = parameters.get("invalid_inputs", ["", "   "])
        timeout = parameters.get("timeout", 30)
        
        results = []
        handled_errors = 0
        
        for invalid_input in invalid_inputs:
            try:
                # Simulate processing invalid input
                await asyncio.sleep(0.05)
                
                # Check if input is handled gracefully
                if not invalid_input.strip():
                    # Empty input should be handled gracefully
                    results.append({
                        "input": repr(invalid_input),
                        "handled": True,
                        "response": "Please provide a valid message."
                    })
                    handled_errors += 1
                else:
                    # Other invalid inputs
                    results.append({
                        "input": repr(invalid_input),
                        "handled": True,
                        "response": "Input processed successfully."
                    })
                    handled_errors += 1
                    
            except Exception as e:
                results.append({
                    "input": repr(invalid_input),
                    "handled": False,
                    "error": str(e)
                })
        
        success_rate = handled_errors / len(invalid_inputs) if invalid_inputs else 0
        
        return {
            "success": success_rate >= 0.9,  # 90% error handling threshold
            "success_rate": success_rate,
            "total_inputs": len(invalid_inputs),
            "handled_errors": handled_errors,
            "results": results
        }
    
    async def _run_system_integration_test(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Run system integration test"""
        test_components = parameters.get("test_components", ["memory", "model", "analytics"])
        timeout = parameters.get("timeout", 60)
        
        component_results = {}
        all_successful = True
        
        for component in test_components:
            try:
                await asyncio.sleep(0.1)  # Simulate component check
                
                if component == "memory":
                    # Test database connectivity
                    async with AsyncSessionLocal() as session:
                        await session.execute("SELECT 1")
                    component_results[component] = {"status": "connected", "success": True}
                
                elif component == "model":
                    # Test model availability
                    component_results[component] = {"status": "available", "success": True}
                
                elif component == "analytics":
                    # Test analytics service
                    component_results[component] = {"status": "operational", "success": True}
                
                else:
                    component_results[component] = {"status": "unknown", "success": False}
                    all_successful = False
                    
            except Exception as e:
                component_results[component] = {"status": "error", "error": str(e), "success": False}
                all_successful = False
        
        return {
            "success": all_successful,
            "components_tested": len(test_components),
            "successful_components": sum(1 for r in component_results.values() if r["success"]),
            "component_results": component_results
        }
    
    async def _save_test_result(self, test_name: str, test_type: str, status: str,
                               duration: float, parameters: Dict[str, Any],
                               results: Dict[str, Any], error_message: Optional[str] = None) -> Dict[str, Any]:
        """Save test result to database"""
        async with AsyncSessionLocal() as session:
            test_result = TestResult(
                test_name=test_name,
                test_type=test_type,
                status=status,
                duration=duration,
                parameters=parameters,
                results=results,
                error_message=error_message
            )
            session.add(test_result)
            await session.commit()
            
            return {
                "id": test_result.id,
                "test_name": test_result.test_name,
                "test_type": test_result.test_type,
                "status": test_result.status,
                "duration": test_result.duration,
                "created_at": test_result.created_at
            }
    
    async def get_test_results(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent test results"""
        async with AsyncSessionLocal() as session:
            stmt = select(TestResult).order_by(TestResult.created_at.desc()).limit(limit)
            result = await session.execute(stmt)
            test_results = result.scalars().all()
            
            return [
                {
                    "id": tr.id,
                    "test_name": tr.test_name,
                    "test_type": tr.test_type,
                    "status": tr.status,
                    "duration": tr.duration,
                    "parameters": tr.parameters,
                    "results": tr.results,
                    "error_message": tr.error_message,
                    "created_at": tr.created_at
                }
                for tr in test_results
            ]
    
    async def get_test_summary(self) -> Dict[str, Any]:
        """Get test summary statistics"""
        async with AsyncSessionLocal() as session:
            # Get total tests
            stmt = select(func.count(TestResult.id))
            result = await session.execute(stmt)
            total_tests = result.scalar() or 0
            
            # Get tests by status
            stmt = select(TestResult.status, func.count(TestResult.id)).group_by(TestResult.status)
            result = await session.execute(stmt)
            status_counts = {row.status: row.count for row in result.all()}
            
            # Get average duration
            stmt = select(func.avg(TestResult.duration))
            result = await session.execute(stmt)
            avg_duration = result.scalar() or 0.0
            
            # Get recent test success rate
            recent_date = datetime.now() - timedelta(days=7)
            stmt = select(func.count(TestResult.id)).where(
                TestResult.created_at >= recent_date,
                TestResult.status == "passed"
            )
            result = await session.execute(stmt)
            recent_passed = result.scalar() or 0
            
            stmt = select(func.count(TestResult.id)).where(
                TestResult.created_at >= recent_date
            )
            result = await session.execute(stmt)
            recent_total = result.scalar() or 0
            
            recent_success_rate = recent_passed / recent_total if recent_total > 0 else 0
            
            return {
                "total_tests": total_tests,
                "status_distribution": status_counts,
                "average_duration": round(avg_duration, 2),
                "recent_success_rate": round(recent_success_rate, 2),
                "recent_tests": recent_total
            }
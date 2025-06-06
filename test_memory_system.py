#!/usr/bin/env python3
"""
Test script to demonstrate the opinion-weighted memory system and belief drift.
This runs a shorter debate with lower thresholds to showcase the memory system.
"""

import os
from agents.agent import PhilosopherAgent
from orchestrator.orchestrator import DebateOrchestrator
from prompts.system_prompts import get_prompt

def setup_test_llm_config():
    """Set up LLM configuration for testing."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    return {
        "config_list": [{
            "model": "gpt-4",
            "api_key": api_key,
        }],
        "temperature": 0.8,  # Higher temperature for more varied responses
        "max_tokens": 600,
        "timeout": 60,
    }

def create_test_philosophers(llm_config):
    """Create a smaller set of philosophers for testing with lower belief drift threshold."""
    philosophers = []
    
    # Kant with lower threshold for belief drift
    kant = PhilosopherAgent(
        name="Kant",
        philosophy="deontology",
        system_message=get_prompt("kant"),
        goals=["Defend universal moral principles", "Emphasize duty over consequences"],
        llm_config=llm_config
    )
    kant.belief_drift_threshold = 0.5  # Lower threshold for faster demonstration
    philosophers.append(kant)
    
    # Mill
    mill = PhilosopherAgent(
        name="Mill",
        philosophy="consequentialism",
        system_message=get_prompt("mill"),
        goals=["Maximize overall happiness", "Focus on practical outcomes"],
        llm_config=llm_config
    )
    mill.belief_drift_threshold = 0.5
    philosophers.append(mill)
    
    # Confucian
    confucian = PhilosopherAgent(
        name="Confucian_Sage",
        philosophy="confucian",
        system_message=get_prompt("confucian"),
        goals=["Promote social harmony", "Emphasize virtue and proper relationships"],
        llm_config=llm_config
    )
    confucian.belief_drift_threshold = 0.5
    philosophers.append(confucian)
    
    return philosophers

def run_test_debate():
    """Run a test debate to demonstrate the memory system."""
    print("🧪 TESTING OPINION-WEIGHTED MEMORY SYSTEM")
    print("=" * 60)
    
    llm_config = setup_test_llm_config()
    philosophers = create_test_philosophers(llm_config)
    
    orchestrator = DebateOrchestrator(llm_config=llm_config)
    orchestrator.max_rounds = 6  # Shorter debate
    orchestrator.speakers_per_round = 2
    
    for philosopher in philosophers:
        orchestrator.add_agent(philosopher)
    
    # Topic that might encourage cross-philosophical agreement
    topic = "How should we balance individual rights with collective welfare during a crisis?"
    
    opening = orchestrator.start_debate(topic)
    print(f"🎤 {orchestrator.name}: {opening}")
    print("-" * 60)
    
    round_count = 0
    while orchestrator.should_continue_debate() and round_count < orchestrator.max_rounds:
        print(f"\n🔄 Round {round_count + 1}")
        result = orchestrator.run_debate_round()
        
        if 'responses' in result:
            print(f"Speakers: {', '.join(result['speakers'])}")
            
            for agent, response in result['responses']:
                print(f"\n💬 {response}")
            
            # Show detailed memory state
            print("\n📊 Memory State:")
            for agent in philosophers:
                if agent.memory:
                    print(f"\n{agent.name} ({agent.philosophy}):")
                    for i, mem in enumerate(agent.memory[:3]):  # Show top 3 memories
                        print(f"  Memory {i+1}: Opinion={mem['opinion_weight']:.2f}, "
                              f"Importance={mem['importance']:.2f}, "
                              f"From={mem.get('speaker_philosophy', 'unknown')}")
                        print(f"    Content: {mem['content'][:100]}...")
        
        round_count += 1
    
    # Final summary
    summary = orchestrator.end_debate()
    
    print("\n" + "=" * 60)
    print("🏁 TEST DEBATE CONCLUDED")
    print("\n🧠 FINAL MEMORY ANALYSIS:")
    
    for agent in philosophers:
        print(f"\n{agent.name}:")
        print(f"  Total memories: {len(agent.memory)}")
        if agent.memory:
            avg_opinion = sum(m['opinion_weight'] for m in agent.memory) / len(agent.memory)
            print(f"  Average opinion weight: {avg_opinion:.3f}")
            
            # Check for belief evolution
            if hasattr(agent, 'system_message') and agent.system_message != agent.initial_system_message:
                print(f"  ✨ BELIEF DRIFT DETECTED! System prompt has been modified.")
    
    print("\n🤔 REFLECTIONS:")
    for agent_name, reflection in summary['reflections'].items():
        print(f"\n{agent_name}: {reflection[:300]}...")

if __name__ == "__main__":
    run_test_debate() 
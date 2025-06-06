#!/usr/bin/env python3
"""
Multi-Agent Philosophical Debate System

This script demonstrates how to set up and run debates between AI agents
representing different philosophical worldviews using Microsoft Autogen.
"""

import os
from agents.agent import PhilosopherAgent
from orchestrator.orchestrator import DebateOrchestrator
from prompts.system_prompts import get_prompt
from dotenv import load_dotenv

load_dotenv()
print(os.getenv("OPENAI_API_KEY"))

def setup_llm_config():
    """
    Set up LLM configuration for Autogen.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    return {
        "config_list": [
            {
                "model": "gpt-4",  # or your preferred model
                "api_key": api_key,
            }
        ],
        "temperature": 0.7,
        "max_tokens": 800,  # Increased for more detailed responses
        "timeout": 60,
    }

def create_philosophers(llm_config):
    """Create the 5 specified philosopher agents with different worldviews."""
    philosophers = []
    
    # 1. Kant - Deontological Ethics
    kant = PhilosopherAgent(
        name="Kant",
        philosophy="deontology",
        system_message=get_prompt("kant"),
        goals=["Defend universal moral principles", "Emphasize duty over consequences"],
        llm_config=llm_config
    )
    philosophers.append(kant)
    
    # 2. Mill - Utilitarian Consequentialism
    mill = PhilosopherAgent(
        name="Mill",
        philosophy="consequentialism",
        system_message=get_prompt("mill"),
        goals=["Maximize overall happiness", "Focus on practical outcomes"],
        llm_config=llm_config
    )
    philosophers.append(mill)
    
    # 3. Confucian Ethics
    confucian = PhilosopherAgent(
        name="Confucian_Sage",
        philosophy="confucian",
        system_message=get_prompt("confucian"),
        goals=["Promote social harmony", "Emphasize virtue and proper relationships"],
        llm_config=llm_config
    )
    philosophers.append(confucian)
    
    # 4. Existentialism (Sartre/Nietzsche fusion)
    existentialist = PhilosopherAgent(
        name="Existentialist",
        philosophy="existentialist",
        system_message=get_prompt("existentialist"),
        goals=["Defend radical freedom", "Challenge imposed moral systems"],
        llm_config=llm_config
    )
    philosophers.append(existentialist)
    
    # 5. Śāntideva - Mahayana Buddhist Ethics
    santideva = PhilosopherAgent(
        name="Santideva",
        philosophy="buddhist",
        system_message=get_prompt("santideva"),
        goals=["Reduce suffering for all beings", "Promote compassion and non-attachment"],
        llm_config=llm_config
    )
    philosophers.append(santideva)
    
    return philosophers

def run_debate(topic: str, max_rounds: int = 10):
    """
    Run a philosophical debate on the given topic.
    
    Args:
        topic: The ethical or philosophical question to debate
        max_rounds: Maximum number of debate rounds
    """
    print(f"🎭 Starting Multi-Agent Philosophical Debate")
    print(f"📝 Topic: {topic}")
    print("=" * 60)
    
    try:
        # Set up LLM configuration
        llm_config = setup_llm_config()
        print("✅ LLM configuration validated")
        
        # Create philosopher agents
        philosophers = create_philosophers(llm_config)
        print(f"✅ Created {len(philosophers)} philosopher agents")
        
        # Create orchestrator
        orchestrator = DebateOrchestrator(llm_config=llm_config)
        orchestrator.max_rounds = max_rounds
        orchestrator.speakers_per_round = 2  # Allow 2 speakers per round
        
        # Add philosophers to the debate
        for philosopher in philosophers:
            orchestrator.add_agent(philosopher)
        
        # Start the debate
        opening = orchestrator.start_debate(topic)
        print(f"🎤 {orchestrator.name}: {opening}")
        print("-" * 60)
        
        # Run debate rounds
        round_count = 0
        while orchestrator.should_continue_debate() and round_count < max_rounds:
            print(f"\n🔄 Processing round {round_count + 1}...")
            result = orchestrator.run_debate_round()
            
            if 'responses' in result:
                print(f"\n📍 ROUND {result['round']}:")
                print(f"Speakers selected: {', '.join(result['speakers'])}")
                
                # Show intent scores for transparency
                if 'intent_scores' in result:
                    print("Intent to speak scores:")
                    for agent, score in result['intent_scores']:
                        print(f"  {agent.name}: {score:.3f}")
                
                print("\nResponses:")
                for agent, response in result['responses']:
                    print(f"💬 {response}")
                    print("-" * 40)
                
                # Display memory statistics for active speakers
                print("\n📊 Memory Statistics:")
                for agent_name in result['speakers']:
                    agent = next(a for a in philosophers if a.name == agent_name)
                    if agent.memory:
                        positive_memories = sum(1 for m in agent.memory if m['opinion_weight'] > 0.3)
                        negative_memories = sum(1 for m in agent.memory if m['opinion_weight'] < -0.3)
                        print(f"  {agent.name}: {len(agent.memory)} memories "
                              f"(+{positive_memories}/-{negative_memories})")
            
            if not result.get('continue', True):
                break
                
            round_count += 1
        
        # End debate and get summary
        print("\n🔄 Generating final reflections...")
        summary = orchestrator.end_debate()
        
        print("\n" + "=" * 60)
        print("🏁 DEBATE CONCLUDED")
        print(f"📊 Total rounds: {summary['rounds']}")
        print(f"💬 Total messages: {summary['total_messages']}")
        
        print("\n🤔 AGENT REFLECTIONS:")
        for agent_name, reflection in summary['reflections'].items():
            print(f"\n{agent_name}: {reflection}")
        
        return summary
        
    except Exception as e:
        print(f"❌ Error during debate: {e}")
        print("Please check your API key and internet connection.")
        raise

def main():
    """Main function to run example debates."""
    
    # Example debate topics
    topics = [
        "Is it ever morally permissible to lie?",
        "Should we prioritize individual freedom or collective welfare?",
        "What is the relationship between happiness and virtue?",
        "Is moral truth objective or subjective?",
        "How should we respond to moral disagreement?"
    ]
    
    print("🌟 Welcome to the Multi-Agent Philosophical Debate System!")
    print("\nParticipating Philosophers:")
    print("1. Immanuel Kant (Deontological Ethics)")
    print("2. John Stuart Mill (Utilitarian Consequentialism)")
    print("3. Confucian Sage (Confucian Ethics)")
    print("4. Existentialist (Sartre/Nietzsche fusion)")
    print("5. Śāntideva (Mahayana Buddhist Ethics)")
    
    print("\nAvailable debate topics:")
    for i, topic in enumerate(topics, 1):
        print(f"{i}. {topic}")
    
    try:
        choice = input("\nSelect a topic (1-5) or enter your own: ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(topics):
            selected_topic = topics[int(choice) - 1]
        else:
            selected_topic = choice
        
        if not selected_topic:
            selected_topic = topics[0]  # Default topic
        
        # Run the debate
        summary = run_debate(selected_topic, max_rounds=8)
        
        # Optionally save results
        save_choice = input("\nSave debate transcript? (y/n): ").strip().lower()
        if save_choice == 'y':
            filename = f"debate_{selected_topic.replace(' ', '_').replace('?', '')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Debate Topic: {selected_topic}\n")
                f.write("=" * 60 + "\n\n")
                for msg in summary['chat_history']:
                    f.write(f"Round {msg.get('round', 0)} - {msg['speaker']}: {msg['content']}\n\n")
                f.write("\nReflections:\n")
                for agent, reflection in summary['reflections'].items():
                    f.write(f"{agent}: {reflection}\n\n")
            print(f"💾 Debate saved to {filename}")
    
    except KeyboardInterrupt:
        print("\n👋 Debate interrupted. Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure you have set up your LLM configuration properly.")

if __name__ == "__main__":
    main() 
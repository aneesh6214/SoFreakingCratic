# orchestrator.py

from autogen import ConversableAgent
import random
from typing import List, Dict, Any, Tuple
from agents.agent import PhilosopherAgent

class DebateOrchestrator(ConversableAgent):
    def __init__(self, name="Moderator", llm_config=None):
        system_message = """
        You are a philosophical debate moderator. Your role is to:
        1. Introduce topics and maintain focus
        2. Ensure fair participation among all philosophical perspectives
        3. Ask clarifying questions when needed
        4. Summarize key points and identify areas of agreement/disagreement
        5. Keep the debate constructive and intellectually rigorous
        """
        
        super().__init__(
            name=name,
            system_message=system_message,
            llm_config=llm_config
        )
        
        self.agents: List[PhilosopherAgent] = []
        self.chat_history = []
        self.current_topic = None
        self.round_count = 0
        self.max_rounds = 10
        self.debate_active = False
        self.speakers_per_round = 2  # Number of agents that speak per round
        
    def add_agent(self, agent: PhilosopherAgent):
        """Add a philosopher agent to the debate."""
        self.agents.append(agent)
        
    def start_debate(self, topic: str):
        """Initialize a new debate on the given topic."""
        self.current_topic = topic
        self.round_count = 0
        self.debate_active = True
        self.chat_history = []
        
        # Reset all agent cooldowns
        for agent in self.agents:
            agent.cooldown = 0
            
        opening_message = f"""
        Welcome to our philosophical debate on: "{topic}"
        
        We have {len(self.agents)} distinguished philosophers joining us today:
        {', '.join([f"{agent.name} ({agent.philosophy})" for agent in self.agents])}
        
        Let us begin with opening statements.
        """
        
        self.chat_history.append({
            'speaker': self.name,
            'content': opening_message,
            'round': self.round_count
        })
        
        return opening_message
    
    def collect_intent_to_speak(self) -> List[Tuple[PhilosopherAgent, float]]:
        """
        Collect intent to speak from all agents based on their reactivity scores.
        Returns list of (agent, reactivity_score) tuples.
        """
        intent_scores = []
        
        for agent in self.agents:
            # All agents observe the full message history
            reactivity_score = agent.compute_reactivity(self.chat_history)
            
            # Only include agents not on cooldown
            if agent.cooldown == 0:
                intent_scores.append((agent, reactivity_score))
            else:
                # Reduce cooldown for agents not speaking
                agent.reduce_cooldown()
        
        return intent_scores
    
    def select_speakers(self, intent_scores: List[Tuple[PhilosopherAgent, float]]) -> List[PhilosopherAgent]:
        """
        Pick top N agents to speak based on their intent scores.
        """
        if not intent_scores:
            return []
        
        # Sort by reactivity score (highest first)
        intent_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Select top N speakers (but not more than available agents)
        num_speakers = min(self.speakers_per_round, len(intent_scores))
        
        # Add some randomness among highly reactive agents
        if len(intent_scores) >= num_speakers:
            # Take top candidates with some weighted randomness
            top_candidates = intent_scores[:min(num_speakers * 2, len(intent_scores))]
            weights = [score for _, score in top_candidates]
            
            # If all weights are 0, select randomly
            if sum(weights) == 0:
                selected = random.sample([agent for agent, _ in top_candidates], num_speakers)
            else:
                # Weighted selection favoring higher reactivity
                selected = []
                remaining_candidates = top_candidates.copy()
                
                for _ in range(num_speakers):
                    if not remaining_candidates:
                        break
                    
                    agents = [agent for agent, _ in remaining_candidates]
                    weights = [score + 0.1 for _, score in remaining_candidates]  # Add small base weight
                    
                    chosen_agent = random.choices(agents, weights=weights)[0]
                    selected.append(chosen_agent)
                    
                    # Remove chosen agent from remaining candidates
                    remaining_candidates = [(a, s) for a, s in remaining_candidates if a != chosen_agent]
        else:
            selected = [agent for agent, _ in intent_scores]
        
        return selected
    
    def generate_agent_responses(self, speakers: List[PhilosopherAgent]) -> List[Tuple[PhilosopherAgent, str]]:
        """
        Generate responses from selected speakers using actual LLM calls.
        """
        responses = []
        
        for agent in speakers:
            # Store chat history for agent to access
            agent.chat_history = self.chat_history
            
            # Prepare the conversation context for the agent
            # Convert chat history to the format expected by Autogen
            messages = []
            for msg in self.chat_history[-5:]:  # Use last 5 messages for context
                messages.append({
                    "role": "user" if msg['speaker'] != agent.name else "assistant",
                    "content": f"{msg['speaker']}: {msg['content']}"
                })
            
            # Add the current topic and request for response
            base_prompt = f"""
            Current debate topic: {self.current_topic}
            
            Recent conversation:
            {chr(10).join([f"{msg['speaker']}: {msg['content']}" for msg in self.chat_history[-3:]])}
            
            As {agent.name}, representing {agent.philosophy}, please provide your philosophical perspective on this discussion. 
            Stay true to your philosophical framework and engage directly with the points raised.
            """
            
            # Enhance prompt with memory influence
            prompt = agent.generate_memory_influenced_prompt(base_prompt)
            
            try:
                # Use Autogen's generate_reply method
                response = agent.generate_reply(
                    messages=[{"role": "user", "content": prompt}],
                    sender=self  # The orchestrator is the sender
                )
                
                # Clean up the response if needed
                if isinstance(response, dict) and 'content' in response:
                    response_text = response['content']
                elif isinstance(response, str):
                    response_text = response
                else:
                    response_text = str(response)
                
                # Ensure the response is attributed to the agent
                if not response_text.startswith(agent.name):
                    response_text = f"{agent.name}: {response_text}"
                
                responses.append((agent, response_text))
                
            except Exception as e:
                # Fallback to philosophical stance if LLM call fails
                print(f"Warning: LLM call failed for {agent.name}: {e}")
                fallback_response = f"{agent.name}: " + agent.get_philosophical_stance(self.current_topic)
                responses.append((agent, fallback_response))
            
        return responses
    
    def update_memory_and_reflection(self, responses: List[Tuple[PhilosopherAgent, str]]):
        """
        Update memory for all agents and handle optional reflection.
        """
        # Add responses to chat history
        for agent, response in responses:
            self.chat_history.append({
                'speaker': agent.name,
                'content': response,
                'round': self.round_count,
                'philosophy': agent.philosophy
            })
            
            # Set cooldown for speaking agent
            agent.set_cooldown(rounds=2)
        
        # Update memory for all agents based on what was said
        for speaking_agent, response in responses:
            for agent in self.agents:
                if agent != speaking_agent:
                    importance = self._calculate_message_importance(response, agent)
                    # Pass the speaker's philosophy for opinion weight calculation
                    agent.update_memory(response, importance, speaker_philosophy=speaking_agent.philosophy)
    
    def _calculate_message_importance(self, message: str, agent: PhilosopherAgent) -> float:
        """Calculate how important a message is for a specific agent."""
        importance = 0.5  # Base importance
        
        # Higher importance if message mentions agent's philosophy
        if agent.philosophy.lower() in message.lower():
            importance += 0.3
            
        # Higher importance for questions
        if '?' in message:
            importance += 0.2
            
        # Higher importance for strong disagreement
        disagreement_words = ["wrong", "disagree", "incorrect", "false", "reject"]
        for word in disagreement_words:
            if word in message.lower():
                importance += 0.2
                break
        
        return min(importance, 1.0)
    
    def should_continue_debate(self) -> bool:
        """Determine if the debate should continue."""
        if self.round_count >= self.max_rounds:
            return False
            
        if not self.debate_active:
            return False
            
        # Check if any agents want to speak (have positive reactivity)
        intent_scores = self.collect_intent_to_speak()
        engaged_agents = sum(1 for _, score in intent_scores if score > 0.1)
        
        return engaged_agents > 0
    
    def generate_moderator_intervention(self) -> str:
        """Generate moderator comments to guide the debate."""
        interventions = [
            f"Let's hear from a different philosophical perspective. How might {random.choice(self.agents).philosophy} approach this?",
            "Can someone provide a concrete example to illustrate this point?",
            "I notice we have some disagreement here. Can we identify the core issue?",
            "How might we find common ground between these positions?",
            "What are the practical implications of this philosophical stance?",
            f"We're {self.round_count} rounds into our discussion of '{self.current_topic}'. What new insights have emerged?"
        ]
        
        return random.choice(interventions)
    
    def end_debate(self) -> Dict[str, Any]:
        """End the debate and generate summary."""
        self.debate_active = False
        
        summary = {
            'topic': self.current_topic,
            'rounds': self.round_count,
            'participants': [{'name': agent.name, 'philosophy': agent.philosophy} for agent in self.agents],
            'total_messages': len(self.chat_history),
            'chat_history': self.chat_history
        }
        
        # Generate reflections from all agents
        transcript = '\n'.join([f"{msg['speaker']}: {msg['content']}" for msg in self.chat_history])
        reflections = {}
        for agent in self.agents:
            reflections[agent.name] = agent.reflect(transcript)
        
        summary['reflections'] = reflections
        
        return summary
    
    def run_debate_round(self) -> Dict[str, Any]:
        """
        Run a single round of the debate following the specified architecture:
        1. Agents observe full message history
        2. Each computes reactivity score  
        3. Orchestrator collects "intent to speak" from all agents
        4. Picks top N agents to speak
        5. Agents generate responses
        6. Memory + optional reflection updated
        """
        if not self.should_continue_debate():
            return self.end_debate()
        
        self.round_count += 1
        
        # Step 1 & 2: Agents observe full history and compute reactivity (done in collect_intent_to_speak)
        # Step 3: Collect intent to speak from all agents
        intent_scores = self.collect_intent_to_speak()
        
        if not intent_scores:
            # No one can speak, end debate
            return self.end_debate()
        
        # Step 4: Pick top N agents to speak
        selected_speakers = self.select_speakers(intent_scores)
        
        if not selected_speakers:
            return self.end_debate()
        
        # Step 5: Agents generate responses
        responses = self.generate_agent_responses(selected_speakers)
        
        # Step 6: Update memory and optional reflection
        self.update_memory_and_reflection(responses)
        
        # Occasionally add moderator intervention
        if random.random() < 0.3:  # 30% chance
            moderator_comment = self.generate_moderator_intervention()
            self.chat_history.append({
                'speaker': self.name,
                'content': moderator_comment,
                'round': self.round_count
            })
        
        return {
            'round': self.round_count,
            'speakers': [agent.name for agent in selected_speakers],
            'responses': responses,
            'intent_scores': intent_scores,
            'continue': self.should_continue_debate()
        } 
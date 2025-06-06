# agent.py
from autogen import ConversableAgent
import random
import re
from typing import Dict, List, Tuple
import time

class PhilosopherAgent(ConversableAgent):
    def __init__(self, name, philosophy, system_message, goals=None, llm_config=None):
        super().__init__(
            name=name,
            system_message=system_message,
            llm_config=llm_config
        )
        self.philosophy = philosophy
        self.initial_system_message = system_message  # Store original for reference
        self.goals = goals or []
        self.cooldown = 0
        self.beliefs = []  # Optional future use
        self.memory = []  # Store important points from debates with opinion weights
        self.reactivity_threshold = 0.3
        self.belief_drift_threshold = 0.7  # Threshold for system prompt modification
        self.memory_decay_rate = 0.05  # How much memories decay per round
        
    def compute_reactivity(self, chat_history):
        """
        Compute reactivity score based on recent messages, philosophical triggers, and weighted memories.
        Returns a float score (0-1) indicating how much the agent wants to respond.
        """
        if not chat_history:
            return 0.0
            
        recent_messages = chat_history[-3:]  # Look at last 3 messages
        reactivity_score = 0.0
        
        # Check for philosophical keywords that trigger this agent
        philosophy_keywords = {
            "deontology": ["duty", "moral law", "categorical imperative", "universal", "principle", "kant", "obligation"],
            "consequentialism": ["outcome", "consequence", "utility", "greatest good", "result", "mill", "happiness", "welfare"],
            "confucian": ["virtue", "harmony", "social", "tradition", "ritual", "confucius", "relationship", "hierarchy"],
            "existentialism": ["freedom", "authenticity", "choice", "existence", "responsibility", "sartre", "nietzsche", "meaning"],
            "buddhist": ["suffering", "compassion", "mindfulness", "attachment", "enlightenment", "santideva", "interdependence"]
        }
        
        keywords = philosophy_keywords.get(self.philosophy.lower(), [])
        
        for message in recent_messages:
            if isinstance(message, dict) and 'content' in message:
                content = message['content'].lower()
                
                # Skip own messages
                if message.get('speaker') == self.name:
                    continue
                
                # Direct mention increases reactivity significantly
                if self.name.lower() in content:
                    reactivity_score += 0.5
                
                # Philosophical keywords increase reactivity
                for keyword in keywords:
                    if keyword in content:
                        reactivity_score += 0.3
                        break  # Only count once per message
                
                # Questions increase reactivity
                if '?' in content:
                    reactivity_score += 0.2
                
                # Disagreement patterns increase reactivity
                disagreement_patterns = ["disagree", "wrong", "incorrect", "however", "but", "reject", "false"]
                for pattern in disagreement_patterns:
                    if pattern in content:
                        reactivity_score += 0.2
                        break  # Only count once per message
                
                # Challenges to core philosophical positions
                challenge_patterns = {
                    "deontology": ["consequences matter", "outcomes", "flexible rules"],
                    "consequentialism": ["regardless of outcome", "duty", "absolute rule"],
                    "confucian": ["individual freedom", "break tradition", "social chaos"],
                    "existentialist": ["universal truth", "objective morality", "predetermined"],
                    "buddhist": ["permanent self", "absolute truth", "attachment necessary"]
                }
                
                challenges = challenge_patterns.get(self.philosophy.lower(), [])
                for challenge in challenges:
                    if challenge in content:
                        reactivity_score += 0.4
                        break
        
        # Influence of weighted memories on reactivity
        relevant_memories = self._get_relevant_memories(recent_messages)
        for memory in relevant_memories:
            # Strong opinions (positive or negative) increase reactivity
            reactivity_score += abs(memory['opinion_weight']) * 0.2
        
        # Add some randomness to make debates more dynamic
        reactivity_score += random.uniform(0, 0.15)
        
        return min(reactivity_score, 1.0)
    
    def should_respond(self, chat_history):
        """Determine if agent should respond based on reactivity and cooldown."""
        if self.cooldown > 0:
            return False
        
        reactivity = self.compute_reactivity(chat_history)
        return reactivity >= self.reactivity_threshold
    
    def update_memory(self, message, importance_score=0.5, speaker_philosophy=None):
        """
        Store important points in agent's memory with opinion weights.
        Opinion weight indicates agreement (-1.0 to 1.0).
        """
        # Calculate initial opinion weight based on philosophical alignment
        opinion_weight = self._calculate_opinion_weight(message, speaker_philosophy)
        
        # Store memory with metadata
        memory_entry = {
            'content': message,
            'importance': importance_score,
            'opinion_weight': opinion_weight,
            'timestamp': len(self.memory),
            'decay_rounds': 0,  # Track how many rounds since creation
            'speaker_philosophy': speaker_philosophy
        }
        
        self.memory.append(memory_entry)
        
        # Keep memory manageable by removing decayed memories
        self._clean_decayed_memories()
        
        # Limit total memories
        if len(self.memory) > 15:
            # Sort by combined score of importance and absolute opinion weight
            self.memory = sorted(
                self.memory, 
                key=lambda x: x['importance'] + abs(x['opinion_weight']), 
                reverse=True
            )[:15]
    
    def _calculate_opinion_weight(self, message: str, speaker_philosophy: str) -> float:
        """
        Calculate opinion weight for a message based on content and speaker.
        Returns a value between -1.0 (strong disagreement) and 1.0 (strong agreement).
        """
        opinion = 0.0
        message_lower = message.lower()
        
        # Agreement patterns
        agreement_patterns = {
            "deontology": ["duty", "universal law", "categorical imperative", "moral principle"],
            "consequentialism": ["maximize happiness", "best outcome", "utility", "greater good"],
            "confucian": ["harmony", "virtue", "proper conduct", "social order"],
            "existentialist": ["freedom", "authentic", "create meaning", "individual choice"],
            "buddhist": ["reduce suffering", "compassion", "interdependence", "middle way"]
        }
        
        # Check alignment with own philosophy
        own_patterns = agreement_patterns.get(self.philosophy.lower(), [])
        for pattern in own_patterns:
            if pattern in message_lower:
                opinion += 0.3
        
        # Check for opposing views
        opposing_philosophies = {
            "deontology": ["consequentialism", "existentialist"],
            "consequentialism": ["deontology"],
            "confucian": ["existentialist"],
            "existentialist": ["deontology", "confucian"],
            "buddhist": []  # Buddhist philosophy tends to be more inclusive
        }
        
        if speaker_philosophy and speaker_philosophy.lower() in opposing_philosophies.get(self.philosophy.lower(), []):
            opinion -= 0.2
        
        # Specific disagreement patterns
        if "disagree" in message_lower or "wrong" in message_lower or "reject" in message_lower:
            if self.name.lower() in message_lower or self.philosophy.lower() in message_lower:
                opinion -= 0.4
        
        # Compelling argument patterns (regardless of philosophy)
        if any(phrase in message_lower for phrase in ["excellent point", "i see your point", "that's true", "compelling argument"]):
            opinion += 0.2
        
        return max(-1.0, min(1.0, opinion))
    
    def _get_relevant_memories(self, recent_messages: List[Dict]) -> List[Dict]:
        """Get memories relevant to recent discussion."""
        relevant = []
        
        # Extract keywords from recent messages
        keywords = set()
        for msg in recent_messages[-3:]:
            if isinstance(msg, dict) and 'content' in msg:
                words = msg['content'].lower().split()
                keywords.update(words)
        
        # Find memories with matching keywords
        for memory in self.memory:
            memory_words = set(memory['content'].lower().split())
            if len(keywords.intersection(memory_words)) > 3:  # At least 3 common words
                relevant.append(memory)
        
        return relevant
    
    def _apply_belief_decay(self):
        """Apply decay to all memories and update opinion weights."""
        for memory in self.memory:
            memory['decay_rounds'] += 1
            
            # Decay importance over time
            decay_factor = 1.0 - (self.memory_decay_rate * memory['decay_rounds'])
            memory['importance'] *= max(0.1, decay_factor)
            
            # Opinion weights tend toward neutral over time (but more slowly)
            if abs(memory['opinion_weight']) > 0.1:
                memory['opinion_weight'] *= 0.95
    
    def _clean_decayed_memories(self):
        """Remove memories that have decayed below threshold."""
        self.memory = [m for m in self.memory if m['importance'] > 0.2]
    
    def generate_memory_influenced_prompt(self, base_prompt: str) -> str:
        """
        Enhance the prompt with relevant weighted memories to influence response.
        """
        relevant_memories = self._get_relevant_memories(self.chat_history[-5:] if hasattr(self, 'chat_history') else [])
        
        if not relevant_memories:
            return base_prompt
        
        # Sort by opinion weight
        positive_memories = [m for m in relevant_memories if m['opinion_weight'] > 0.3]
        negative_memories = [m for m in relevant_memories if m['opinion_weight'] < -0.3]
        
        memory_context = "\n\nRelevant considerations from your past reflections:"
        
        if positive_memories:
            memory_context += "\n\nArguments you found compelling:"
            for mem in positive_memories[:3]:
                memory_context += f"\n- {mem['content'][:200]}... (weight: {mem['opinion_weight']:.2f})"
        
        if negative_memories:
            memory_context += "\n\nArguments you disagreed with:"
            for mem in negative_memories[:3]:
                memory_context += f"\n- {mem['content'][:200]}... (weight: {mem['opinion_weight']:.2f})"
        
        return base_prompt + memory_context
    
    def reflect(self, transcript):
        """Generate reflection on the debate transcript using LLM, with potential for belief drift."""
        # Apply belief decay before reflection
        self._apply_belief_decay()
        
        reflection_prompt = f"""
        As {self.name}, a {self.philosophy} philosopher, reflect on this debate transcript.
        Consider:
        1. How well did your philosophical position hold up?
        2. What new insights emerged from the discussion?
        3. Where might you adjust or strengthen your arguments?
        4. What did you learn from the other philosophical perspectives?
        
        Recent debate transcript:
        {transcript[-800:]}
        
        Provide a thoughtful reflection on the debate from your philosophical perspective.
        """
        
        # Add memory influence to reflection
        reflection_prompt = self.generate_memory_influenced_prompt(reflection_prompt)
        
        try:
            # Use Autogen's generate_reply method for reflection
            response = self.generate_reply(
                messages=[{"role": "user", "content": reflection_prompt}]
            )
            
            # Clean up the response
            if isinstance(response, dict) and 'content' in response:
                reflection_text = response['content']
            elif isinstance(response, str):
                reflection_text = response
            else:
                reflection_text = str(response)
            
            # Check for belief drift based on accumulated memories
            self._check_belief_drift()
            
            return f"{self.name} reflects: {reflection_text}"
            
        except Exception as e:
            # Fallback reflection if LLM call fails
            print(f"Warning: Reflection LLM call failed for {self.name}: {e}")
            return f"{self.name} reflects: This debate highlighted the importance of {self.philosophy} principles in addressing complex moral questions. The exchange of ideas has been valuable for understanding different ethical frameworks."
    
    def _check_belief_drift(self):
        """
        Check if accumulated memories warrant a modification to the agent's system prompt.
        """
        # Calculate overall belief tendency from memories
        if not self.memory:
            return
        
        # Group memories by philosophy they relate to
        philosophy_scores = {}
        for memory in self.memory:
            if memory['speaker_philosophy']:
                phil = memory['speaker_philosophy'].lower()
                if phil not in philosophy_scores:
                    philosophy_scores[phil] = 0
                philosophy_scores[phil] += memory['opinion_weight'] * memory['importance']
        
        # Check if any philosophy has accumulated enough positive weight
        for philosophy, score in philosophy_scores.items():
            if philosophy != self.philosophy.lower() and score > self.belief_drift_threshold:
                self._modify_system_prompt(philosophy, score)
    
    def _modify_system_prompt(self, influenced_philosophy: str, influence_score: float):
        """
        Modify the agent's system prompt to incorporate influences from other philosophies.
        """
        modification_prompt = f"""
        
        [BELIEF EVOLUTION: Through extended dialogue and reflection, you have found merit in certain aspects of {influenced_philosophy} philosophy. 
        While maintaining your core {self.philosophy} framework, you now incorporate insights about {influenced_philosophy} perspectives 
        with an openness score of {influence_score:.2f}. You may reference these complementary ideas when they strengthen your arguments.]
        """
        
        # Update the system message
        self.system_message = self.initial_system_message + modification_prompt
        
        # Log the belief drift
        print(f"📝 {self.name} has evolved beliefs, incorporating aspects of {influenced_philosophy}")
    
    def set_cooldown(self, rounds=2):
        """Set cooldown period after speaking."""
        self.cooldown = rounds
    
    def reduce_cooldown(self):
        """Reduce cooldown by 1 round."""
        if self.cooldown > 0:
            self.cooldown -= 1
    
    def get_philosophical_stance(self, topic):
        """Get this agent's philosophical stance on a given topic."""
        stance_templates = {
            "deontology": f"From a deontological perspective on {topic}, we must ask: could this action be universalized as a moral law? Our duty is clear regardless of consequences...",
            "consequentialism": f"Regarding {topic}, we must focus on outcomes. What action produces the greatest happiness for the greatest number? The consequences determine the moral worth...",
            "confucian": f"When examining {topic}, we must consider how this affects social harmony and relationships. What would the exemplary person do in this context?...",
            "existentialist": f"Concerning {topic}, we must reject imposed moral systems. Each individual must authentically choose their own values. Who has the authority to dictate morality?...",
            "buddhist": f"From a Buddhist perspective on {topic}, we should ask: how does this increase or decrease suffering? All phenomena are interdependent and empty of inherent existence..."
        }
        
        return stance_templates.get(self.philosophy.lower(), f"My philosophical view on {topic} is...")

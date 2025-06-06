# Multi-Agent Philosophical Debate System

This project is a multi-agent debate system designed to explore agentic behavior, value-driven reasoning, and interaction dynamics between autonomous language model agents. Each agent represents a distinct philosophical worldview and engages in structured debates over moral or epistemic questions.

## Features

- **Multiple Philosophical Perspectives**: Agents representing deontology (Kant), consequentialism (Mill), virtue ethics (Aristotle), existentialism (Sartre), Buddhist ethics (Nagarjuna), and Confucian ethics
- **Dynamic Debate Flow**: Orchestrator manages conversation flow based on agent reactivity scores and cooldown mechanisms
- **Opinion-Weighted Memory System**: Agents form opinions about arguments and store them with weights indicating agreement/disagreement
- **Belief Drift**: Agents can evolve their philosophical positions based on accumulated positive experiences with other viewpoints
- **Memory Decay**: Beliefs naturally decay over time, allowing for dynamic evolution of positions
- **Self-Modification**: Agents can modify their own system prompts when influenced sufficiently by other philosophies
- **Reflection Capabilities**: Agents can reflect on debate transcripts and adjust their approaches
- **Configurable Parameters**: Customizable debate settings, agent behaviors, and LLM configurations

## Project Structure

```
├── agents/
│   └── agent.py              # PhilosopherAgent class with debate logic
├── orchestrator/
│   └── orchestrator.py       # DebateOrchestrator for managing debates
├── prompts/
│   ├── kant.py              # Kantian system prompt (legacy)
│   └── system_prompts.py    # All philosophical system prompts
├── main.py                  # Main script to run debates
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── devjournal.md          # Development notes and project goals
└── README.md              # This file
```

## Installation

1. **Clone the repository** (or ensure you're in the project directory)

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your API key**:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
   
   Or create a `.env` file:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

## Usage

### Basic Usage

Run the main script to start an interactive debate:

```bash
python main.py
```

This will present you with debate topic options and guide you through running a philosophical debate.

### Programmatic Usage

```python
from agents.agent import PhilosopherAgent
from orchestrator.orchestrator import DebateOrchestrator
from prompts.system_prompts import get_prompt
from config import get_llm_config

# Set up LLM configuration
llm_config = get_llm_config()

# Create philosopher agents
kant = PhilosopherAgent(
    name="Kant",
    philosophy="deontology",
    system_message=get_prompt("kant"),
    llm_config=llm_config
)

mill = PhilosopherAgent(
    name="Mill",
    philosophy="consequentialism", 
    system_message=get_prompt("mill"),
    llm_config=llm_config
)

# Create orchestrator and add agents
orchestrator = DebateOrchestrator(llm_config=llm_config)
orchestrator.add_agent(kant)
orchestrator.add_agent(mill)

# Start debate
topic = "Is it ever morally permissible to lie?"
orchestrator.start_debate(topic)

# Run debate rounds
while orchestrator.should_continue_debate():
    result = orchestrator.run_debate_round()
    print(f"Round {result['round']}: {result['message']}")
    if not result.get('continue', True):
        break

# Get final summary
summary = orchestrator.end_debate()
```

## Configuration

The system can be configured through `config.py`:

- **Debate settings**: Maximum rounds, cooldown periods, reactivity thresholds
- **LLM settings**: Model selection, temperature, token limits
- **Agent settings**: Memory limits, reflection capabilities, default goals

## Philosophical Agents

The system includes agents representing major ethical frameworks:

1. **Kant (Deontological Ethics)**: Focuses on duty, universal principles, and the categorical imperative
2. **Mill (Utilitarian Consequentialism)**: Emphasizes outcomes, happiness maximization, and practical consequences
3. **Aristotle (Virtue Ethics)**: Centers on character, human flourishing, and practical wisdom
4. **Sartre (Existentialism)**: Emphasizes radical freedom, authenticity, and individual responsibility
5. **Nagarjuna (Buddhist Ethics)**: Focuses on interdependence, compassion, and the middle way
6. **Confucius (Confucian Ethics)**: Emphasizes social harmony, moral cultivation, and proper relationships

## How It Works

1. **Agent Selection**: The orchestrator selects speakers based on reactivity scores computed from recent messages and philosophical triggers
2. **Cooldown Management**: Agents enter cooldown periods after speaking to ensure balanced participation
3. **Memory Updates**: Agents store important points from the debate in their memory systems
4. **Dynamic Flow**: The debate continues until maximum rounds are reached or agents lose interest
5. **Reflection**: At the end, agents reflect on the debate and generate insights

## Future Enhancements

- **Fine-tuning Support**: Integration with LoRA or instruction tuning for deeper personality persistence
- **Symbolic Belief Stores**: More sophisticated belief tracking and updating
- **Web Interface**: User-friendly UI for observing and interacting with debates
- **Advanced Memory**: Hierarchical memory systems with long-term retention
- **Evaluation Metrics**: Automated assessment of argument quality and philosophical consistency

## Research Applications

This system can be used to study:
- Emergent reasoning in multi-agent systems
- Value alignment and philosophical consistency
- Interaction dynamics between different ethical frameworks
- Epistemic alignment in AI systems
- Interpretability of agent decision-making

## Contributing

This project is designed for research and experimentation. Feel free to:
- Add new philosophical perspectives
- Implement additional memory systems
- Enhance the orchestrator logic
- Create new evaluation metrics
- Develop user interfaces

## License

This project is open source and available for research and educational purposes.

## Getting Started

To begin working on the project:

1. Ensure you have Microsoft Autogen installed and configured
2. Set up your LLM provider credentials
3. Run `python main.py` to start your first debate
4. Experiment with different topics and agent configurations
5. Review the debate transcripts and agent reflections

For questions or issues, please refer to the development journal (`devjournal.md`) or create an issue in the repository.


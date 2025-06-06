# What is this?

multi-agent debate system, exploring emergence in agents through memory dynamics.
each agent is grounded in a philosophical worldview (rn through ICL)
^^ note, do this through fine tuning later

the agents debate, guided by an orchestrator.
we study their behavior.

Long term goal: how do memory augmented, goal-aligned agents interact? how will this interaction change when extend to humans?
a testbed for epistemic alignment / interpretability.

# Journal Entries

## Entry 1
basic ConversableAgents using autogen
agents have: internal goals, memory, reactivity score
agents submit "intent to speak" (based on reactivity score)
orchestrator guides debate / allows agents to speak

## Entry 2
switching to opinion weighted memory-
agent "hears" an argument, calculates opinions weights (positive = aligned w/agent, negative = misaligned w/agent)
memory influences agent output
reflection can trigger agent to modify worldview (append to their own system prompt)

todo: 
can explore distributed/shared memory
    this can build tension through [shared epistemology but contrasting worldview]
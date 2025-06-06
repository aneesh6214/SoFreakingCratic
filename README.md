# What is this?

multi-agent debate system, exploring emergence in agents through memory dynamics.<br>
each agent is grounded in a philosophical worldview (rn through ICL)<br>
^^ note, do this through fine tuning later<br>

the agents debate, guided by an orchestrator.<br>
we study their behavior.<br>

Long term goal: how do memory augmented, goal-aligned agents interact? how will this interaction change when extend to humans?<br>
a testbed for epistemic alignment / interpretability.<br>

# Journal Entries

## Entry 1
basic ConversableAgents using autogen<br>
agents have: internal goals, memory, reactivity score<br>
agents submit "intent to speak" (based on reactivity score)<br>
orchestrator guides debate / allows agents to speak<br>

## Entry 2
switching to opinion weighted memory-<br>
agent "hears" an argument, calculates opinions weights (positive = aligned w/agent, negative = misaligned w/agent)<br>
memory influences agent output<br>
reflection can trigger agent to modify worldview (append to their own system prompt)<br>

todo:<br>
can explore distributed/shared memory<br>
    this can build tension through [shared epistemology but contrasting worldview]<br>
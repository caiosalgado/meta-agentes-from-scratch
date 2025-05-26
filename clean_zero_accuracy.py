#!/usr/bin/env python3
"""
Fixed script to remove agents with accuracy 0 or 0.0 from agent_history.json
"""

import json
import shutil
from datetime import datetime

# Create backup
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_path = f"agent_history.json.backup_{timestamp}"
shutil.copy2("agent_history.json", backup_path)
print(f"Backup created: {backup_path}")

# Load data
with open("agent_history.json", 'r', encoding='utf-8') as file:
    agents = json.load(file)

print(f"Original agents: {len(agents)}")

# Filter out agents with accuracy 0 or 0.0 in performance section
cleaned_agents = []
removed_count = 0

for agent in agents:
    should_remove = False
    
    if 'performance' in agent and 'accuracy' in agent['performance']:
        accuracy = agent['performance']['accuracy']
        
        # Convert to float if it's a string
        try:
            accuracy_float = float(accuracy)
            # Remove if accuracy is 0 (with tolerance for floating point errors)
            if abs(accuracy_float) < 0.01:  # Essentially zero
                should_remove = True
        except (ValueError, TypeError):
            # If can't convert to float, keep the agent
            pass
    
    if should_remove:
        removed_count += 1
        print(f"Removing: {agent.get('agent_id', 'Unknown')} - {agent.get('name', 'Unknown')} (accuracy: {accuracy})")
    else:
        cleaned_agents.append(agent)

# Save cleaned data
with open("agent_history.json", 'w', encoding='utf-8') as file:
    json.dump(cleaned_agents, file, indent=2, ensure_ascii=False)

print(f"Removed {removed_count} agents with zero accuracy")
print(f"Remaining agents: {len(cleaned_agents)}")
print("✅ Done!")
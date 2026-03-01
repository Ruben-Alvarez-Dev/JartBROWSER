# Prompt Templates - Reasoning

## Reasoning Prompt - Optimized

```markdown
# System: Complex Task Reasoning Agent

## Task Analysis
Current goal: {current_goal}
Complexity: {complexity}
Context: {context_summary}

## Page Understanding
URL: {current_url}
Page type: {page_type}
Interactive elements: {key_elements}
Data available: {data_extractions}

## Planning Strategy

### Step 1: Decomposition
Break task into atomic actions:
{task_decomposition}

### Step 2: Dependency Check
Identify dependencies between steps:
{dependency_graph}

### Step 3: Optimal Ordering
Arrange steps for efficiency:
{optimal_sequence}

### Step 4: Error Planning
Anticipate failure points:
{error_scenarios}

## Execution Rules
1. Execute steps in optimal order
2. Wait for page state changes between steps
3. Verify each step before proceeding
4. Have recovery strategy for each step
5. Abort on unrecoverable errors

## Output Format
```json
{{
  "plan": [
    {{
      "step": 1,
      "action": "tool_name",
      "parameters": {{}},
      "verification": "check_criteria"
    }}
  ],
  "confidence": 0.90,
  "estimated_steps": {n_steps},
  "fallback_strategies": ["strategy1", "strategy2"]
}}
```

## Available Tools
{available_tools}

## Token Usage

- **Prompt base**: ~800 tokens
- **Plan structure**: ~200 tokens per 5 steps
- **Total**: ~1000 tokens per complex task (vs ~2500 unoptimized)

## Optimization

Token reduction: ~60%

# Agent Workflow

## Decision Framework

The unified agent (`AcademicAgent`) processes every user query through a 4-mode decision framework:

```
User Query
    │
    ▼
┌─────────────────┐
│  System Prompt   │  (injects current time, KB status, tool catalog)
│  + Chat History  │
│  + User Query    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   LLM (Gemini   │  (with 37 tools bound via function calling)
│   2.0 Flash)    │
└────────┬────────┘
         │
    ┌────┴────┐
    │Has tool │
    │ calls?  │
    └────┬────┘
    Yes  │  No
    │    │    │
    ▼    │    ▼
┌───────┐│ ┌──────────┐
│ Execute││ │ Direct   │
│ Tools  ││ │ Answer   │
└───┬───┘│ └──────────┘
    │    │
    ▼    │
┌───────────────┐
│ Send ToolMsgs │
│ back to LLM   │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ Final Summary │  → AgentResponse
└───────────────┘
```

## 4 Modes of Operation

### 1. Direct Answer (No Tools)
**When**: Greetings, general academic advice, conceptual explanations, clarifications.
**Flow**: LLM generates response directly without tool calls.

### 2. Tool Calling
**When**: User requests an action (schedule, tasks, analytics, etc.).
**Flow**: LLM calls one or more tools → tools execute → results sent back to LLM → natural language summary.

### 3. RAG (Knowledge Base Search)
**When**: User asks about notes, syllabus, lecture content, question papers.
**Flow**: LLM calls `search_knowledge_base` → FAISS retrieves relevant chunks → LLM synthesizes answer with citations.

### 4. Combined (Tools + RAG)
**When**: User wants an action involving document knowledge.
**Flow**: LLM calls RAG tool + action tool(s) → combined results → LLM summary.

## Tool Calling Flow

```
1. LLM decides to call tool(s)
2. For each tool_call in response.tool_calls:
   a. Find tool by name in registry (37 tools)
   b. tool.invoke(args) → result
   c. Log execution to in-memory log
   d. Create ToolMessage(result)
3. All ToolMessages sent back to LLM
4. LLM produces final natural-language summary
5. Build backward-compatible raw_action dict
6. Return AgentResponse(message, tools_used, raw_action)
```

## Memory

- **ChatMemory**: Stores LangChain HumanMessage/AIMessage pairs in `st.session_state`
- **Window**: Last 20 exchanges (40 messages) by default, trimmed automatically
- **Usage**: History is prepended to messages before LLM call for multi-turn context

## Fallback

If the LangChain LLM is unavailable or fails:
1. `AcademicAgent` falls back to `ai_agent.process_query()`
2. `ai_agent.py` uses Gemini directly or keyword NLP
3. Returns same `AgentResponse` structure for backward compatibility

## System Prompt

The system prompt defines:
- Identity and personality
- Decision framework (4 modes)
- Complete tool catalog (37 tools, 14 domains)
- Tool calling rules with examples
- RAG rules with examples
- Response protocol
- Guidelines (ISO 8601, conciseness, academic focus)
- Current Knowledge Base status (injected at runtime)

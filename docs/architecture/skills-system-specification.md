# Skills System Specification

## Overview

JartBROWSER Skills System provides a flexible, extensible framework for defining and executing complex automation tasks. Skills are defined in YAML format and can be chained, parallelized, and managed through REST API and MCP.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      SKILLS SYSTEM                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────────┐    │
│  │  Skill Definitions (YAML)                │    │
│  │  - Semantic analysis                         │    │
│  │  - Web research                               │    │
│  │  - Automation                                │    │
│  │  - Data extraction                            │    │
│  │  └── Custom skills                           │    │
│  └───────────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────────┐    │
│  │  Skill Engine                       │    │
│  │  - Parser & Validator                        │    │
│  │  - Execution Orchestrator                   │    │
│  │  - Chaining Engine                            │    │
│  │  - Parallel Executor                         │    │
│  │  └── Error Recovery                          │    │
│  └───────────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────────┐    │
│  │  Storage Layer                        │    │
│  │  - SQLite (skills metadata)                  │    │
│  │  - Redis (execution cache)                   │    │
│  │  - File System (skill files)                  │    │
│  └───────────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────────┐    │
│  │  REST API Endpoints                    │    │
│  │  - /skills (CRUD)                           │    │
│  │  - /skills/{id}/execute                   │    │
│  │  - /skills/{id}/chain                       │    │
│  │  └── /skills/categories                       │    │
│  └───────────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────────┐    │
│  │  MCP Tools                          │    │
│  │  - list_skills                              │    │
│  │  - get_skill                                │    │
│  │  - execute_skill                            │    │
│  │  └── skill_metrics                          │    │
│  └───────────────────────────────────────────────────────────────────┘    │
│                                                                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Skill Definition Schema

### YAML Format

```yaml
name: <skill_name>           # Required: Unique skill identifier
description: <description>     # Required: One-line description
version: <semver>             # Required: Semantic version
author: <author>             # Required: Skill author or team

metadata:                      # Optional: Additional metadata
  category: <category>        # Required: Category (semantic-analysis, web-research, automation, data-extraction)
  tags: [<tag1>, <tag2>]     # Optional: List of tags
  complexity: <low|medium|high> # Required: Execution complexity
  estimated_time: <seconds>     # Optional: Estimated execution time
  dependencies: [<skill>]      # Optional: Skills this depends on
  capabilities: [<cap>]         # Optional: Required capabilities (browser_control, vision, research)

tools:                          # Required: Tools provided by this skill
  - name: <tool_name>
    description: <description>
    input_schema:
      type: <type>
      properties:
        <property_name>:
          type: <type>
          description: <description>
          required: [<field>]
    output_schema:
      type: <type>
      properties: {}

prompts:                         # Optional: Custom prompts
  system_prompt: <prompt>         # Optional: System prompt for this skill
  task_prompt: <prompt>          # Optional: Task-specific prompt

execution:                      # Required: Execution configuration
  max_retries: <number>          # Default: 3
  timeout: <seconds>             # Default: 60
  parallelizable: <boolean>        # Default: false
  retry_strategy: <strategy>     # linear, exponential, immediate

validation:                     # Optional: Input/output validation
  input_validator: <code>       # Optional: Custom validation code
  output_validator: <code>      # Optional: Custom validation code
  schema_validation: <boolean>  # Default: true

error_handling:                 # Optional: Error handling
  fallback_strategies: [<strategy>]
  recovery_prompts: [<prompt>]
  continue_on_error: <boolean>  # Default: false

monitoring:                    # Optional: Monitoring configuration
  log_level: <debug|info|warn|error>
  metrics_enabled: <boolean>
  track_success_rate: <boolean>
```

## Skill Categories

### 1. Semantic Analysis
Skills that analyze and understand web page structure.

**Capabilities**: browser_control

**Examples**:
- `semantic-analysis` - Extract page structure and content
- `content-classification` - Classify page type (product, blog, form, etc.)
- `element-extraction` - Extract interactive elements with metadata

### 2. Web Research
Skills that research across multiple web sources.

**Capabilities**: browser_control, research

**Examples**:
- `web-research` - Research information across multiple sources
- `price-comparison` - Compare prices across e-commerce sites
- `source-verification` - Verify information from multiple sources

### 3. Automation
Skills that automate repetitive web tasks.

**Capabilities**: browser_control, automation

**Examples**:
- `form-filling` - Fill web forms with validation
- `multi-step-task` - Execute multi-step tasks with branching
- `scheduled-task` - Execute tasks on schedule

### 4. Data Extraction
Skills that extract structured data from web pages.

**Capabilities**: browser_control, extraction

**Examples**:
- `product-extraction` - Extract product information
- `contact-extraction` - Extract contact information
- `table-extraction` - Extract tabular data

## Execution Engine

### 1. Parser & Validator

**Responsibilities**:
- Parse YAML skill definitions
- Validate schema compliance
- Check dependencies and circular references
- Load tool definitions

**API**: Internal module, no REST endpoints

### 2. Execution Orchestrator

**Responsibilities**:
- Execute skills in correct order
- Handle tool invocations
- Manage skill timeouts and retries
- Collect execution results

**API**: 
- `POST /api/v1/skills/{id}/execute` - Execute a skill
- `POST /api/v1/skills/{id}/chain` - Chain multiple skills

### 3. Chaining Engine

**Responsibilities**:
- Chain multiple skills together
- Pass data between skills
- Handle conditional logic
- Support parallel branches

**API**:
- `POST /api/v1/skills/chain` - Chain multiple skills

**Chain Format**:
```json
{
  "skills": ["skill1", "skill2", "skill3"],
  "data_flow": {
    "skill1_output": "skill2_input",
    "skill2_output": "skill3_input"
  },
  "condition": {
    "if": "skill1_success",
    "then": "skill2"
  }
}
```

### 4. Parallel Executor

**Responsibilities**:
- Execute skills in parallel
- Merge results from multiple skills
- Handle parallel errors
- Limit concurrent executions

**API**:
- `POST /api/v1/skills/parallel` - Execute skills in parallel

### 5. Error Recovery

**Responsibilities**:
- Detect and classify errors
- Apply recovery strategies
- Log errors with context
- Notify monitoring system

**Recovery Strategies**:
- `retry` - Retry the skill with exponential backoff
- `fallback` - Use alternative skill
- `skip` - Skip this skill and continue
- `abort` - Abort the entire chain

## REST API Endpoints

### Skills Management

#### List All Skills
```
GET /api/v1/skills
```

**Response**:
```json
{
  "skills": [
    {
      "id": "semantic-analysis",
      "name": "Semantic Page Analysis",
      "description": "Extract semantic information from web pages",
      "category": "semantic-analysis",
      "version": "1.0.0",
      "author": "JartBROWSER Team",
      "complexity": "medium",
      "estimated_time": 30,
      "capabilities": ["browser_control"],
      "tags": ["semantic", "analysis"],
      "tools": [...]
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 1
  }
}
```

#### Get Skill Details
```
GET /api/v1/skills/{skill_id}
```

#### Create Skill
```
POST /api/v1/skills
Content-Type: application/x-yaml
```

**Body**: YAML skill definition

#### Update Skill
```
PUT /api/v1/skills/{skill_id}
Content-Type: application/x-yaml
```

**Body**: Partial or full YAML skill definition

#### Delete Skill
```
DELETE /api/v1/skills/{skill_id}
```

### Skill Execution

#### Execute Single Skill
```
POST /api/v1/skills/{skill_id}/execute
Content-Type: application/json
```

**Body**:
```json
{
  "parameters": {
    "param1": "value1",
    "param2": "value2"
  },
  "context": {
    "url": "https://example.com",
    "page_data": {}
  },
  "options": {
    "max_retries": 5,
    "timeout": 120,
    "parallelizable": false
  }
}
```

**Response**:
```json
{
  "execution_id": "exec_12345",
  "skill_id": "semantic-analysis",
  "status": "running",
  "started_at": "2026-03-01T15:00:00Z"
}
```

#### Chain Multiple Skills
```
POST /api/v1/skills/chain
Content-Type: application/json
```

**Body**:
```json
{
  "skills": [
    {
      "id": "semantic-analysis",
      "parameters": {}
    },
    {
      "id": "web-research",
      "parameters": {
        "query": "product prices"
      }
    }
  ],
  "chain_config": {
    "parallel": false,
    "stop_on_failure": true,
    "data_flow": {}
  }
}
```

#### Execute Skills in Parallel
```
POST /api/v1/skills/parallel
Content-Type: application/json
```

**Body**:
```json
{
  "skills": [
    {"id": "semantic-analysis", "parameters": {}},
    {"id": "web-research", "parameters": {}}
  ],
  "max_concurrent": 3
}
```

### Execution Status

#### Get Execution Status
```
GET /api/v1/skills/executions/{execution_id}
```

**Response**:
```json
{
  "execution_id": "exec_12345",
  "status": "running",
  "progress": 0.5,
  "current_step": "Analyzing page structure",
  "results": {},
  "errors": [],
  "started_at": "2026-03-01T15:00:00Z",
  "estimated_completion": "2026-03-01T15:01:00Z"
}
```

#### List All Executions
```
GET /api/v1/skills/executions?skill_id={id}&status={status}&limit=10
```

#### Cancel Execution
```
POST /api/v1/skills/executions/{execution_id}/cancel
```

### Skill Categories

#### List Categories
```
GET /api/v1/skills/categories
```

**Response**:
```json
{
  "categories": [
    {
      "id": "semantic-analysis",
      "name": "Semantic Analysis",
      "description": "Skills for analyzing web page structure and content",
      "skill_count": 5
    }
  ]
}
```

#### Get Skills by Category
```
GET /api/v1/skills?category={category_id}
```

## MCP Tools

### List Skills
```
Tool: list_skills
Description: List all available skills
Input Schema:
  type: object
  properties: {}
Output: Array of skill objects
```

### Get Skill Details
```
Tool: get_skill
Description: Get details of a specific skill
Input Schema:
  type: object
  properties:
    skill_id:
      type: string
      required: true
Output: Skill object with full definition
```

### Execute Skill
```
Tool: execute_skill
Description: Execute a skill with parameters
Input Schema:
  type: object
  properties:
    skill_id:
      type: string
      required: true
    parameters:
      type: object
      additionalProperties: true
    context:
      type: object
      additionalProperties: true
Output: Execution result with status and data
```

### Chain Skills
```
Tool: chain_skills
Description: Chain multiple skills together
Input Schema:
  type: object
  properties:
    skills:
      type: array
      items:
        type: object
        properties:
          id:
            type: string
          parameters:
            type: object
    chain_config:
      type: object
      properties:
        parallel:
          type: boolean
        stop_on_failure:
          type: boolean
        data_flow:
          type: object
Output: Chain execution result
```

### Skill Metrics
```
Tool: skill_metrics
Description: Get performance metrics for skills
Input Schema:
  type: object
  properties:
    skill_id:
      type: string
      time_range:
      type: string
        enum: [1h, 24h, 7d, 30d]
Output: Metrics object with success rate, avg time, etc.
```

## Database Schema

### Skills Table

```sql
CREATE TABLE skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    version VARCHAR(50) NOT NULL,
    author VARCHAR(255),
    category VARCHAR(100) NOT NULL,
    tags JSONB,
    complexity VARCHAR(20),
    estimated_time INTEGER,
    capabilities JSONB,
    dependencies JSONB,
    tools JSONB NOT NULL,
    prompts JSONB,
    execution_config JSONB NOT NULL,
    validation_config JSONB,
    error_handling_config JSONB,
    monitoring_config JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

### Skill Executions Table

```sql
CREATE TABLE skill_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id UUID REFERENCES skills(id) ON DELETE CASCADE,
    execution_config JSONB NOT NULL,
    status VARCHAR(50) NOT NULL,
    progress FLOAT DEFAULT 0,
    results JSONB,
    errors JSONB,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    timeout_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_skill_executions_skill_id ON skill_executions(skill_id);
CREATE INDEX idx_skill_executions_status ON skill_executions(status);
CREATE INDEX idx_skill_executions_started_at ON skill_executions(started_at);
```

## Monitoring & Metrics

### Metrics Collection

Track the following metrics for each skill:

1. **Execution Metrics**
   - Average execution time
   - Success rate
   - Error rate by error type
   - Timeout rate

2. **Performance Metrics**
   - Average retry count
   - Average memory usage
   - CPU usage per execution

3. **Usage Metrics**
   - Most used skills
   - Least used skills
   - Usage by category

### Metrics API

```
GET /api/v1/skills/metrics
```

**Query Parameters**:
- `skill_id` - Metrics for specific skill
- `category` - Metrics for category
- `time_range` - 1h, 24h, 7d, 30d

**Response**:
```json
{
  "skill_id": "semantic-analysis",
  "execution_count": 1250,
  "success_rate": 0.92,
  "avg_execution_time": 28.5,
  "error_breakdown": {
    "timeout": 0.05,
    "invalid_input": 0.03,
    "network_error": 0.00
  },
  "time_series": [
    {
      "timestamp": "2026-03-01T15:00:00Z",
      "success_rate": 0.95
    }
  ]
}
```

## Security

### Skill Validation

1. **Schema Validation**: All skill definitions must pass YAML schema validation
2. **Dependency Check**: Skills cannot have circular dependencies
3. **Capability Check**: Verify required capabilities are available
4. **Input Sanitization**: Validate all inputs against schema
5. **Output Filtering**: Filter sensitive information from logs

### Rate Limiting

- API rate limits per skill execution
- Concurrent execution limits per user
- Resource quotas for CPU/memory

## Error Handling

### Error Types

1. **Validation Errors**
   - Invalid YAML syntax
   - Schema validation failed
   - Missing required fields

2. **Execution Errors**
   - Skill timeout
   - Tool not available
   - Invalid parameters

3. **System Errors**
   - Storage failure
   - Database connection error
   - Memory exhaustion

### Error Response Format

```json
{
  "error": {
    "type": "validation_error",
    "message": "Invalid skill definition",
    "details": {
      "field": "tools",
      "issue": "Required field missing"
    },
    "timestamp": "2026-03-01T15:00:00Z"
  }
}
```

## Extensibility

### Custom Skills

Users can create custom skills by:

1. Writing YAML skill definitions
2. Adding to `/skills/` directory
3. Registering via REST API
4. Testing via `/execute` endpoint

### Skill Plugins

Advanced skills can include:

1. **Custom Python code** in skill definition
2. **External tool integrations**
3. **Complex decision trees**
4. **Machine learning models**

## Examples

### Example 1: Semantic Analysis Skill

```yaml
name: semantic-analysis
description: Extract semantic information from web pages
version: 1.0.0
author: JartBROWSER Team

metadata:
  category: semantic-analysis
  tags: [semantic, analysis, page-understanding]
  complexity: medium
  estimated_time: 30
  capabilities: [browser_control]

tools:
  - name: get_page_structure
    description: Get page structure and interactive elements
    input_schema:
      type: object
      properties:
        include_coordinates:
          type: boolean
          default: true
    output_schema:
      type: object
      properties:
        structure:
          type: object
        elements:
          type: array

  - name: classify_content_type
    description: Classify page content type
    input_schema:
      type: object
      properties:
        page_content:
          type: string
    output_schema:
      type: object
      properties:
        page_type:
          type: string
          enum: [product_page, blog, form, dashboard, other]
        confidence:
          type: number
          minimum: 0
          maximum: 1

execution:
  max_retries: 3
  timeout: 60
  parallelizable: false

prompts:
  system_prompt: |
    You are an expert in semantic page analysis. Extract structured information from web pages.
  task_prompt: |
    Analyze the page structure and classify the content type.
```

### Example 2: Web Research Skill

```yaml
name: web-research
description: Research information across multiple web sources
version: 1.0.0
author: JartBROWSER Team

metadata:
  category: web-research
  tags: [research, multi-source, verification]
  complexity: high
  estimated_time: 120
  capabilities: [browser_control, research]

tools:
  - name: search_web
    description: Search web for information
    input_schema:
      type: object
      properties:
        query:
          type: string
        num_results:
          type: integer
          default: 10
    output_schema:
      type: object
      properties:
        results:
          type: array

  - name: extract_search_results
    description: Extract information from search results
    input_schema:
      type: object
      properties:
        urls:
          type: array
    output_schema:
      type: object
      properties:
        extracted_data:
          type: array

  - name: verify_information
    description: Verify information from multiple sources
    input_schema:
      type: object
      properties:
        information:
          type: array
    output_schema:
      type: object
      properties:
        verified_info:
          type: object
        confidence_score:
          type: number

execution:
  max_retries: 5
  timeout: 180
  parallelizable: false

prompts:
  system_prompt: |
    You are an expert web researcher. Find and verify information across multiple sources.
  task_prompt: |
    Research the query and verify findings across multiple sources.
```

## API OpenAPI Specification

See `/api/v1/openapi.json` for complete OpenAPI 3.1 specification of all endpoints.

## Configuration

Skills system can be configured via:

1. **Environment Variables**
   - `SKILLS_ENABLED`: Enable/disable skills system
   - `MAX_CONCURRENT_EXECUTIONS`: Max parallel executions
   - `DEFAULT_TIMEOUT`: Default timeout in seconds
   - `ENABLE_METRICS`: Enable metrics collection

2. **API Configuration**
   - Update via `/api/v1/skills/config` endpoint

3. **Database Configuration**
   - PostgreSQL or SQLite based on environment
   - Redis for caching and metrics

## Testing

Skills system includes:

1. **Unit Tests**
   - Parser tests
   - Validator tests
   - Execution engine tests

2. **Integration Tests**
   - REST API tests
   - MCP tools tests
   - Database tests

3. **Skill Tests**
   - Test each skill execution
   - Test skill chaining
   - Test parallel execution
   - Test error recovery

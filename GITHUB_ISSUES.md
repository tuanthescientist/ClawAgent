# GitHub Issues - ClawAgent Roadmap

**How to use**: Copy each issue template and create in GitHub Issues.

---

## Phase 1: Zalo OA Integration (PRIORITY 1)

### Issue 1.1: Implement Zalo OA Webhook Integration
```markdown
## Title: Feat: Add Zalo OA Webhook Integration

### Description
Implement complete Zalo OA integration to support messaging through Official Account.

### Details
- Create `src/integrations/zalo.py`
- Implement webhook receiver for `/api/v1/zalo/webhook`
- Handle event types: user_send_text, user_send_image, attachment
- Signature verification (X-ZALO-SIGNATURE header)
- Message parsing to platform-agnostic format
- Async message processing with logging

### Technical Requirements
- Zalo webhook documentation: https://developers.zalo.me/
- Support event types from Zalo API v3
- Rate limit: 10 requests/sec
- Signature verification using HMAC-SHA256

### Acceptance Criteria
- [ ] Webhook receives messages from Zalo
- [ ] All event types parsed correctly
- [ ] Signature validation passes
- [ ] Messages logged with platform=zalo
- [ ] Unit tests passing (100% coverage)
- [ ] Integration test with Zalo mock

### Subtasks
1. [ ] Create ZaloOAIntegration class
2. [ ] Implement webhook handler
3. [ ] Add signature verification
4. [ ] Event parsing logic
5. [ ] Error handling & logging
6. [ ] Write tests

### Labels
zalo, integration, critical

### Milestone
v2.1 - Zalo OA Support

### Estimated Effort
3-4 days
```

### Issue 1.2: Implement Zalo Message Sending
```markdown
## Title: Feat: Add Zalo Message Sending Capability

### Description
Implement sending messages through Zalo OA to users.

### Details
- Send text messages
- Send rich messages (template format)
- Send images & attachments
- Send quick reply buttons
- Send carousels
- Async delivery with retry logic

### Technical Requirements
- Use Zalo SendMessage API
- Support all message types
- Implement exponential backoff retry (3 attempts)
- Cache user info locally

### Acceptance Criteria
- [ ] Text messages send & deliver
- [ ] Template messages support
- [ ] Image attachments work
- [ ] Quick reply buttons interactive
- [ ] Retry on failure (3x)
- [ ] Tests passing

### Labels
zalo, integration

### Milestone
v2.1

### Estimated Effort
2 days
```

### Issue 1.3: Create Zalo Setup Documentation
```markdown
## Title: Docs: Complete Zalo OA Setup Guide

### Description
Create comprehensive documentation for setting up Zalo OA integration.

### Details
Create file: `ZALO_SETUP.md`
- Create Zalo Developer Account
- Create Business App
- Get API credentials
- Configure webhook
- Testing with Zalo API Tester
- Troubleshooting section
- Real examples with code

### Acceptance Criteria
- [ ] New users can setup in 15 minutes
- [ ] All credential types explained
- [ ] Webhook URL configuration clear
- [ ] Common issues addressed
- [ ] Screenshots where helpful

### Labels
documentation, zalo

### Milestone
v2.1

### Estimated Effort
1 day
```

---

## Phase 2: Local LLM + Hybrid Backend (PRIORITY 2)

### Issue 2.1: Refactor LLM to Provider Architecture
```markdown
## Title: Refactor: Create LLMProvider Abstract Architecture

### Description
Refactor LLM system to support multiple providers (OpenAI, Ollama, vLLM, LM Studio).

### Details
- Create `src/llm/llm_provider.py` with LLMProvider base class
- Methods: get_response(), get_streaming(), embed(), health_check()
- Implement providers:
  - OpenAIProvider (refactor existing)
  - OllamaProvider (new)
  - vLLMProvider (new - OpenAI compatible)
  - LMStudioProvider (new - OpenAI compatible)
- Configuration management

### Technical Requirements
- Abstract base class with ~5 methods
- Provider auto-detection
- Consistent response format
- Error handling per provider

### Acceptance Criteria
- [ ] All providers implement interface
- [ ] Response format consistent
- [ ] Configuration loading works
- [ ] Unit tests for each provider
- [ ] Integration tests passing

### Labels
refactor, llm, local-llm

### Milestone
v2.1

### Estimated Effort
3 days
```

### Issue 2.2: Implement Hybrid LLM Controller with Fallback
```markdown
## Title: Feat: Add Hybrid LLM with Fallback System

### Description
Create HybridLLMController that tries local LLM first, falls back to cloud on timeout/error.

### Details
- HybridLLMController class
- Config: LLM_BACKEND=hybrid
- Local timeout: configurable (default 30s)
- Fallback to OpenAI on timeout
- Fallback on error
- Response caching for similar queries
- Health check loop (every 60s)
- Log provider + latency

### Technical Requirements
- Timeout handling
- Health check circuit breaker
- Cache key generation (hash of prompt)
- Logging provider usage
- User feedback on provider used

### Acceptance Criteria
- [ ] Local LLM responds when available
- [ ] Auto-fallback on timeout >threshold
- [ ] User informed of provider (#provider_used)
- [ ] Latency logged
- [ ] Tests (unit + integration)
- [ ] Config validation

### Labels
llm, local-llm, feature

### Milestone
v2.1

### Estimated Effort
2-3 days
```

### Issue 2.3: Add Docker Compose Ollama Support
```markdown
## Title: DevOps: Add Ollama Container to docker-compose.yml

### Description
Add Ollama service to docker-compose with GPU support.

### Details
- New service: ollama
- GPU support (NVIDIA)
- Model auto-pull on startup
- Health check
- Resource limits (CPU, memory)
- Volume mount for models persistence
- Network: internal + ClawAgent

### Technical Requirements
- NVIDIA GPU support (optional)
- Models: mistral, llama2
- Health endpoint: http://ollama:11434/api/tags

### Acceptance Criteria
- [ ] docker-compose up starts Ollama
- [ ] GPU recognized (if available)
- [ ] Models auto-pulled
- [ ] Health check passing
- [ ] ClawAgent connects to Ollama
- [ ] Documentation updated

### Labels
devops, docker, local-llm

### Milestone
v2.1

### Estimated Effort
1 day
```

### Issue 2.4: Local LLM Documentation
```markdown
## Title: Docs: Complete Local LLM Guide

### Description
Create comprehensive guide for setting up and using local LLMs.

### Details
Create file: `LOCAL_LLM_GUIDE.md`
- Why use local LLM?
- Ollama installation & models
- vLLM setup
- LM Studio guide
- Performance tuning
- Cost analysis
- Troubleshooting
- Benchmarks: latency comparison

### Acceptance Criteria
- [ ] Each provider covered
- [ ] Setup instructions clear
- [ ] Performance tips included
- [ ] Troubleshooting comprehensive

### Labels
documentation, local-llm

### Milestone
v2.1

### Estimated Effort
1 day
```

---

## Phase 3: Documentation & Release (PRIORITY 3)

### Issue 3.1: Rewrite README.md
```markdown
## Title: Docs: Rewrite README.md with Better Visibility

### Description
Rewrite README.md for better community visibility and adoption.

### Details
New structure:
1. Eye-catching header + badges
2. 30-second demo (GIF) - chat interaction
3. Feature comparison table
4. Features matrix (WhatsApp, Zalo, Local LLM)
5. Quick start (WhatsApp + Zalo)
6. Architecture diagram
7. Benchmarks & performance
8. Contributing & roadmap links
9. Author & license

### Badges Needed
- Python 3.10+
- FastAPI
- Local LLM Ready
- Zalo OA
- WhatsApp
- MIT License
- GitHub stars

### Acceptance Criteria
- [ ] README is engaging & clear
- [ ] All features visible
- [ ] Setup quick & easy
- [ ] Links to guides working
- [ ] Badges displaying

### Labels
documentation, readme

### Milestone
v2.1

### Estimated Effort
1 day
```

### Issue 3.2: Create Architecture Documentation
```markdown
## Title: Docs: Add ARCHITECTURE.md

### Description
Create detailed architecture documentation.

### Content
- System design diagram
- Component interactions
- Data flow
- Deployment architecture
- Caching strategy
- Error handling flow
- ReAct reasoning flow

### Acceptance Criteria
- [ ] Diagram clear & comprehensive
- [ ] All components explained
- [ ] Data flows documented

### Labels
documentation, architecture

### Milestone
v2.1

### Estimated Effort
1 day
```

### Issue 3.3: Create Release v2.1
```markdown
## Title: Release: ClawAgent v2.1 - Zalo OA & Local LLM

### Description
Create and publish v2.1 release.

### Tasks
- [ ] Update version numbers
- [ ] Create CHANGELOG entry
- [ ] Create GitHub Release
- [ ] Tag commit as v2.1.0
- [ ] Write release notes
- [ ] Link to key docs

### Release Notes Template
**🎉 Major Features**
- ✨ Zalo OA integration complete
- 🌍 Local LLM support (Ollama, vLLM)
- 🔄 Hybrid fallback system
- 📊 Vector memory upgrade (ChromaDB ready)

**📚 Documentation**
- Complete Zalo setup guide
- Local LLM guide
- Architecture documentation

**🔧 Technical**
- Rate limiting prepared
- Monitoring foundation added
- Docker GPU support

### Labels
release

### Milestone
v2.1

### Estimated Effort
0.5 day
```

---

## Phase 4: Memory & Tools Upgrade (PRIORITY 4)

### Issue 4.1: Migrate to ChromaDB Vector Memory
```markdown
## Title: Feat: Upgrade Vector Memory to ChromaDB

### Description
Replace in-memory vector memory with persistent ChromaDB.

### Details
- Install ChromaDB
- Create collection per user/platform
- Metadata filtering: user_id, platform, time
- Multi-user isolation
- Backup strategy
- Performance optimization

### Acceptance Criteria
- [ ] Memory persists across restarts
- [ ] User isolation verified
- [ ] Queries filtered by user_id
- [ ] Performance acceptable (<100ms)
- [ ] Tests passing

### Labels
memory, database, feature

### Milestone
v2.2

### Estimated Effort
2 days
```

### Issue 4.2: Expand Tool Suite
```markdown
## Title: Feat: Add Browser, Database, Image Tools

### Description
Add new tools: browser, database, image generation.

### Details
- BrowserTool (Playwright):
  - Web scraping
  - Screenshots
  - Form filling

- DatabaseTool:
  - Query SQLite/PostgreSQL
  - Safe SQL execution

- ImageGenerationTool:
  - Local Flux/Stable Diffusion
  - Prompt safety

### Acceptance Criteria
- [ ] All tools implemented
- [ ] Error handling robust
- [ ] Tests comprehensive
- [ ] Documentation clear

### Labels
tools, feature

### Milestone
v2.2

### Estimated Effort
3 days
```

---

## Phase 5: Production Hardening (PRIORITY 5)

### Issue 5.1: Implement Rate Limiting
```markdown
## Title: Feat: Add Rate Limiting & Throttling

### Description
Implement per-user and per-API rate limiting.

### Details
- Per-user message rate limit
- Per-API call limits
- Platform-aware limiting
- Configuration via .env
- Graceful degradation

### Config Example
```yaml
RATE_LIMITS:
  USER_MESSAGE_PER_MINUTE: 60
  USER_API_CALLS_PER_HOUR: 1000
  ZALO_API_PER_SECOND: 10
```

### Acceptance Criteria
- [ ] Rate limits enforced
- [ ] Configuration working
- [ ] User notifications clear
- [ ] Logging detailed

### Labels
production, performance, reliability

### Milestone
v2.2

### Estimated Effort
2 days
```

### Issue 5.2: Add Retry & Circuit Breaker
```markdown
## Title: Feat: Implement Retry & Circuit Breaker

### Description
Add resilience patterns for external API calls.

### Details
- Exponential backoff retry (3 attempts)
- Circuit breaker for Zalo/OpenAI
- Fallback strategies
- Health check endpoints

### Acceptance Criteria
- [ ] Retry working for Zalo API
- [ ] Circuit breaker prevents cascading failures
- [ ] Fallback works (Zalo→OpenAI)
- [ ] Tests passing

### Labels
production, reliability

### Milestone
v2.2

### Estimated Effort
1-2 days
```

### Issue 5.3: Security Hardening
```markdown
## Title: Security: Harden Webhook & API Security

### Description
Enhance security: input sanitization, signature validation, key management.

### Details
- Input sanitization (SQL/XSS prevention)
- Enhanced signature validation
- Secret key management
- HTTPS enforcement
- User data isolation

### Acceptance Criteria
- [ ] Security audit passed
- [ ] No vulnerabilities found
- [ ] Tests cover edge cases
- [ ] Documentation updated

### Labels
security, production

### Milestone
v2.2

### Estimated Effort
2 days
```

### Issue 5.4: Add Monitoring & Observability
```markdown
## Title: Ops: Add Prometheus Metrics & Logging

### Description
Implement production monitoring with Prometheus & structured logging.

### Details
- Prometheus metrics
- Structured logging (JSON)
- Alert rules
- Dashboard template (Grafana)

### Metrics
```
clawagent_requests_total
clawagent_response_latency
clawagent_errors_total
clawagent_tool_execution_duration
```

### Acceptance Criteria
- [ ] Metrics exposed on /metrics
- [ ] Logging structured & centralized
- [ ] Alerts defined
- [ ] Grafana dashboard template included

### Labels
ops, monitoring

### Milestone
v2.2

### Estimated Effort
2 days
```

### Issue 5.5: CI/CD Pipeline Setup
```markdown
## Title: DevOps: Setup GitHub Actions CI/CD

### Description
Implement automated testing, building, and deployment.

### Details
- Unit tests on push
- Integration tests
- Docker build
- Docker push to registry
- Deploy to staging
- Code coverage reporting

### Workflow
```
push → lint → test → build → push → deploy-staging
```

### Acceptance Criteria
- [ ] Workflow passing
- [ ] Coverage >80%
- [ ] Docker image builds
- [ ] Staging deployment automated

### Labels
devops, ci-cd

### Milestone
v2.2

### Estimated Effort
1-2 days
```

---

## Summary: Total Issues

| Phase | Issue Count | Effort |
|-------|------------|--------|
| Phase 1 | 3 | 5-7 days |
| Phase 2 | 4 | 6-8 days |
| Phase 3 | 3 | 2-3 days |
| Phase 4 | 2 | 5 days |
| Phase 5 | 5 | 8-10 days |
| **TOTAL** | **17** | **26-33 days** |

---

## How to Create Issues

1. Go to GitHub: https://github.com/tuanthescientist/ClawAgent/issues/new
2. Use the templates above
3. Assign to team members
4. Add to Milestone (v2.1 or v2.2)
5. Add labels
6. Link in ROADMAP.md

---

## Issue Tracking Kanban

Use GitHub Project to organize:
- **Backlog**: All issues
- **Ready**: Approved & prioritized
- **In Progress**: Currently being worked on
- **Review**: Code/docs in review
- **Done**: Completed & merged


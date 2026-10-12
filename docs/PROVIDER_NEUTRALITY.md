# Provider Neutrality

ARCHITECT is intentionally independent of model vendors and hosting platforms.

## Core boundary

The recommendation engine receives architecture facts and returns architecture decisions. It does not send prompts to an external model.

```text
ArchitectureCase -> deterministic rules -> Recommendation -> DecisionPlan
```

No API key, provider SDK or hosted model is required.

## What is vendor-specific?

Only an optional runtime/reviewer layer should know about a concrete provider.

Examples of provider-specific concerns that belong behind an adapter:

- authentication credentials;
- model identifiers;
- request/response payloads;
- tool-calling schema differences;
- structured-output features;
- token accounting;
- retry/rate-limit behavior;
- provider-specific telemetry.

## Adapter principle

Future model-assisted features should depend on a small generic contract, for example:

```python
from typing import Protocol

class ModelAdapter(Protocol):
    def generate(self, system: str, user: str) -> str: ...
```

Concrete adapters can then implement any provider or local runtime without changing the ARCHITECT engine.

## Tool integration is also provider-neutral

The framework distinguishes the architecture problem from a concrete transport:

- existing API/tool;
- protocol-based tool discovery (for example MCP-compatible tooling);
- agent-to-agent interaction;
- direct deterministic service integration.

A protocol is selected because it solves a capability/discovery/interoperability requirement, not because of the model vendor.

## Portability rule

If replacing one model/provider requires rewriting authorization, business rules or transaction controls, those responsibilities are probably located in the wrong layer.

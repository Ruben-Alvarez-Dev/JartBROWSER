"""
Workflow Builder Service

Provides visual workflow creation, execution, and management.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import json


class NodeType(Enum):
    """Workflow node types"""

    TRIGGER = "trigger"
    ACTION = "action"
    CONDITION = "condition"
    LOOP = "loop"
    WAIT = "wait"
    TRANSFORM = "transform"
    LLM = "llm"
    OUTPUT = "output"


class TriggerType(Enum):
    """Trigger types"""

    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT = "event"
    WEBHOOK = "webhook"


class EdgeType(Enum):
    """Edge types"""

    SUCCESS = "success"
    FAILURE = "failure"
    DEFAULT = "default"


@dataclass
class WorkflowNode:
    """Workflow node"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: NodeType = NodeType.ACTION
    label: str = ""
    description: str = ""
    config: Dict[str, Any] = field(default_factory=dict)
    position: Dict[str, int] = field(default_factory=lambda: {"x": 0, "y": 0})
    next_nodes: List[str] = field(default_factory=list)


@dataclass
class WorkflowEdge:
    """Workflow edge (connection)"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str = ""
    target_id: str = ""
    edge_type: EdgeType = EdgeType.DEFAULT
    label: str = ""
    condition: Optional[str] = None


@dataclass
class WorkflowExecution:
    """Workflow execution"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str = ""
    status: str = "pending"  # pending, running, completed, failed, cancelled
    current_node_id: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Workflow:
    """Workflow definition"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    nodes: List[WorkflowNode] = field(default_factory=list)
    edges: List[WorkflowEdge] = field(default_factory=list)
    trigger_type: TriggerType = TriggerType.MANUAL
    trigger_config: Dict[str, Any] = field(default_factory=dict)
    is_template: bool = False
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "nodes": [
                {
                    "id": n.id,
                    "type": n.type.value,
                    "label": n.label,
                    "description": n.description,
                    "config": n.config,
                    "position": n.position,
                    "next_nodes": n.next_nodes,
                }
                for n in self.nodes
            ],
            "edges": [
                {
                    "id": e.id,
                    "source_id": e.source_id,
                    "target_id": e.target_id,
                    "edge_type": e.edge_type.value,
                    "label": e.label,
                    "condition": e.condition,
                }
                for e in self.edges
            ],
            "trigger_type": self.trigger_type.value,
            "trigger_config": self.trigger_config,
            "is_template": self.is_template,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class WorkflowBuilderService:
    """
    Service for building and executing visual workflows.

    Provides:
    - Workflow creation and management
    - Node and edge management
    - Workflow execution
    - Templates
    """

    def __init__(self):
        self._workflows: Dict[str, Workflow] = {}
        self._executions: Dict[str, WorkflowExecution] = {}
        self._node_handlers: Dict[NodeType, Callable] = {}
        self._register_default_handlers()

    def _register_default_handlers(self) -> None:
        """Register default node handlers"""
        # Handlers would be registered for each node type
        pass

    # ============== Workflow CRUD ==============

    def create_workflow(
        self,
        name: str,
        description: str = "",
        trigger_type: TriggerType = TriggerType.MANUAL,
        trigger_config: Optional[Dict[str, Any]] = None,
    ) -> Workflow:
        """Create a new workflow"""
        workflow = Workflow(
            name=name,
            description=description,
            trigger_type=trigger_type,
            trigger_config=trigger_config or {},
        )

        self._workflows[workflow.id] = workflow
        return workflow

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get a workflow"""
        return self._workflows.get(workflow_id)

    def get_workflows(
        self, template_only: bool = False, active_only: bool = False, limit: int = 50
    ) -> List[Workflow]:
        """Get workflows"""
        results = list(self._workflows.values())

        if template_only:
            results = [w for w in results if w.is_template]
        if active_only:
            results = [w for w in results if w.is_active]

        results.sort(key=lambda w: w.updated_at, reverse=True)
        return results[:limit]

    def update_workflow(
        self,
        workflow_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[Workflow]:
        """Update workflow"""
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            return None

        if name is not None:
            workflow.name = name
        if description is not None:
            workflow.description = description
        if is_active is not None:
            workflow.is_active = is_active

        workflow.updated_at = datetime.utcnow()
        return workflow

    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow"""
        if workflow_id in self._workflows:
            del self._workflows[workflow_id]
            return True
        return False

    # ============== Nodes ==============

    def add_node(
        self,
        workflow_id: str,
        node_type: NodeType,
        label: str,
        config: Optional[Dict[str, Any]] = None,
        position: Optional[Dict[str, int]] = None,
    ) -> Optional[WorkflowNode]:
        """Add a node to workflow"""
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            return None

        node = WorkflowNode(
            type=node_type, label=label, config=config or {}, position=position or {"x": 0, "y": 0}
        )

        workflow.nodes.append(node)
        workflow.updated_at = datetime.utcnow()
        return node

    def update_node(
        self,
        workflow_id: str,
        node_id: str,
        label: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        position: Optional[Dict[str, int]] = None,
    ) -> Optional[WorkflowNode]:
        """Update a node"""
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            return None

        node = next((n for n in workflow.nodes if n.id == node_id), None)
        if not node:
            return None

        if label is not None:
            node.label = label
        if config is not None:
            node.config = config
        if position is not None:
            node.position = position

        workflow.updated_at = datetime.utcnow()
        return node

    def remove_node(self, workflow_id: str, node_id: str) -> bool:
        """Remove a node"""
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            return False

        workflow.nodes = [n for n in workflow.nodes if n.id != node_id]

        # Also remove edges connected to this node
        workflow.edges = [
            e for e in workflow.edges if e.source_id != node_id and e.target_id != node_id
        ]

        workflow.updated_at = datetime.utcnow()
        return True

    def get_node(self, workflow_id: str, node_id: str) -> Optional[WorkflowNode]:
        """Get a node"""
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            return None

        return next((n for n in workflow.nodes if n.id == node_id), None)

    # ============== Edges ==============

    def add_edge(
        self,
        workflow_id: str,
        source_id: str,
        target_id: str,
        edge_type: EdgeType = EdgeType.DEFAULT,
        label: str = "",
        condition: Optional[str] = None,
    ) -> Optional[WorkflowEdge]:
        """Add an edge between nodes"""
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            return None

        # Verify nodes exist
        source = next((n for n in workflow.nodes if n.id == source_id), None)
        target = next((n for n in workflow.nodes if n.id == target_id), None)

        if not source or not target:
            return None

        edge = WorkflowEdge(
            source_id=source_id,
            target_id=target_id,
            edge_type=edge_type,
            label=label,
            condition=condition,
        )

        workflow.edges.append(edge)

        # Update source node's next_nodes
        source.next_nodes.append(target_id)

        workflow.updated_at = datetime.utcnow()
        return edge

    def remove_edge(self, workflow_id: str, edge_id: str) -> bool:
        """Remove an edge"""
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            return False

        edge = next((e for e in workflow.edges if e.id == edge_id), None)
        if not edge:
            return False

        # Remove from source node's next_nodes
        source = next((n for n in workflow.nodes if n.id == edge.source_id), None)
        if source and edge.target_id in source.next_nodes:
            source.next_nodes.remove(edge.target_id)

        workflow.edges = [e for e in workflow.edges if e.id != edge_id]
        workflow.updated_at = datetime.utcnow()
        return True

    # ============== Execution ==============

    async def execute(
        self, workflow_id: str, context: Optional[Dict[str, Any]] = None
    ) -> Optional[WorkflowExecution]:
        """Execute a workflow"""
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            return None

        execution = WorkflowExecution(
            workflow_id=workflow_id,
            context=context or {},
            status="running",
            started_at=datetime.utcnow(),
        )

        self._executions[execution.id] = execution

        try:
            # Find trigger node
            trigger_node = next((n for n in workflow.nodes if n.type == NodeType.TRIGGER), None)

            if not trigger_node:
                execution.status = "failed"
                execution.errors.append({"error": "No trigger node found"})
                return execution

            # Execute nodes in order
            current_node_id = trigger_node.id

            while current_node_id:
                execution.current_node_id = current_node_id

                node = next((n for n in workflow.nodes if n.id == current_node_id), None)

                if not node:
                    break

                # Execute node
                result = await self._execute_node(node, execution)

                if not result.get("success", False):
                    execution.errors.append(
                        {"node_id": current_node_id, "error": result.get("error", "Unknown error")}
                    )

                    # Find failure edge
                    failure_edge = next(
                        (
                            e
                            for e in workflow.edges
                            if e.source_id == current_node_id and e.edge_type == EdgeType.FAILURE
                        ),
                        None,
                    )

                    if failure_edge:
                        current_node_id = failure_edge.target_id
                    else:
                        execution.status = "failed"
                        break

                execution.results[current_node_id] = result

                # Find next node
                success_edge = next(
                    (
                        e
                        for e in workflow.edges
                        if e.source_id == current_node_id and e.edge_type == EdgeType.SUCCESS
                    ),
                    None,
                )

                if success_edge:
                    current_node_id = success_edge.target_id
                else:
                    current_node_id = None

            if execution.status == "running":
                execution.status = "completed"

        except Exception as e:
            execution.status = "failed"
            execution.errors.append({"error": str(e)})

        execution.completed_at = datetime.utcnow()
        return execution

    async def _execute_node(
        self, node: WorkflowNode, execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Execute a single node"""
        try:
            if node.type == NodeType.ACTION:
                return await self._execute_action(node, execution)
            elif node.type == NodeType.LLM:
                return await self._execute_llm(node, execution)
            elif node.type == NodeType.CONDITION:
                return await self._execute_condition(node, execution)
            elif node.type == NodeType.WAIT:
                return await self._execute_wait(node, execution)
            elif node.type == NodeType.TRANSFORM:
                return await self._execute_transform(node, execution)
            else:
                return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _execute_action(
        self, node: WorkflowNode, execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Execute action node"""
        action_type = node.config.get("type", "unknown")

        # In production, would execute actual action
        return {"success": True, "action": action_type, "result": {}}

    async def _execute_llm(
        self, node: WorkflowNode, execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Execute LLM node"""
        prompt = node.config.get("prompt", "")
        model = node.config.get("model", "gpt-4o")

        # In production, would call LLM service
        return {"success": True, "model": model, "response": "LLM response placeholder"}

    async def _execute_condition(
        self, node: WorkflowNode, execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Execute condition node"""
        condition = node.config.get("condition", "true")

        # In production, would evaluate condition
        return {"success": True, "result": True}

    async def _execute_wait(
        self, node: WorkflowNode, execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Execute wait node"""
        duration = node.config.get("duration", 1)  # seconds

        import asyncio

        await asyncio.sleep(duration)

        return {"success": True}

    async def _execute_transform(
        self, node: WorkflowNode, execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Execute transform node"""
        transform_type = node.config.get("type", "identity")

        return {"success": True, "transformed": True}

    def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get execution"""
        return self._executions.get(execution_id)

    def get_executions(
        self, workflow_id: Optional[str] = None, status: Optional[str] = None, limit: int = 20
    ) -> List[WorkflowExecution]:
        """Get executions"""
        results = list(self._executions.values())

        if workflow_id:
            results = [e for e in results if e.workflow_id == workflow_id]
        if status:
            results = [e for e in results if e.status == status]

        results.sort(key=lambda e: e.created_at, reverse=True)
        return results[:limit]

    # ============== Templates ==============

    def save_as_template(self, workflow_id: str) -> Optional[Workflow]:
        """Save workflow as template"""
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            return None

        template = Workflow(
            name=f"{workflow.name} (Template)",
            description=workflow.description,
            nodes=workflow.nodes.copy(),
            edges=workflow.edges.copy(),
            trigger_type=workflow.trigger_type,
            trigger_config=workflow.trigger_config.copy(),
            is_template=True,
        )

        self._workflows[template.id] = template
        return template

    def get_templates(self) -> List[Workflow]:
        """Get all templates"""
        return self.get_workflows(template_only=True)

    # ============== Import/Export ==============

    def export_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Export workflow as JSON"""
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            return None

        return workflow.to_dict()

    def import_workflow(self, data: Dict[str, Any]) -> Workflow:
        """Import workflow from JSON"""
        workflow = Workflow(
            name=data.get("name", "Imported Workflow"),
            description=data.get("description", ""),
            is_template=data.get("is_template", False),
        )

        # Import nodes and edges
        # In production, would properly reconstruct nodes

        self._workflows[workflow.id] = workflow
        return workflow


# Singleton
_workflow_service: Optional[WorkflowBuilderService] = None


def get_workflow_service() -> WorkflowBuilderService:
    """Get the workflow builder service instance"""
    global _workflow_service
    if _workflow_service is None:
        _workflow_service = WorkflowBuilderService()
    return _workflow_service

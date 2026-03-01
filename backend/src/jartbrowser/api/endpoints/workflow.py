"""Workflow API endpoints"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from jartbrowser.services.workflow import (
    WorkflowBuilderService,
    NodeType,
    TriggerType,
    EdgeType,
    get_workflow_service,
)


router = APIRouter()

workflow_service: WorkflowBuilderService = get_workflow_service()


class NodeCreate(BaseModel):
    type: NodeType
    label: str
    config: Optional[Dict[str, Any]] = None
    position: Optional[Dict[str, int]] = None


class EdgeCreate(BaseModel):
    source_id: str
    target_id: str
    edge_type: Optional[EdgeType] = EdgeType.DEFAULT
    label: Optional[str] = None
    condition: Optional[str] = None


class WorkflowCreate(BaseModel):
    name: str
    description: str = ""
    trigger_type: Optional[TriggerType] = TriggerType.MANUAL
    trigger_config: Optional[Dict[str, Any]] = None


class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ExecutionRequest(BaseModel):
    context: Optional[Dict[str, Any]] = None


@router.post("/workflows", status_code=status.HTTP_201_CREATED)
async def create_workflow(payload: WorkflowCreate):
    """Create a new workflow"""
    workflow = workflow_service.create_workflow(
        name=payload.name,
        description=payload.description,
        trigger_type=payload.trigger_type,
        trigger_config=payload.trigger_config,
    )
    return workflow.to_dict()


@router.get("/workflows")
async def list_workflows(
    template_only: bool = False,
    active_only: bool = False,
    limit: int = 50,
):
    """List workflows"""
    workflows = workflow_service.get_workflows(
        template_only=template_only,
        active_only=active_only,
        limit=limit,
    )
    return [w.to_dict() for w in workflows]


@router.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Get a workflow"""
    workflow = workflow_service.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow.to_dict()


@router.put("/workflows/{workflow_id}")
async def update_workflow(workflow_id: str, payload: WorkflowUpdate):
    """Update a workflow"""
    workflow = workflow_service.update_workflow(
        workflow_id,
        name=payload.name,
        description=payload.description,
        is_active=payload.is_active,
    )
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow.to_dict()


@router.delete("/workflows/{workflow_id}")
async def delete_workflow(workflow_id: str):
    """Delete a workflow"""
    if not workflow_service.delete_workflow(workflow_id):
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"status": "deleted"}


@router.post("/workflows/{workflow_id}/nodes")
async def add_node(workflow_id: str, payload: NodeCreate):
    """Add a node to workflow"""
    node = workflow_service.add_node(
        workflow_id=workflow_id,
        node_type=payload.type,
        label=payload.label,
        config=payload.config,
        position=payload.position,
    )
    if not node:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"id": node.id, "type": node.type.value, "label": node.label}


@router.delete("/workflows/{workflow_id}/nodes/{node_id}")
async def remove_node(workflow_id: str, node_id: str):
    """Remove a node"""
    if not workflow_service.remove_node(workflow_id, node_id):
        raise HTTPException(status_code=404, detail="Workflow or node not found")
    return {"status": "deleted"}


@router.post("/workflows/{workflow_id}/edges")
async def add_edge(workflow_id: str, payload: EdgeCreate):
    """Add an edge"""
    edge = workflow_service.add_edge(
        workflow_id=workflow_id,
        source_id=payload.source_id,
        target_id=payload.target_id,
        edge_type=payload.edge_type,
        label=payload.label,
        condition=payload.condition,
    )
    if not edge:
        raise HTTPException(status_code=404, detail="Workflow or nodes not found")
    return {"id": edge.id, "source": edge.source_id, "target": edge.target_id}


@router.delete("/workflows/{workflow_id}/edges/{edge_id}")
async def remove_edge(workflow_id: str, edge_id: str):
    """Remove an edge"""
    if not workflow_service.remove_edge(workflow_id, edge_id):
        raise HTTPException(status_code=404, detail="Workflow or edge not found")
    return {"status": "deleted"}


@router.post("/workflows/{workflow_id}/execute")
async def execute_workflow(workflow_id: str, payload: Optional[ExecutionRequest] = None):
    """Execute a workflow"""
    context = payload.context if payload else None
    execution = await workflow_service.execute(workflow_id, context)
    if not execution:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {
        "id": execution.id,
        "workflow_id": execution.workflow_id,
        "status": execution.status,
        "current_node_id": execution.current_node_id,
        "results": execution.results,
        "errors": execution.errors,
    }


@router.get("/executions/{execution_id}")
async def get_execution(execution_id: str):
    """Get execution"""
    execution = workflow_service.get_execution(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return {
        "id": execution.id,
        "workflow_id": execution.workflow_id,
        "status": execution.status,
        "current_node_id": execution.current_node_id,
        "context": execution.context,
        "results": execution.results,
        "errors": execution.errors,
    }


@router.get("/workflows/{workflow_id}/executions")
async def list_executions(workflow_id: str, status: Optional[str] = None, limit: int = 20):
    """List workflow executions"""
    executions = workflow_service.get_executions(
        workflow_id=workflow_id, status=status, limit=limit
    )
    return [
        {
            "id": e.id,
            "workflow_id": e.workflow_id,
            "status": e.status,
            "current_node_id": e.current_node_id,
            "started_at": e.started_at.isoformat() if e.started_at else None,
            "completed_at": e.completed_at.isoformat() if e.completed_at else None,
        }
        for e in executions
    ]


@router.post("/workflows/{workflow_id}/template")
async def save_as_template(workflow_id: str):
    """Save workflow as template"""
    template = workflow_service.save_as_template(workflow_id)
    if not template:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return template.to_dict()


@router.get("/templates")
async def list_templates():
    """List workflow templates"""
    templates = workflow_service.get_templates()
    return [t.to_dict() for t in templates]


@router.get("/workflows/{workflow_id}/export")
async def export_workflow(workflow_id: str):
    """Export workflow as JSON"""
    data = workflow_service.export_workflow(workflow_id)
    if not data:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return data


@router.post("/workflows/import")
async def import_workflow(data: Dict[str, Any]):
    """Import workflow from JSON"""
    workflow = workflow_service.import_workflow(data)
    return workflow.to_dict()

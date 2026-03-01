"""Tests for WorkflowBuilderService"""

import pytest
from jartbrowser.services.workflow import (
    WorkflowBuilderService,
    NodeType,
    TriggerType,
    EdgeType,
)


@pytest.fixture
def workflow_service():
    return WorkflowBuilderService()


def test_create_workflow(workflow_service):
    """Test workflow creation"""
    workflow = workflow_service.create_workflow(
        name="Test Workflow",
        description="A test workflow",
    )
    assert workflow.name == "Test Workflow"
    assert workflow.description == "A test workflow"
    assert workflow.id is not None


def test_get_workflow(workflow_service):
    """Test getting a workflow"""
    created = workflow_service.create_workflow(name="Get Test")
    retrieved = workflow_service.get_workflow(created.id)
    assert retrieved is not None
    assert retrieved.id == created.id


def test_get_workflows(workflow_service):
    """Test listing workflows"""
    workflow_service.create_workflow(name="Workflow 1")
    workflow_service.create_workflow(name="Workflow 2")
    workflows = workflow_service.get_workflows()
    assert len(workflows) >= 2


def test_add_node(workflow_service):
    """Test adding a node"""
    workflow = workflow_service.create_workflow(name="Node Test")
    node = workflow_service.add_node(
        workflow_id=workflow.id,
        node_type=NodeType.ACTION,
        label="Test Action",
        config={"type": "click"},
    )
    assert node is not None
    assert node.label == "Test Action"


def test_add_edge(workflow_service):
    """Test adding an edge"""
    workflow = workflow_service.create_workflow(name="Edge Test")
    node1 = workflow_service.add_node(workflow.id, NodeType.TRIGGER, "Start")
    node2 = workflow_service.add_node(workflow.id, NodeType.ACTION, "Action")

    edge = workflow_service.add_edge(
        workflow_id=workflow.id,
        source_id=node1.id,
        target_id=node2.id,
        edge_type=EdgeType.SUCCESS,
    )
    assert edge is not None
    assert edge.source_id == node1.id
    assert edge.target_id == node2.id


def test_update_workflow(workflow_service):
    """Test updating workflow"""
    workflow = workflow_service.create_workflow(name="Original")
    updated = workflow_service.update_workflow(workflow.id, name="Updated")
    assert updated.name == "Updated"


def test_delete_workflow(workflow_service):
    """Test deleting workflow"""
    workflow = workflow_service.create_workflow(name="To Delete")
    workflow_id = workflow.id
    result = workflow_service.delete_workflow(workflow_id)
    assert result is True
    assert workflow_service.get_workflow(workflow_id) is None


@pytest.mark.asyncio
async def test_execute_workflow(workflow_service):
    """Test workflow execution"""
    workflow = workflow_service.create_workflow(name="Execute Test")
    trigger = workflow_service.add_node(workflow.id, NodeType.TRIGGER, "Start")
    action = workflow_service.add_node(workflow.id, NodeType.ACTION, "Do Something")

    workflow_service.add_edge(workflow.id, trigger.id, action.id, EdgeType.SUCCESS)

    execution = await workflow_service.execute(workflow.id)
    assert execution is not None
    assert execution.workflow_id == workflow.id


def test_save_as_template(workflow_service):
    """Test saving as template"""
    workflow = workflow_service.create_workflow(name="Template Source")
    template = workflow_service.save_as_template(workflow.id)
    assert template is not None
    assert template.is_template is True


def test_export_workflow(workflow_service):
    """Test exporting workflow"""
    workflow = workflow_service.create_workflow(name="Export Test")
    exported = workflow_service.export_workflow(workflow.id)
    assert exported is not None
    assert exported["name"] == "Export Test"


def test_import_workflow(workflow_service):
    """Test importing workflow"""
    data = {"name": "Imported", "description": "From JSON"}
    imported = workflow_service.import_workflow(data)
    assert imported.name == "Imported"

"""Tests for ignition-mcp-server."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ignition_mcp_server.parsers import alarms, named_queries, scripts, tags, udts, views
from ignition_mcp_server.project_source import (
    DirectoryProjectSource,
    ZipProjectSource,
    open_project,
)

FIXTURES = Path(__file__).parent / "fixtures"
DIR_PROJECT = FIXTURES / "sample-project"
ZIP_PROJECT = FIXTURES / "sample-project.zip"


@pytest.fixture(autouse=True)
def _clear_cache():
    """Clear the open_project LRU cache between tests."""
    open_project.cache_clear()


# ── Project Source ──────────────────────────────────────────


class TestProjectSource:
    def test_open_directory(self):
        src = open_project(str(DIR_PROJECT))
        assert isinstance(src, DirectoryProjectSource)

    def test_open_zip(self):
        src = open_project(str(ZIP_PROJECT))
        assert isinstance(src, ZipProjectSource)

    def test_project_info_matches(self):
        dir_info = open_project(str(DIR_PROJECT)).project_info()
        zip_info = open_project(str(ZIP_PROJECT)).project_info()
        assert dir_info == zip_info
        assert dir_info["title"] == "Sample Project"

    def test_list_resources_views(self):
        for path in (DIR_PROJECT, ZIP_PROJECT):
            src = open_project(str(path))
            result = src.list_resources("com.inductiveautomation.perspective", "views")
            assert "Overview" in result
            assert "Screens/MotorDetail" in result

    def test_list_resources_scripts(self):
        for path in (DIR_PROJECT, ZIP_PROJECT):
            src = open_project(str(path))
            result = src.list_resources("ignition", "script-python")
            assert "utils" in result
            assert "alarmHandler" in result

    def test_not_found(self):
        with pytest.raises(FileNotFoundError):
            open_project("/nonexistent/path")

    def test_no_project_json(self, tmp_path):
        (tmp_path / "empty").mkdir()
        with pytest.raises(FileNotFoundError):
            open_project(str(tmp_path / "empty"))

    def test_cache_returns_same_instance(self):
        a = open_project(str(DIR_PROJECT))
        b = open_project(str(DIR_PROJECT))
        assert a is b

    def test_zip_context_manager(self):
        with ZipProjectSource(ZIP_PROJECT) as src:
            info = src.project_info()
            assert info["title"] == "Sample Project"


# ── Tags ────────────────────────────────────────────────────


class TestTags:
    @pytest.fixture
    def source(self):
        return open_project(str(DIR_PROJECT))

    def test_root_tags(self, source):
        result = tags.parse_tags(source)
        names = [t["name"] for t in result]
        assert "Conveyors" in names
        assert "SystemClock" in names
        assert "Motor_UDT" in names

    def test_folder_has_child_count(self, source):
        result = tags.parse_tags(source)
        conveyors = next(t for t in result if t["name"] == "Conveyors")
        assert conveyors["tagType"] == "Folder"
        assert conveyors["childCount"] == 2

    def test_path_filter(self, source):
        result = tags.parse_tags(source, "Conveyors/Line1")
        names = [t["name"] for t in result]
        assert "Running" in names
        assert "Speed" in names
        assert "Faulted" in names
        assert len(result) == 3

    def test_path_filter_nonexistent(self, source):
        result = tags.parse_tags(source, "Nonexistent/Path")
        assert result == []

    def test_atomic_tag_fields(self, source):
        result = tags.parse_tags(source, "Conveyors/Line1")
        running = next(t for t in result if t["name"] == "Running")
        assert running["dataType"] == "Boolean"
        assert running["valueSource"] == "opc"

    def test_udt_instance_has_type_id(self, source):
        result = tags.parse_tags(source, "Conveyors")
        instance = next(t for t in result if t["name"] == "Line2_Motor")
        assert instance["typeId"] == "Motor_UDT"

    def test_zip_returns_same(self):
        dir_result = tags.parse_tags(open_project(str(DIR_PROJECT)))
        zip_result = tags.parse_tags(open_project(str(ZIP_PROJECT)))
        assert dir_result == zip_result

    def test_list_tag_providers(self, source):
        result = tags.list_tag_providers(source)
        assert "default" in result
        assert "edge" in result
        assert len(result) == 2

    def test_edge_provider(self, source):
        result = tags.parse_tags(source, provider="edge")
        names = [t["name"] for t in result]
        assert "EdgeTemp" in names

    def test_nonexistent_provider(self, source):
        result = tags.parse_tags(source, provider="nonexistent")
        assert result == []

    def test_zip_list_tag_providers(self):
        source = open_project(str(ZIP_PROJECT))
        result = tags.list_tag_providers(source)
        assert "default" in result
        assert "edge" in result


# ── Views ───────────────────────────────────────────────────


class TestViews:
    @pytest.fixture
    def source(self):
        return open_project(str(DIR_PROJECT))

    def test_list_views(self, source):
        result = views.list_views(source)
        assert "Overview" in result
        assert "Screens/MotorDetail" in result

    def test_get_view_structure(self, source):
        result = views.get_view(source, "Overview")
        assert result["path"] == "Overview"
        root = result["root"]
        assert root["type"] == "ia.container.flex"
        assert len(root["children"]) == 3

    def test_view_bindings(self, source):
        result = views.get_view(source, "Overview")
        children = result["root"]["children"]
        label = children[0]
        assert len(label["bindings"]) == 1
        assert label["bindings"][0]["type"] == "property"

    def test_view_events(self, source):
        result = views.get_view(source, "Overview")
        button = result["root"]["children"][2]
        assert button["eventCount"] == 1

    def test_zip_returns_same(self):
        dir_result = views.list_views(open_project(str(DIR_PROJECT)))
        zip_result = views.list_views(open_project(str(ZIP_PROJECT)))
        assert dir_result == zip_result


# ── Scripts ─────────────────────────────────────────────────


class TestScripts:
    @pytest.fixture
    def source(self):
        return open_project(str(DIR_PROJECT))

    def test_list_scripts(self, source):
        result = scripts.list_scripts(source)
        names = [s["name"] for s in result]
        assert "utils" in names
        assert "alarmHandler" in names

    def test_script_scope(self, source):
        result = scripts.list_scripts(source)
        alarm = next(s for s in result if s["name"] == "alarmHandler")
        assert alarm["scope"] == "gateway"

    def test_get_script_code(self, source):
        result = scripts.get_script(source, "ignition/script-python/utils")
        assert "def format_tag_path" in result["code"]
        assert "def read_motor_status" in result["code"]

    def test_get_gateway_script(self, source):
        result = scripts.get_script(source, "ignition/script-python/alarmHandler")
        assert "def handleAlarm" in result["code"]

    def test_zip_returns_same(self):
        dir_result = scripts.list_scripts(open_project(str(DIR_PROJECT)))
        zip_result = scripts.list_scripts(open_project(str(ZIP_PROJECT)))
        assert dir_result == zip_result


# ── UDTs ────────────────────────────────────────────────────


class TestUDTs:
    @pytest.fixture
    def source(self):
        return open_project(str(DIR_PROJECT))

    def test_list_udts(self, source):
        result = udts.list_udts(source)
        assert "Motor_UDT" in result
        assert "Valve_UDT" in result
        assert len(result) == 2

    def test_get_all_udts(self, source):
        result = udts.get_udt(source)
        assert len(result) == 2

    def test_get_specific_udt(self, source):
        result = udts.get_udt(source, "Motor_UDT")
        assert len(result) == 1
        motor = result[0]
        assert motor["name"] == "Motor_UDT"
        assert len(motor["members"]) == 3
        member_names = [m["name"] for m in motor["members"]]
        assert "Running" in member_names
        assert "Faulted" in member_names
        assert "Speed_RPM" in member_names

    def test_udt_has_parameters(self, source):
        result = udts.get_udt(source, "Motor_UDT")
        assert "parameters" in result[0]
        assert "MotorName" in result[0]["parameters"]

    def test_udt_has_documentation(self, source):
        result = udts.get_udt(source, "Motor_UDT")
        assert "documentation" in result[0]

    def test_nonexistent_udt(self, source):
        result = udts.get_udt(source, "Nonexistent_UDT")
        assert result == []

    def test_zip_returns_same(self):
        dir_result = udts.get_udt(open_project(str(DIR_PROJECT)))
        zip_result = udts.get_udt(open_project(str(ZIP_PROJECT)))
        assert dir_result == zip_result


# ── Alarms ──────────────────────────────────────────────────


class TestAlarms:
    @pytest.fixture
    def source(self):
        return open_project(str(DIR_PROJECT))

    def test_list_alarms(self, source):
        result = alarms.list_alarms(source)
        assert "MainAlarmPipeline" in result
        assert "EscalationPipeline" in result
        assert len(result) == 2

    def test_get_alarm_structure(self, source):
        result = alarms.get_alarm(source, "MainAlarmPipeline")
        assert result["name"] == "MainAlarmPipeline"
        assert result["enabled"] is True
        assert len(result["stages"]) == 3

    def test_alarm_stage_types(self, source):
        result = alarms.get_alarm(source, "MainAlarmPipeline")
        types = [s["type"] for s in result["stages"]]
        assert types == ["delay", "notification", "notification"]

    def test_alarm_stage_config(self, source):
        result = alarms.get_alarm(source, "MainAlarmPipeline")
        delay = result["stages"][0]
        assert delay["name"] == "Delay"
        assert delay["delaySeconds"] == 30

    def test_alarm_notification_profile(self, source):
        result = alarms.get_alarm(source, "MainAlarmPipeline")
        email = result["stages"][1]
        assert email["notificationProfileName"] == "PlantEmail"

    def test_disabled_pipeline(self, source):
        result = alarms.get_alarm(source, "EscalationPipeline")
        assert result["enabled"] is False
        assert len(result["stages"]) == 1

    def test_zip_returns_same(self):
        dir_result = alarms.list_alarms(open_project(str(DIR_PROJECT)))
        zip_result = alarms.list_alarms(open_project(str(ZIP_PROJECT)))
        assert dir_result == zip_result


# ── Named Queries ───────────────────────────────────────────


class TestNamedQueries:
    @pytest.fixture
    def source(self):
        return open_project(str(DIR_PROJECT))

    def test_list_named_queries(self, source):
        result = named_queries.list_named_queries(source)
        assert "GetActiveFaults" in result
        assert "LogFault" in result
        assert "GetMotorHistory" in result
        assert len(result) == 3

    def test_get_query_structure(self, source):
        result = named_queries.get_named_query(source, "GetActiveFaults")
        assert result["name"] == "GetActiveFaults"
        assert result["database"] == "PlantHistorian"
        assert result["queryType"] == "Query"
        assert "SELECT" in result["query"]

    def test_query_parameters(self, source):
        result = named_queries.get_named_query(source, "GetActiveFaults")
        assert "area" in result["parameters"]
        assert result["parameters"]["area"]["dataType"] == "String"

    def test_update_query_type(self, source):
        result = named_queries.get_named_query(source, "LogFault")
        assert result["queryType"] == "Update"
        assert "INSERT" in result["query"]

    def test_multiple_parameters(self, source):
        result = named_queries.get_named_query(source, "GetMotorHistory")
        params = result["parameters"]
        assert len(params) == 3
        assert "motorName" in params
        assert "startTime" in params
        assert "endTime" in params

    def test_query_description(self, source):
        result = named_queries.get_named_query(source, "GetActiveFaults")
        assert "active faults" in result["description"].lower()

    def test_zip_returns_same(self):
        dir_result = named_queries.list_named_queries(open_project(str(DIR_PROJECT)))
        zip_result = named_queries.list_named_queries(open_project(str(ZIP_PROJECT)))
        assert dir_result == zip_result


# ── Error Handling ──────────────────────────────────────────


class TestErrorHandling:
    def test_get_tags_bad_project(self):
        from ignition_mcp_server.server import get_tags
        result = json.loads(get_tags("/nonexistent/project"))
        assert "error" in result

    def test_get_view_bad_path(self):
        from ignition_mcp_server.server import get_view
        result = json.loads(get_view(str(DIR_PROJECT), "NonexistentView"))
        assert "error" in result

    def test_get_script_bad_path(self):
        from ignition_mcp_server.server import get_script
        result = json.loads(get_script(str(DIR_PROJECT), "nonexistent/path"))
        # Should return empty code, not crash
        assert isinstance(result, dict)

    def test_read_tag_no_gateway(self):
        from ignition_mcp_server import server
        server._gateway = None
        result = json.loads(server.read_tag("[default]test"))
        assert "error" in result
        assert "No gateway configured" in result["error"]

    def test_write_tag_no_gateway(self):
        from ignition_mcp_server import server
        server._gateway = None
        result = json.loads(server.write_tag("[default]test", "123"))
        assert "error" in result

    def test_execute_script_no_gateway(self):
        from ignition_mcp_server import server
        server._gateway = None
        result = json.loads(server.execute_script("x = 1"))
        assert "error" in result

    def test_get_history_no_gateway(self):
        from ignition_mcp_server import server
        server._gateway = None
        result = json.loads(server.get_history("[default]test", "2026-01-01", "2026-01-02"))
        assert "error" in result

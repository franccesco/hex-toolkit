"""Tests for project models."""

from datetime import datetime
from uuid import UUID

from hex_api.models.projects import (
    AccessLevel,
    AnalyticsInfo,
    AppViewsInfo,
    DayOfWeek,
    Project,
    ProjectList,
    ProjectType,
    ScheduleCadence,
)


class TestProjectModels:
    """Test project-related models."""

    def test_project_model_validation(self, sample_project_data: dict):
        """Test Project model validation."""
        project = Project.model_validate(sample_project_data)

        assert isinstance(project.id, UUID)
        assert project.title == "Test Project"
        assert project.description == "A test project"
        assert project.type == ProjectType.PROJECT
        assert project.creator.email == "creator@test.com"
        assert project.owner.email == "owner@test.com"
        assert project.status.name == "active"
        assert len(project.categories) == 1
        assert project.categories[0].name == "Test"
        assert isinstance(project.created_at, datetime)
        assert isinstance(project.analytics, AnalyticsInfo)
        assert project.analytics.app_views.all_time == 1000

    def test_project_list_model(self, sample_project_data: dict):
        """Test ProjectList model validation."""
        data = {
            "values": [sample_project_data],
            "pagination": {
                "after": "cursor123",
                "before": None,
            },
        }

        project_list = ProjectList.model_validate(data)

        assert len(project_list.values) == 1
        assert isinstance(project_list.values[0], Project)
        assert project_list.pagination.after == "cursor123"
        assert project_list.pagination.before is None

    def test_enum_values(self):
        """Test enum values."""
        assert ProjectType.PROJECT.value == "PROJECT"
        assert ProjectType.COMPONENT.value == "COMPONENT"

        assert AccessLevel.NONE.value == "NONE"
        assert AccessLevel.FULL_ACCESS.value == "FULL_ACCESS"

        assert ScheduleCadence.DAILY.value == "DAILY"
        assert ScheduleCadence.CUSTOM.value == "CUSTOM"

        assert DayOfWeek.MONDAY.value == "MONDAY"
        assert DayOfWeek.SUNDAY.value == "SUNDAY"

    def test_app_views_info(self):
        """Test AppViewsInfo model."""
        data = {
            "lastThirtyDays": 100,
            "lastFourteenDays": 50,
            "lastSevenDays": 25,
            "allTime": 1000,
        }

        app_views = AppViewsInfo.model_validate(data)

        assert app_views.last_thirty_days == 100
        assert app_views.last_fourteen_days == 50
        assert app_views.last_seven_days == 25
        assert app_views.all_time == 1000

    def test_field_aliases(self, sample_project_data: dict):
        """Test that field aliases work correctly."""
        # Update the sample data with aliased fields
        project_data = sample_project_data.copy()
        project_data.update({
            "lastEditedAt": "2024-01-01T00:00:00Z",
            "createdAt": "2024-01-01T00:00:00Z",
            "publicWeb": {"access": "NONE"},
        })

        project = Project.model_validate(project_data)
        assert isinstance(project.last_edited_at, datetime)
        assert isinstance(project.created_at, datetime)
        assert project.sharing.public_web.access == AccessLevel.NONE

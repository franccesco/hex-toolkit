"""Models for run-related API responses."""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import Field

from hex_toolkit.models.base import HexBaseModel, TraceInfo


class RunStatus(str, Enum):
    """Status of a project run."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    ERRORED = "ERRORED"
    COMPLETED = "COMPLETED"
    KILLED = "KILLED"
    UNABLE_TO_ALLOCATE_KERNEL = "UNABLE_TO_ALLOCATE_KERNEL"


class RunNotificationType(str, Enum):
    """Notification trigger types."""

    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    ALL = "ALL"


class NotificationRecipientType(str, Enum):
    """Types of notification recipients."""

    USER = "USER"
    GROUP = "GROUP"
    SLACK_CHANNEL = "SLACK_CHANNEL"


class ScreenshotFormat(str, Enum):
    """Screenshot format types."""

    PNG = "png"
    PDF = "pdf"


class NotificationRecipient(HexBaseModel):
    """Notification recipient details."""

    id: str = Field(..., description="Recipient ID")
    name: str = Field(..., description="Human readable name")
    is_private: bool | None = Field(None, alias="isPrivate")


class ProjectRunNotification(HexBaseModel):
    """Notification configuration for project runs."""

    type: RunNotificationType
    include_success_screenshot: bool = Field(..., alias="includeSuccessScreenshot")
    screenshot_format: ScreenshotFormat | None = Field(
        None, alias="screenshotFormat"
    )
    slack_channel_ids: list[str] | None = Field(None, alias="slackChannelIds")
    user_ids: list[str] | None = Field(None, alias="userIds")
    group_ids: list[str] | None = Field(None, alias="groupIds")
    subject: str | None = None
    body: str | None = None


class ProjectRunNotificationRecipient(HexBaseModel):
    """Notification recipient with full details."""

    type: RunNotificationType
    subject: str | None = None
    body: str | None = None
    recipient_type: NotificationRecipientType = Field(..., alias="recipientType")
    include_success_screenshot: bool = Field(..., alias="includeSuccessScreenshot")
    screenshot_format: list[ScreenshotFormat] | None = Field(
        None, alias="screenshotFormat"
    )
    recipient: NotificationRecipient


class RunProjectRequest(HexBaseModel):
    """Request body for running a project."""

    input_params: dict[str, Any] | None = Field(None, alias="inputParams")
    dry_run: bool = Field(False, alias="dryRun")
    update_cache: bool | None = Field(None, alias="updateCache", deprecated=True)
    notifications: list[ProjectRunNotification] | None = None
    update_published_results: bool = Field(False, alias="updatePublishedResults")
    use_cached_sql_results: bool = Field(True, alias="useCachedSqlResults")
    view_id: str | None = Field(None, alias="viewId")


class ProjectRunResponse(TraceInfo):
    """Response from running a project."""

    project_id: UUID = Field(..., alias="projectId")
    run_id: UUID = Field(..., alias="runId")
    run_url: str = Field(..., alias="runUrl")
    run_status_url: str = Field(..., alias="runStatusUrl")
    project_version: int = Field(..., alias="projectVersion")
    notifications: list[ProjectRunNotificationRecipient] | None = None


class ProjectStatusResponse(TraceInfo):
    """Status response for a project run."""

    project_id: UUID = Field(..., alias="projectId")
    project_version: int = Field(..., alias="projectVersion")
    run_id: UUID = Field(..., alias="runId")
    run_url: str = Field(..., alias="runUrl")
    status: RunStatus
    start_time: datetime | None = Field(None, alias="startTime")
    end_time: datetime | None = Field(None, alias="endTime")
    elapsed_time: float | None = Field(None, alias="elapsedTime")
    notifications: list[ProjectRunNotificationRecipient] | None = None


class ProjectRunsResponse(TraceInfo):
    """List of project runs."""

    runs: list[ProjectStatusResponse]
    next_page: str | None = Field(None, alias="nextPage")
    previous_page: str | None = Field(None, alias="previousPage")


class InvalidParam(HexBaseModel):
    """Invalid parameter information."""

    data_type: str = Field(..., alias="dataType")
    input_cell_type: str = Field(..., alias="inputCellType")
    param_value: str = Field(..., alias="paramValue")
    param_name: str = Field(..., alias="paramName")


class InvalidParamResponse(TraceInfo):
    """Response for invalid parameters."""

    invalid: list[InvalidParam] = []
    not_found: list[str] = Field([], alias="notFound")

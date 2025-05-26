"""Models for run-related API responses."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import Field

from hex_api.models.base import HexBaseModel, TraceInfo


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
    is_private: Optional[bool] = Field(None, alias="isPrivate")


class ProjectRunNotification(HexBaseModel):
    """Notification configuration for project runs."""

    type: RunNotificationType
    include_success_screenshot: bool = Field(..., alias="includeSuccessScreenshot")
    screenshot_format: Optional[ScreenshotFormat] = Field(
        None, alias="screenshotFormat"
    )
    slack_channel_ids: Optional[List[str]] = Field(None, alias="slackChannelIds")
    user_ids: Optional[List[str]] = Field(None, alias="userIds")
    group_ids: Optional[List[str]] = Field(None, alias="groupIds")
    subject: Optional[str] = None
    body: Optional[str] = None


class ProjectRunNotificationRecipient(HexBaseModel):
    """Notification recipient with full details."""

    type: RunNotificationType
    subject: Optional[str] = None
    body: Optional[str] = None
    recipient_type: NotificationRecipientType = Field(..., alias="recipientType")
    include_success_screenshot: bool = Field(..., alias="includeSuccessScreenshot")
    screenshot_format: Optional[List[ScreenshotFormat]] = Field(
        None, alias="screenshotFormat"
    )
    recipient: NotificationRecipient


class RunProjectRequest(HexBaseModel):
    """Request body for running a project."""

    input_params: Optional[Dict[str, Any]] = Field(None, alias="inputParams")
    dry_run: bool = Field(False, alias="dryRun")
    update_cache: Optional[bool] = Field(None, alias="updateCache", deprecated=True)
    notifications: Optional[List[ProjectRunNotification]] = None
    update_published_results: bool = Field(False, alias="updatePublishedResults")
    use_cached_sql_results: bool = Field(True, alias="useCachedSqlResults")
    view_id: Optional[str] = Field(None, alias="viewId")


class ProjectRunResponse(TraceInfo):
    """Response from running a project."""

    project_id: UUID = Field(..., alias="projectId")
    run_id: UUID = Field(..., alias="runId")
    run_url: str = Field(..., alias="runUrl")
    run_status_url: str = Field(..., alias="runStatusUrl")
    project_version: int = Field(..., alias="projectVersion")
    notifications: Optional[List[ProjectRunNotificationRecipient]] = None


class ProjectStatusResponse(TraceInfo):
    """Status response for a project run."""

    project_id: UUID = Field(..., alias="projectId")
    project_version: int = Field(..., alias="projectVersion")
    run_id: UUID = Field(..., alias="runId")
    run_url: str = Field(..., alias="runUrl")
    status: RunStatus
    start_time: Optional[datetime] = Field(None, alias="startTime")
    end_time: Optional[datetime] = Field(None, alias="endTime")
    elapsed_time: Optional[float] = Field(None, alias="elapsedTime")
    notifications: Optional[List[ProjectRunNotificationRecipient]] = None


class ProjectRunsResponse(TraceInfo):
    """List of project runs."""

    runs: List[ProjectStatusResponse]
    next_page: Optional[str] = Field(None, alias="nextPage")
    previous_page: Optional[str] = Field(None, alias="previousPage")


class InvalidParam(HexBaseModel):
    """Invalid parameter information."""

    data_type: str = Field(..., alias="dataType")
    input_cell_type: str = Field(..., alias="inputCellType")
    param_value: str = Field(..., alias="paramValue")
    param_name: str = Field(..., alias="paramName")


class InvalidParamResponse(TraceInfo):
    """Response for invalid parameters."""

    invalid: List[InvalidParam] = []
    not_found: List[str] = Field([], alias="notFound")

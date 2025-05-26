"""Models for project-related API responses."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import Field

from hex_api.models.base import HexBaseModel, PaginationInfo


class ProjectType(str, Enum):
    """Type of Hex project."""

    PROJECT = "PROJECT"
    COMPONENT = "COMPONENT"


class AccessLevel(str, Enum):
    """Access level for sharing."""

    NONE = "NONE"
    APP_ONLY = "APP_ONLY"
    CAN_VIEW = "CAN_VIEW"
    CAN_EDIT = "CAN_EDIT"
    FULL_ACCESS = "FULL_ACCESS"


class ScheduleCadence(str, Enum):
    """Schedule cadence types."""

    HOURLY = "HOURLY"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    CUSTOM = "CUSTOM"


class DayOfWeek(str, Enum):
    """Days of the week."""

    SUNDAY = "SUNDAY"
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"


class SortBy(str, Enum):
    """Sort options for project listing."""

    CREATED_AT = "CREATED_AT"
    LAST_EDITED_AT = "LAST_EDITED_AT"
    LAST_PUBLISHED_AT = "LAST_PUBLISHED_AT"


class SortDirection(str, Enum):
    """Sort direction."""

    DESC = "DESC"
    ASC = "ASC"


class UserInfo(HexBaseModel):
    """User information."""

    email: str


class CreatorInfo(UserInfo):
    """Creator information."""

    pass


class StatusInfo(HexBaseModel):
    """Project status information."""

    name: str


class CategoryInfo(HexBaseModel):
    """Project category information."""

    name: str
    description: Optional[str] = None


class ReviewsInfo(HexBaseModel):
    """Project reviews configuration."""

    required: bool


class AppViewsInfo(HexBaseModel):
    """App view analytics."""

    last_thirty_days: int = Field(..., alias="lastThirtyDays")
    last_fourteen_days: int = Field(..., alias="lastFourteenDays")
    last_seven_days: int = Field(..., alias="lastSevenDays")
    all_time: int = Field(..., alias="allTime")


class AnalyticsInfo(HexBaseModel):
    """Project analytics information."""

    published_results_updated_at: Optional[datetime] = Field(
        None, alias="publishedResultsUpdatedAt"
    )
    last_viewed_at: Optional[datetime] = Field(None, alias="lastViewedAt")
    app_views: AppViewsInfo = Field(..., alias="appViews")


class ScheduleTimeInfo(HexBaseModel):
    """Base schedule time configuration."""

    timezone: str
    minute: int = Field(..., ge=0, le=59)
    hour: int = Field(..., ge=0, le=23)


class HourlySchedule(HexBaseModel):
    """Hourly schedule configuration."""

    timezone: str
    minute: int = Field(..., ge=0, le=59)


class DailySchedule(ScheduleTimeInfo):
    """Daily schedule configuration."""

    pass


class WeeklySchedule(ScheduleTimeInfo):
    """Weekly schedule configuration."""

    day_of_week: DayOfWeek = Field(..., alias="dayOfWeek")


class MonthlySchedule(ScheduleTimeInfo):
    """Monthly schedule configuration."""

    day: int = Field(..., ge=1, le=28)


class CustomSchedule(HexBaseModel):
    """Custom cron schedule configuration."""

    timezone: str
    cron: str


class Schedule(HexBaseModel):
    """Project schedule configuration."""

    cadence: ScheduleCadence
    enabled: bool
    hourly: Optional[HourlySchedule] = None
    daily: Optional[DailySchedule] = None
    weekly: Optional[WeeklySchedule] = None
    monthly: Optional[MonthlySchedule] = None
    custom: Optional[CustomSchedule] = None


class UserAccess(HexBaseModel):
    """User access configuration."""

    user: UserInfo
    access: AccessLevel


class CollectionAccess(HexBaseModel):
    """Collection access configuration."""

    collection: Dict[str, str]  # {"name": "collection_name"}
    access: AccessLevel


class GroupAccess(HexBaseModel):
    """Group access configuration."""

    group: Dict[str, str]  # {"name": "group_name"}
    access: AccessLevel


class WorkspaceAccess(HexBaseModel):
    """Workspace access configuration."""

    access: AccessLevel


class PublicWebAccess(HexBaseModel):
    """Public web access configuration."""

    access: AccessLevel


class SupportAccess(HexBaseModel):
    """Support access configuration."""

    access: AccessLevel


class SharingInfo(HexBaseModel):
    """Project sharing configuration."""

    users: List[UserAccess] = []
    collections: List[CollectionAccess] = []
    groups: List[GroupAccess] = []
    workspace: WorkspaceAccess
    public_web: PublicWebAccess = Field(..., alias="publicWeb")
    support: SupportAccess


class Project(HexBaseModel):
    """Hex project resource."""

    id: UUID
    title: str
    description: Optional[str] = None
    type: ProjectType
    creator: CreatorInfo
    owner: UserInfo
    status: Optional[StatusInfo] = None
    categories: List[CategoryInfo] = []
    reviews: ReviewsInfo
    analytics: AnalyticsInfo
    last_edited_at: datetime = Field(..., alias="lastEditedAt")
    last_published_at: Optional[datetime] = Field(None, alias="lastPublishedAt")
    created_at: datetime = Field(..., alias="createdAt")
    archived_at: Optional[datetime] = Field(None, alias="archivedAt")
    trashed_at: Optional[datetime] = Field(None, alias="trashedAt")
    schedules: List[Schedule] = []
    sharing: Optional[SharingInfo] = None


class ProjectList(HexBaseModel):
    """List of projects with pagination."""

    values: List[Project]
    pagination: PaginationInfo
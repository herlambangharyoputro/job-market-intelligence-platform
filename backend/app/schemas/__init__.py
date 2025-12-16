# from app.schemas.job_listing import (
#     JobListing,
#     JobListingCreate,
#     JobListingUpdate,
#     JobListingList,
#     JobListingFilter,
#     JobListingStats
# )

# __all__ = [
#     "JobListing",
#     "JobListingCreate", 
#     "JobListingUpdate",
#     "JobListingList",
#     "JobListingFilter",
#     "JobListingStats"
# ]


# ADD: Module #5 - Skill Validation System
from .skill_category import (
    SkillCategory,
    SkillCategoryCreate,
    SkillCategoryUpdate,
    SkillCategoryList
)

from .skill_dictionary import (
    SkillsDictionary,
    SkillsDictionaryCreate,
    SkillsDictionaryUpdate,
    SkillsDictionaryWithCategory,
    SkillsDictionaryList,
    ValidationStatus
)

from .validation_queue import (
    ValidationQueue,
    ValidationQueueCreate,
    ValidationQueueUpdate,
    ValidationQueueWithCategory,
    ValidationQueueList,
    ValidateSkillRequest,
    ValidateSkillResponse,
    BulkValidateRequest,
    BulkValidateResponse,
    ValidationAction,
    QueueStatus
)

from .validation_history import (
    ValidationHistory,
    ValidationHistoryCreate,
    ValidationHistoryWithDetails,
    ValidationHistoryList,
    ValidationStatsResponse,
    HistoryAction
)

__all__ = [
    # ... existing exports
    
    # Module #5 - Categories
    "SkillCategory",
    "SkillCategoryCreate",
    "SkillCategoryUpdate",
    "SkillCategoryList",
    
    # Module #5 - Dictionary
    "SkillsDictionary",
    "SkillsDictionaryCreate",
    "SkillsDictionaryUpdate",
    "SkillsDictionaryWithCategory",
    "SkillsDictionaryList",
    "ValidationStatus",
    
    # Module #5 - Queue
    "ValidationQueue",
    "ValidationQueueCreate",
    "ValidationQueueUpdate",
    "ValidationQueueWithCategory",
    "ValidationQueueList",
    "ValidateSkillRequest",
    "ValidateSkillResponse",
    "BulkValidateRequest",
    "BulkValidateResponse",
    "ValidationAction",
    "QueueStatus",
    
    # Module #5 - History
    "ValidationHistory",
    "ValidationHistoryCreate",
    "ValidationHistoryWithDetails",
    "ValidationHistoryList",
    "ValidationStatsResponse",
    "HistoryAction",
]
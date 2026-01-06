from enum import StrEnum


class AgentID(StrEnum):

    BEST_FLAT_LABEL = "best-flat-label"
    BEST_FLAT_FLOOR = "best-flat-floor"
    LAYOUT_EVALUATOR = "layout_evaluator"
    WINDOW_VIEW_EVALUATOR = "window_view_evaluator"

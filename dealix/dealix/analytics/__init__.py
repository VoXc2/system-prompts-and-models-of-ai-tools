"""Dealix analytics — PostHog funnel tracking + feature flags."""

from dealix.analytics.posthog_client import FUNNEL_EVENTS, capture_event, get_feature_flag

__all__ = ["FUNNEL_EVENTS", "capture_event", "get_feature_flag"]

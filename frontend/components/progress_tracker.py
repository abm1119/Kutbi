"""
Progress tracker component for Streamlit UI.
"""

import streamlit as st


def render_progress(
    current_step: int,
    total_steps: int,
    status_message: str,
    details: dict = None
):
    """
    Render progress indicator.

    Args:
        current_step: Current step number
        total_steps: Total number of steps
        status_message: Current status message
        details: Optional details dictionary
    """
    progress = current_step / total_steps if total_steps > 0 else 0
    st.progress(progress, text=status_message)

    if details:
        with st.expander("Details", expanded=False):
            for key, value in details.items():
                st.caption(f"**{key}:** {value}")


def render_processing_status(is_processing: bool, message: str = ""):
    """
    Render processing status indicator.

    Args:
        is_processing: Whether processing is in progress
        message: Status message
    """
    if is_processing:
        with st.status(message, expanded=True) as status:
            st.write("Processing videos...")
            return status
    return None


class ProgressTracker:
    """Helper class for tracking multi-step progress."""

    def __init__(self, total_videos: int):
        """
        Initialize progress tracker.

        Args:
            total_videos: Total number of videos to process
        """
        self.total_videos = total_videos
        self.current_video = 0
        self.steps = [
            ("Fetching channel info...", ":material/search:"),
            ("Getting video list...", ":material/list:"),
            ("Processing videos...", ":modeling:"),
            ("Creating Notion pages...", ":material/edit_document:"),
            ("Complete!", ":material/check_circle:"),
        ]
        self.current_step = 0
        self.progress_bar = None
        self.status_text = None

    def start(self):
        """Start progress tracking."""
        self.progress_bar = st.progress(0)
        self.status_text = st.empty()
        self.update_step(0)

    def update_step(self, step: int, message: str = None):
        """
        Update to a specific step.

        Args:
            step: Step index
            message: Optional custom message
        """
        self.current_step = step
        progress = (step / len(self.steps)) * 0.3  # First 30% for setup steps

        if self.progress_bar:
            self.progress_bar.progress(progress)

        if self.status_text:
            msg = message or self.steps[step][0]
            icon = self.steps[step][1]
            self.status_text.text(f"{icon} {msg}")

    def update_video(self, video_index: int, video_title: str = ""):
        """
        Update video processing progress.

        Args:
            video_index: Current video index (0-based)
            video_title: Video title for display
        """
        self.current_video = video_index + 1

        # 30-90% for video processing
        base_progress = 0.3
        video_progress = (self.current_video / self.total_videos) * 0.6
        progress = base_progress + video_progress

        if self.progress_bar:
            self.progress_bar.progress(progress)

        if self.status_text:
            msg = f"Processing video {self.current_video}/{self.total_videos}"
            if video_title:
                msg += f": {video_title[:40]}..."
            self.status_text.text(f":material/video_library: {msg}")

    def complete(self):
        """Mark processing as complete."""
        if self.progress_bar:
            self.progress_bar.progress(1.0)

        if self.status_text:
            self.status_text.text(":material/check_circle: Processing complete!")

    def error(self, message: str):
        """
        Display error state.

        Args:
            message: Error message
        """
        if self.status_text:
            self.status_text.error(f":material/error: {message}")

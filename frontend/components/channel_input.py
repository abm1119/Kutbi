"""
Channel input component for Streamlit UI.
"""

import re
import streamlit as st


def render_channel_input() -> tuple[str, int]:
    """
    Render channel input form.

    Returns:
        Tuple of (channel_url, max_videos)
    """
    channel_url = st.text_input(
        "YouTube URL, handle, or video ID",
        placeholder="@channel  ·  youtube.com/watch?v=...  ·  video_id",
        help="Enter a YouTube channel URL, @handle, channel ID, video URL, or video ID",
        key="source_input",
    )

    # Validation feedback
    if channel_url:
        is_valid = validate_channel_input(channel_url)
        if is_valid:
            st.caption(":material/check_circle: Valid YouTube input", text_alignment="left")
        else:
            st.caption(":material/warning: Please enter a valid YouTube URL, handle, or ID", text_alignment="left")

    # Number of videos slider
    max_videos = st.slider(
        "Latest videos to scan",
        min_value=1,
        max_value=20,
        help="Choose how many recent uploads to bring into the review step.",
        key="max_videos_input",
    )

    return channel_url, max_videos


def validate_channel_input(input_str: str) -> bool:
    """
    Validate if the input looks like a valid channel URL or ID.

    Args:
        input_str: User input string

    Returns:
        True if valid format
    """
    input_str = input_str.strip()

    # Channel ID format (UC + 22 chars)
    if re.match(r'^UC[\w-]{22}$', input_str):
        return True

    # Video ID format (11 chars)
    if re.match(r'^[A-Za-z0-9_-]{11}$', input_str):
        return True

    # @handle format
    if input_str.startswith('@') and len(input_str) > 1:
        return True

    # YouTube URL patterns
    youtube_patterns = [
        r'youtube\.com/channel/',
        r'youtube\.com/@',
        r'youtube\.com/c/',
        r'youtube\.com/user/',
        r'youtube\.com/watch\?v=',
        r'youtube\.com/shorts/',
        r'youtube\.com/live/',
        r'youtu\.be/',
    ]

    for pattern in youtube_patterns:
        if re.search(pattern, input_str):
            return True

    return False


def render_saved_channels(channels: list) -> str:
    """
    Render saved channels selector.

    Args:
        channels: List of saved channel dicts

    Returns:
        Selected channel ID or empty string
    """
    if not channels:
        st.caption(":material/info: No saved channels yet. Process a channel to save it.")
        return ""

    # Create options
    options = ["Select a channel..."]
    for ch in channels:
        name = ch.get('channel_name', 'Unknown')
        ch_id = ch.get('channel_id', '')
        last = ch.get('last_processed', 'Never')
        if last and last != 'Never':
            last = last.split('T')[0]  # Just the date
        options.append(f"{name} (last: {last})")

    selected_idx = st.selectbox(
        "Saved channels",
        range(len(options)),
        format_func=lambda i: options[i],
    )

    if selected_idx > 0:
        return channels[selected_idx - 1].get('channel_id', '')

    return ""

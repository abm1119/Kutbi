"""Premium, readable result cards for the Kutbi workspace."""

from datetime import datetime

import streamlit as st


def _format_date(value: str | None) -> str:
    """Format ISO timestamp strings for display."""
    if not value:
        return "Unknown date"
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime("%b %d, %Y")
    except ValueError:
        return value


def _format_duration(duration_seconds: int | None) -> str:
    """Format video duration in a compact human-readable form."""
    if not duration_seconds:
        return "Unknown duration"
    hours, remainder = divmod(int(duration_seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{hours:d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:d}:{seconds:02d}"


def render_results(response: dict) -> None:
    """Render the batch summary and individual guide cards."""
    if not response:
        return

    channel_name = response.get("channel_name", "Unknown")
    results = response.get("results", [])
    summary = response.get("summary", {})
    total_time = response.get("total_processing_time_seconds", 0)
    total_tokens = summary.get("total_tokens", 0)

    st.markdown(":green-badge[Guide batch complete]")
    st.title(f"Guides from {channel_name}")
    st.caption("A distilled collection of ideas, steps, and references ready to revisit.")
    st.space("small")

    metric_data = [
        ("Videos", summary.get("total", 0), ":material/video_library:"),
        ("Successful", summary.get("successful", 0), ":material/check_circle:"),
        ("Needs attention", summary.get("failed", 0), ":material/error:"),
        ("Time", f"{total_time:.1f}s", ":material/timer:"),
    ]
    cols = st.columns(4, vertical_alignment="center")
    for col, (label, value, icon) in zip(cols, metric_data):
        with col:
            with st.container(border=True):
                st.caption(f"{icon} {label}")
                st.metric(label, value, label_visibility="collapsed")

    st.caption(f":material/token: {total_tokens:,} tokens used across this batch")
    st.space("medium")
    st.markdown("### Your guides")

    for result in results:
        render_video_result(result)


def render_video_result(result: dict) -> None:
    """Render one compact guide result card."""
    status = result.get("status", "unknown")
    title = result.get("video_title", "Unknown video")
    views = result.get("views", 0)
    published_at = result.get("published_at")
    duration_seconds = result.get("duration_seconds")
    video_url = result.get("video_url")
    notion_url = result.get("notion_page_url")
    error = result.get("error")
    proc_time = result.get("processing_time_seconds")
    total_tokens = result.get("total_tokens")

    with st.container(border=True):
        col_main, col_meta = st.columns([3, 1], vertical_alignment="top")

        with col_main:
            st.markdown(f"**{title}**")
            if status == "success":
                st.badge("Ready", icon=":material/check:", color="green")
            elif status == "failed":
                st.badge("Needs attention", icon=":material/error:", color="red")
            else:
                st.badge("Skipped", icon=":material/remove_circle:", color="orange")

            links = []
            if video_url:
                links.append(f"[Watch video]({video_url})")
            if notion_url:
                links.append(f"[Open Notion guide]({notion_url})")
            if links:
                st.caption(" · ".join(links))

            if error:
                st.error(error, icon=":material/error:")

        with col_meta:
            st.caption(f":material/calendar_today: {_format_date(published_at)}")
            st.caption(f":material/schedule: {_format_duration(duration_seconds)}")
            st.caption(f":material/visibility: {views:,} views")
            if proc_time:
                st.caption(f":material/timer: {proc_time:.1f}s")
            if total_tokens:
                st.caption(f":material/token: {total_tokens:,}")


def render_video_selection(discovery_response: dict) -> list[str]:
    """Render a readable multi-select for discovered videos."""
    videos = discovery_response.get("videos", [])
    source_type = discovery_response.get("source_type", "channel")
    channel_name = discovery_response.get("channel_name", "Unknown")

    if not videos:
        st.warning("No videos were found for this input.", icon=":material/search_off:")
        return []

    if source_type == "video":
        st.caption(":material/play_circle: Single video detected. It is ready to process.")
    else:
        st.caption(f":material/playlist_play: Latest uploads from {channel_name}")

    video_by_id: dict[str, dict] = {}
    video_ids: list[str] = []
    for video in videos:
        video_id = video.get("video_id", "")
        if video_id:
            video_by_id[video_id] = video
            video_ids.append(video_id)

    def format_video(video_id: str) -> str:
        video = video_by_id[video_id]
        return (
            f"{video.get('title', 'Untitled')}  ·  "
            f"{_format_date(video.get('published_at'))}  ·  "
            f"{video.get('view_count', 0):,} views  ·  "
            f"{_format_duration(video.get('duration_seconds'))}"
        )

    return st.multiselect(
        "Videos to synthesize",
        options=video_ids,
        default=video_ids,
        format_func=format_video,
        help="Keep all selected for a complete batch, or narrow the list before generating guides.",
        key="video_selection",
    )


def render_notion_links(results: list) -> None:
    """Render links to the Notion pages created by a batch."""
    successful = [
        result
        for result in results
        if result.get("status") == "success" and result.get("notion_page_url")
    ]
    if not successful:
        return

    with st.container(border=True):
        st.markdown("### :material/auto_stories: Notion pages created")
        st.caption("Your guides are ready to return to whenever the idea becomes useful.")
        for result in successful:
            title = result.get("video_title", "Unknown")
            url = result.get("notion_page_url")
            st.markdown(f":material/arrow_outward: [{title}]({url})")

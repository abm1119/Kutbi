"""
Kutbi: a calm workspace for turning YouTube knowledge into Notion guides.
"""

import sys
from pathlib import Path

import streamlit as st

# Add project root to path for imports.
FRONTEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = FRONTEND_DIR.parent
LOGO_PATH = PROJECT_ROOT / "assets" / "kutbi_purple.png"
sys.path.insert(0, str(PROJECT_ROOT))

from frontend.api_client import APIClient
from frontend.components.channel_input import render_channel_input
from frontend.components.results_display import (
    render_notion_links,
    render_results,
    render_video_selection,
)


st.set_page_config(
    page_title="Kutbi — YouTube to useful knowledge",
    page_icon=str(LOGO_PATH),
    layout="wide",
    initial_sidebar_state="expanded",
)


def _initialize_state() -> None:
    """Initialize per-session values in one predictable place."""
    defaults = {
        "discovery_response": None,
        "discovery_source_input": "",
        "last_results": None,
        "notion_db_input": "",
        "llm_provider_input": "openrouter",
        "llm_model_input": "",
        "source_input": "",
        "max_videos_input": 5,
        "tab_selector": "Discovery",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def _render_sidebar(api_client: APIClient) -> None:
    """Render compact global settings and connection controls."""
    with st.sidebar:
        with st.container(horizontal_alignment="center"):
            st.image(str(LOGO_PATH), width=260)
        st.caption("A quieter way to build your personal technical library.")
        st.space("medium")

        with st.container(border=True):
            st.markdown("**Workspace settings**")
            st.caption("Choose where your guides go and which model shapes them.")

            st.text_input(
                "Notion database ID",
                placeholder="Optional — skip export if empty",
                help="Guides are still generated when this is blank; only the Notion export is skipped.",
                key="notion_db_input",
            )

            st.space("small")
            st.segmented_control(
                "AI provider",
                options=["openrouter", "gemini"],
                format_func=lambda value: (
                    "OpenRouter" if value == "openrouter" else "Gemini"
                ),
                label_visibility="collapsed",
                key="llm_provider_input",
            )
            st.text_input(
                "Model name",
                placeholder="Auto-selected by provider",
                help="Optional model ID override for advanced users.",
                key="llm_model_input",
            )

        st.space("small")
        with st.container(border=True):
            st.markdown("**Connection**")
            st.caption("Check that the Kutbi backend and connected services are ready.")
            if st.button(
                "Check connection",
                icon=":material/monitor_heart:",
                type="secondary",
                width="stretch",
            ):
                with st.status("Checking services…", expanded=False) as status:
                    health = api_client.health_check()
                    if health.get("status") == "healthy":
                        status.update(
                            label="All services connected",
                            state="complete",
                            expanded=False,
                        )
                        st.toast("Kutbi is ready to work")
                    else:
                        status.update(
                            label="Some services need attention",
                            state="error",
                            expanded=True,
                        )
                        st.caption(
                            health.get(
                                "error", "The backend returned a non-healthy status."
                            )
                        )

        st.space("large")
        st.caption("Kutbi · YouTube to Notion guide generator")
        st.caption("Made for thoughtful learning, one video at a time.")


def _render_header() -> None:
    """Render the product header and primary view switcher."""
    st.markdown(":violet-badge[Knowledge workspace]")
    st.title("Turn good videos into useful knowledge.")
    st.markdown(
        "Bring a YouTube channel or a single video. Kutbi finds the signal, "
        "shapes it into an actionable guide, and sends it to Notion."
    )
    st.space("small")

    with st.container(horizontal=True, vertical_alignment="center"):
        st.segmented_control(
            "Workspace view",
            options=["Discovery", "Results"],
            format_func=lambda value: (
                ":material/travel_explore: Discover"
                if value == "Discovery"
                else ":material/auto_stories: Results"
            ),
            label_visibility="collapsed",
            key="tab_selector",
        )


def _run_processing(
    api_client: APIClient,
    source_input: str,
    selected_video_ids: list[str],
    max_videos: int,
) -> None:
    """Run synthesis and persist the response for the results view."""
    status = st.status("Building your guide…", expanded=True)
    try:
        with status:
            st.write("Fetching transcripts and shaping the key ideas…")
            response = api_client.process_videos(
                source_input=source_input,
                selected_video_ids=selected_video_ids,
                notion_database_id=st.session_state.notion_db_input or None,
                max_videos=max_videos,
                llm_provider=st.session_state.llm_provider_input,
                llm_model=st.session_state.llm_model_input,
            )
        st.session_state.last_results = response
        st.session_state.tab_selector = "Results"
        status.update(label="Guide ready", state="complete", expanded=False)
        st.toast("Your guide is ready")
    except Exception as exc:
        status.update(label="Synthesis failed", state="error", expanded=True)
        st.error(f"We could not finish this guide: {exc}")
        st.session_state.last_results = None


def _render_discovery(api_client: APIClient) -> None:
    """Render the discovery and selection workflow."""
    with st.container(border=True):
        st.markdown("### Start with a source")
        st.caption(
            "Paste a channel, handle, video URL, or video ID. Kutbi will do the sorting."
        )

        with st.form("discovery_form", border=False):
            source_input, max_videos = render_channel_input()
            st.space("small")
            submitted = st.form_submit_button(
                "Discover videos",
                type="primary",
                icon=":material/search:",
                width="stretch",
            )

    if submitted:
        if not source_input.strip():
            st.warning("Add a YouTube source to begin.", icon=":material/info:")
        else:
            with st.status("Finding the right videos…", expanded=False) as status:
                try:
                    response = api_client.discover_videos(
                        source_input.strip(), max_videos
                    )
                    st.session_state.discovery_response = response
                    st.session_state.discovery_source_input = source_input.strip()
                    count = len(response.get("videos", []))
                    status.update(
                        label=f"{count} video{'s' if count != 1 else ''} ready to review",
                        state="complete",
                        expanded=False,
                    )
                    st.toast(f"Found {count} videos")
                except Exception as exc:
                    status.update(
                        label="Discovery failed", state="error", expanded=True
                    )
                    st.error(f"We could not read that source: {exc}")

    discovery = st.session_state.get("discovery_response")
    if not discovery:
        st.space("medium")
        with st.container(border=True, horizontal_alignment="center"):
            st.space("small")
            st.markdown(":material/auto_awesome:", text_alignment="center")
            st.markdown("**Your next guide starts here.**", text_alignment="center")
            st.caption(
                "One source in. A structured, memorable guide out.",
                text_alignment="center",
            )
            st.space("small")
        return

    videos = discovery.get("videos", [])
    channel_name = discovery.get("channel_name", "Your source")
    source_type = discovery.get("source_type", "channel")
    st.space("medium")

    with st.container(border=True):
        with st.container(horizontal=True, vertical_alignment="center"):
            st.markdown("### Review the signal")
            st.badge(
                "Single video" if source_type == "video" else "Channel scan",
                icon=":material/video_library:",
                color="blue",
            )
        st.caption(
            f"{channel_name} · {len(videos)} candidate{'s' if len(videos) != 1 else ''}"
        )

        selected_video_ids = render_video_selection(discovery)
        st.space("small")
        with st.container(horizontal=True, vertical_alignment="center"):
            st.caption(
                f"{len(selected_video_ids)} selected · Your choices become individual Notion guides."
                if selected_video_ids
                else "Select at least one video to continue."
            )
            if st.button(
                "Build selected guides",
                type="primary",
                icon=":material/rocket_launch:",
                disabled=not selected_video_ids,
            ):
                _run_processing(
                    api_client,
                    st.session_state.discovery_source_input,
                    selected_video_ids,
                    st.session_state.max_videos_input,
                )

    st.space("small")
    with st.expander("How Kutbi works", icon=":material/lightbulb:"):
        st.caption("01 · Discover")
        st.write(
            "Kutbi finds the latest uploads or inspects the single video you shared."
        )
        st.caption("02 · Understand")
        st.write(
            "Transcripts are distilled into ideas, tools, steps, and practical next actions."
        )
        st.caption("03 · Keep")
        st.write("The finished guides are saved as clean, reusable pages in Notion.")


def _render_results() -> None:
    """Render the results workspace or its empty state."""
    results = st.session_state.get("last_results")
    if results:
        render_results(results)
        st.space("medium")
        render_notion_links(results.get("results", []))
        return

    with st.container(border=True, horizontal_alignment="center"):
        st.space("medium")
        st.markdown(":material/auto_stories:", text_alignment="center")
        st.markdown("### Your library is waiting.", text_alignment="center")
        st.caption(
            "Discover and process a video to see its guide appear here.",
            text_alignment="center",
        )
        st.space("small")


def main() -> None:
    _initialize_state()
    api_client = APIClient()
    _render_sidebar(api_client)
    _render_header()

    if st.session_state.tab_selector == "Discovery":
        _render_discovery(api_client)
    else:
        _render_results()


if __name__ == "__main__":
    main()

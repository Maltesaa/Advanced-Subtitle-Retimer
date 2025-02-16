import re
import os
import json
import sys
import shutil
import tempfile
from dataclasses import dataclass
from . import utility
from typing import List, Dict, Any, Set, Tuple, Callable


@dataclass
class SubtitleStream:
    index: int
    name: str
    codec: str

    @classmethod
    def from_ffprobe_stream(cls, stream: Dict[str, Any]) -> 'SubtitleStream':
        tags = stream.get("tags", {})
        stream_name = (
            tags.get("title", "").strip() or
            tags.get("language", "").strip() or
            "unknown"
        )
        return cls(
            index=stream["index"],
            name=stream_name,
            codec=stream["codec_name"]
        )

    def __hash__(self) -> int:
        return hash((self.index, self.name, self.codec))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SubtitleStream):
            return NotImplemented
        return (self.index == other.index and
                self.name == other.name and
                self.codec == other.codec)


def file_name_sorter(file_name: str) -> str:
    """Zero pads all numbers in a file name to 5 digits for sorting."""
    file_name_without_whitespace = re.sub(r'\s+', '', file_name)
    return re.sub(r'\d+', lambda match: match.group(0).zfill(5), file_name_without_whitespace.lower())


def extract_subtitle_streams_from_file(file_path: str) -> List[Dict[str, Any]]:
    """Extract subtitle stream information from a video file using ffprobe."""
    command = ["ffprobe", "-v", "quiet", "-print_format", "json",
               "-show_streams", "-select_streams", "s", file_path]
    output = utility.run_command(command)
    if not output:
        print(f"Error: Failed to extract subtitle streams from file:\n\t{file_path}", file=sys.stderr)
        sys.exit(1)
    return json.loads(output)["streams"]


def extract_subtitle_streams_from_files(file_paths: List[str]) -> List[List[Dict[str, Any]]]:
    """Extract subtitle stream information from multiple video files."""
    return [extract_subtitle_streams_from_file(file_path) for file_path in file_paths]


def get_unique_streams(file_streams: List[Dict[str, Any]]) -> Set[SubtitleStream]:
    """Convert raw stream data into unique SubtitleStream objects."""
    return {SubtitleStream.from_ffprobe_stream(stream) for stream in file_streams}


def prompt_stream_selection(streams: List[SubtitleStream]) -> SubtitleStream:
    """Prompt user to select a subtitle stream if multiple are available."""
    if len(streams) == 1:
        return streams[0]

    for index, stream in enumerate(streams):
        print(f"[{index}] Stream {stream.index}: {stream.name} ({stream.codec})")
    choice = int(input("Please choose subtitle to extract> "))
    return streams[choice]


def get_subtitle_stream_indices(all_files_streams: List[List[Dict[str, Any]]]) -> Tuple[List[int], List[str]]:
    """Determine which subtitle stream to extract from each file."""
    if not all_files_streams:
        raise ValueError("No subtitle streams found")

    # Handle simple case: all files have exactly one stream
    if all(len(file_streams) == 1 for file_streams in all_files_streams):
        return zip(*[(s[0]["index"], s[0]["codec_name"]) for s in all_files_streams])

    # Handle case where all files have same number of streams
    if all(len(file_streams) == len(all_files_streams[0]) for file_streams in all_files_streams):
        streams = get_unique_streams(all_files_streams[0])
        selected = prompt_stream_selection(list(streams))
        return ([selected.index] * len(all_files_streams),
                [selected.codec] * len(all_files_streams))

    # Handle case where files have different numbers of streams
    indices, codecs = [], []
    print("Subtitle streams differ between files. Please select streams to extract for each file.")
    for file_streams in all_files_streams:
        streams = get_unique_streams(file_streams)
        selected = prompt_stream_selection(list(streams))
        indices.append(selected.index)
        codecs.append(selected.codec)

    return indices, codecs


def extract_subtitle(file_path: str, subtitle_index: int, target_path: str) -> None:
    """Extract a single subtitle stream from a video file."""
    extract_command = ["mkvextract", "tracks", file_path, f"{subtitle_index}:{target_path}"]
    utility.run_command(extract_command)


def extract_subtitles(video_file_paths: List[str],
                      subtitle_codecs: List[str],
                      selected_stream_indices: List[int]) -> Tuple[List[str], Callable[[], None]]:
    """Extract subtitle streams from multiple video files."""
    if not (len(video_file_paths) == len(subtitle_codecs) == len(selected_stream_indices)):
        raise ValueError("All input lists must have the same length")

    temp_dir = tempfile.mkdtemp(prefix="subtitle_extraction")
    extracted_files = []

    for video_path, codec, stream_idx in zip(video_file_paths, subtitle_codecs, selected_stream_indices):
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        output_path = os.path.join(temp_dir, f"{base_name}.{codec}")

        print(f"Extracting subtitles from {os.path.basename(video_path)} to\n\t{os.path.basename(output_path)}")
        extract_subtitle(video_path, stream_idx, output_path)
        extracted_files.append(output_path)

    return extracted_files, lambda: shutil.rmtree(temp_dir)

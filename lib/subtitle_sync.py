from pathlib import Path
from typing import List
from .utility import run_command


def sync_subtitle(reference_subtitle: str, target_subtitle: str, output_path: str) -> None:
    """
    Synchronize a target subtitle file with a reference subtitle file.
    """
    print(f"Syncing subtitle files:\nReference: {reference_subtitle}\nTarget: {target_subtitle}")
    print(f"Output: {output_path}")

    output: str = run_command(["alass", reference_subtitle, target_subtitle, output_path])
    shift_info: str = "\n".join(line for line in output.split("\n") if "shifted block" in line)
    print(shift_info)


def sync_subtitles(reference_subtitles: List[str], target_subtitles: List[str], output_dir: str) -> None:
    """
    Synchronize multiple pairs of subtitle files.
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    for reference_sub, target_sub in zip(reference_subtitles, target_subtitles):
        reference_name = Path(reference_sub).stem
        target_extension = Path(target_sub).suffix
        output_filename = reference_name + target_extension
        output_subtitle = output_path / output_filename

        sync_subtitle(reference_sub, target_sub, str(output_subtitle))

    print("Finished syncing subtitles.")

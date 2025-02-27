import glob
import os
import lib.subtitle_extraction as subtitle_extraction
import lib.subtitle_cleaning as subtitle_cleaning
import lib.subtitle_sync as subtitle_sync
import lib.utility as utility


def main():
    current_dir = os.getcwd()

    reference_mkv_files = sorted(glob.glob(os.path.join(current_dir, '*.mkv')),
                                 key=utility.file_name_sorter)

    # First try with just .srt files
    target_sub_files = sorted(glob.glob(os.path.join(current_dir, '*.srt')),
                              key=utility.file_name_sorter)

    # Only include .ass files if the counts don't match
    if len(reference_mkv_files) != len(target_sub_files):
        target_sub_files = sorted(glob.glob(os.path.join(current_dir, '*.srt')) +
                                  glob.glob(os.path.join(current_dir, '*.ass')),
                                  key=utility.file_name_sorter)

    if len(reference_mkv_files) != len(target_sub_files):
        raise ValueError(
            f"Number of video files ({len(reference_mkv_files)}) and subtitle files ({len(target_sub_files)}) do not match.")

    reference_streams_per_file = subtitle_extraction.extract_subtitle_streams_from_files(reference_mkv_files)
    reference_stream_indices, subtitle_codecs = subtitle_extraction.get_subtitle_stream_indices(
        reference_streams_per_file)

    extracted_reference_files, cleanup_extracted_subs = subtitle_extraction.extract_subtitles(
        reference_mkv_files, subtitle_codecs, reference_stream_indices)

    cleaned_reference_files, cleanup_cleaned_reference_subs = subtitle_cleaning.clean_tags(extracted_reference_files)
    cleaned_target_files, cleanup_cleaned_target_subs = subtitle_cleaning.clean_up_japanese_subs(target_sub_files)
    subtitle_sync.sync_subtitles(cleaned_reference_files, cleaned_target_files, current_dir)

    cleanup_extracted_subs()
    cleanup_cleaned_reference_subs()
    cleanup_cleaned_target_subs()


if __name__ == '__main__':
    main()

import asl_modules.tokenization as tokenization
import asl_modules.downloader as downloader
import asl_modules.stitch_files as stitch_files


def make_vid(input_):
    token = tokenization.tokens(input_)
    arr = downloader.download_all(token)
    stitch_files.stitch_videos_in_folder(arr)

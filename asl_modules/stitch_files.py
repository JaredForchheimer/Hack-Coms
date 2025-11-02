import os
import requests
import tempfile
from moviepy.editor import VideoFileClip, concatenate_videoclips
from moviepy.video.fx.speedx import speedx


def stitch_videos_in_folder(
    urls, output_path=os.path.join("video", "output.mp4"), extensions=None
):
    """
    Takes a list of local or remote video URLs, downloads remote files temporarily,
    speeds each clip up by 2x, trims to 80% of duration, concatenates them,
    and writes the final video to output_path.
    """

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    clips = []
    temp_files = []  # to track downloaded files

    def download_video(url):
        """Download a remote video file to a temp directory."""
        tmp_dir = tempfile.mkdtemp()
        local_filename = os.path.join(
            tmp_dir, os.path.basename(url.split("?")[0]) or "temp.mp4"
        )

        print(f"Downloading {url}...")
        try:
            with requests.get(url, stream=True, timeout=30) as r:
                r.raise_for_status()
                with open(local_filename, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            print(f"Downloaded to {local_filename}")
            return local_filename
        except Exception as e:
            print(f"Failed to download {url}: {e}")
            return None

    for url in urls:
        try:
            # Download remote URLs
            if url.startswith("http://") or url.startswith("https://"):
                local_path = download_video(url)
                if not local_path:
                    continue
                temp_files.append(local_path)
            else:
                local_path = url

            print(f"Loading clip: {local_path}")
            clip = VideoFileClip(local_path).fx(speedx, factor=2)
            clips.append(clip.subclip(0, clip.duration * 0.8))

        except Exception as e:
            print(f"Skipping '{url}': {e}")

    if not clips:
        print("No valid video clips found. Nothing to stitch.")
        return

    try:
        final_clip = concatenate_videoclips(clips, method="chain")
        final_clip.write_videofile(output_path, codec="libx264", fps=24, audio=False)
        print(f"✅ Video successfully saved to: {output_path}")
    except Exception as e:
        print(f"Error during stitching: {e}")
    finally:
        # Close clips to release file handles
        for clip in clips:
            clip.close()
        if "final_clip" in locals():
            final_clip.close()

        # Cleanup temporary downloaded files
        for f in temp_files:
            try:
                os.remove(f)
                os.rmdir(os.path.dirname(f))
            except Exception:
                pass


# Example usage
if __name__ == "__main__":
    # Example URLs: can be local paths or remote mp4 links
    example_urls = [
        # "https://example.com/video1.mp4",
        # "https://example.com/video2.mp4",
    ]

    output_dir = "video"
    stitch_videos_in_folder(
        example_urls, output_path=os.path.join(output_dir, "output.mp4")
    )

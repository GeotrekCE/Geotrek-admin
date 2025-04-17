import re

from embed_video.backends import UnknownIdException, VideoBackend


class DailymotionBackend(VideoBackend):
    """Backend for Dailymotion URLs."""

    re_detect = re.compile(
        r"^(http(s)?://)?((www\.)?dailymotion.com/.*|dai\.ly/\w+)", re.I
    )

    re_code = re.compile(
        r"""(dailymotion.com/|dai\.ly/)  # match dailymotion's domains
            (embed/)?
            (video/)?  # match the embed url syntax
            (?P<code>\w+)  # match and extract
        """,
        re.I | re.X,
    )
    pattern_url = "{protocol}://www.dailymotion.com/embed/video/{code}"
    pattern_thumbnail_url = "{protocol}://dailymotion.com/thumbnail/embed/video/{code}"

    def get_code(self):
        code = super().get_code()
        if not code:
            raise UnknownIdException(f"Cannot get ID from `{self._url}`")

        return code

#!/usr/bin/python3

"""Merge multiple subtitles together into one."""

import datetime
import operator
import logging
from .. import utils

log = logging.getLogger(__name__)

TOP = r"{\an8}"
BOTTOM = r"{\an2}"


def merge_subs(subs, acceptable_diff, attr, width):
    """
    Merge subs with similar start/end times together (in-place).
    This prevents subtitles from jumping around the screen.

    :param subs: :py:class:`Subtitle` objects
    :param datetime.timedelta acceptable_diff: The amount of milliseconds
                                    a subtitle start time must be to shift.
    :param str attr:
    :param int width: The amount of subtitles to consider for time matching at once.
    :rtype: :term:`generator` of :py:class:`Subtitle` objects
    """
    sorted_subs = sorted(subs, key=operator.attrgetter(attr))

    for subs in utils.sliding_window(sorted_subs, width=width):
        current_sub = subs[0]
        future_subs = subs[1:]
        current_comp = getattr(current_sub, attr)

        for future_sub in future_subs:
            future_comp = getattr(future_sub, attr)
            if current_comp + acceptable_diff > future_comp:
                log.debug(
                    "Merging %d's %s time into %d",
                    future_sub.index,
                    attr,
                    current_sub.index,
                )
                setattr(future_sub, attr, current_comp)
            else:
                # Since these are sorted, and this one didn't match, we can be
                # sure future ones won't match either.
                break


def parse_args():
    examples = {
        "Merge English and Chinese subtitles": "srt mux -i eng.srt -i chs.srt -o both.srt",
        "Merge subtitles with one on top and one at the bottom": "srt mux -t -i eng.srt -i chs.srt -o both.srt",
    }
    parser = utils.basic_parser(
        description=__doc__, examples=examples, multi_input=True
    )
    parser.add_argument(
        "--ms",
        metavar="MILLISECONDS",
        default=datetime.timedelta(milliseconds=600),
        type=lambda ms: datetime.timedelta(milliseconds=int(ms)),
        help="if subs being muxed are within this number of milliseconds "
        "of each other, they will have their times matched (default: 600)",
    )
    parser.add_argument(
        "-w",
        "--width",
        default=5,
        type=int,
        help="how many subs to consider for time matching at once (default: %(default)s)",
    )
    parser.add_argument(
        "-t",
        "--top-and-bottom",
        action="store_true",
        help="use SSA-style tags to place files at the top and bottom, respectively. Turns off time matching",
    )
    parser.add_argument(
        "--no-time-matching",
        action="store_true",
        help="don't try to do time matching for close subtitles (see --ms)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(level=args.log_level)

    utils.set_basic_args(args)

    muxed_subs = []
    for idx, subs in enumerate(args.input):
        for sub in subs:
            if args.top_and_bottom:
                if idx % 2 == 0:
                    sub.content = TOP + sub.content
                else:
                    sub.content = BOTTOM + sub.content
            muxed_subs.append(sub)

    if args.no_time_matching or not args.top_and_bottom:
        merge_subs(muxed_subs, args.ms, "start", args.width)
        merge_subs(muxed_subs, args.ms, "end", args.width)

    output = utils.compose_suggest_on_fail(muxed_subs, strict=args.strict)
    args.output.write(output)


if __name__ == "__main__":  # pragma: no cover
    main()

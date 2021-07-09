#!/usr/bin/python3

"""Remove subtitles by index or timestamp."""

import datetime
import logging
import srt
from . import utils

log = logging.getLogger(__name__)


def split(subs, timestamp):
    """
    Splits subtitles at a given timestamp.

    :param subs: :py:class:`Subtitle` objects
    :param datetime.timedelta timestamp: The timestamp to split subtitles at.
    :rtype: :term:`generator` of :py:class:`Subtitle` objects
    """
    # ensures list compatibility
    from types import GeneratorType

    subs = (x for x in subs) if not isinstance(subs, GeneratorType) else subs

    # yield unsplit captions before the timestamp
    idx = 1
    break_subtitle = None
    split_subs = []
    for subtitle in subs:
        if subtitle.start < timestamp and timestamp < subtitle.end:
            yield srt.Subtitle(idx, subtitle.start, timestamp, subtitle.content)
            subtitle.start = timestamp
            split_subs.append(subtitle)
            idx += 1
        elif subtitle.start == timestamp:
            split_subs.append(subtitle)
        elif subtitle.start > timestamp:
            break_subtitle = subtitle
            break
        else:
            yield subtitle
            idx += 1

    # yield split captions (sort to adjust index first)
    split_subs.sort()
    for subtitle in split_subs:
        yield srt.Subtitle(idx, timestamp, subtitle.end, subtitle.content)
        idx += 1

    # yield unsplit captions after the timestamp
    if break_subtitle:
        yield srt.Subtitle(
            idx, break_subtitle.start, break_subtitle.end, break_subtitle.content
        )
        idx += 1

    for subtitle in subs:
        yield srt.Subtitle(idx, subtitle.start, subtitle.end, subtitle.content)
        idx += 1


def remove_by_timestamp(
    subs,
    timestamp_one=datetime.timedelta(0),
    timestamp_two=datetime.timedelta(0),
    adjust=False,
):
    """
    Removes captions from subtitles by timestamp.
    When timestamp one > timestamp two, captions up to timestamp two will be removed
    and captions after timestamp one will be removed.

    :param subs: :py:class:`Subtitle` objects
    :param datetime.timedelta timestamp_one: The timestamp to remove from.
    :param datetime.timedelta timestamp_two: The timestamp to remove to.
    :param boolean: Whether to adjust the timestamps of non-removed captions.
    :rtype: :term:`generator` of :py:class:`Subtitle` objects
    """
    # ensures list compatibility
    from types import GeneratorType

    subs = (x for x in subs) if not isinstance(subs, GeneratorType) else subs

    # edge cases
    sequential = timestamp_one < timestamp_two
    try:
        first_subtitle = next(subs)
    except StopIteration:
        return

    if timestamp_one == timestamp_two:
        return
    elif sequential and timestamp_two <= first_subtitle.start:
        yield first_subtitle
        yield from subs
        return
    elif not sequential and timestamp_one <= first_subtitle.start:
        return

    # Split the caption at the start and end of the block(s).
    subs = split(subs, timestamp_one)
    subs = split(subs, timestamp_two)

    # remove the captions using a generator.
    adjust_time = timestamp_two if adjust else datetime.timedelta(0)
    idx = 1
    if sequential:
        # keep captions before timestamp one
        if first_subtitle.start < timestamp_one:
            yield first_subtitle
            idx += 1

            for subtitle in subs:
                if timestamp_one <= subtitle.start:
                    break
                yield subtitle
                idx += 1

        # remove captions after timestamp one but before timestamp two
        for subtitle in subs:
            if timestamp_two <= subtitle.start:
                yield srt.Subtitle(
                    idx,
                    subtitle.start - adjust_time,
                    subtitle.end - adjust_time,
                    subtitle.content,
                )
                idx += 1
                break

        # keep captions after timestamp two
        for subtitle in subs:
            yield srt.Subtitle(
                idx,
                subtitle.start - adjust_time,
                subtitle.end - adjust_time,
                subtitle.content,
            )
            idx += 1
    else:
        # remove captions before timestamp two
        if first_subtitle.start < timestamp_two:
            for subtitle in subs:
                if timestamp_two <= subtitle.start:
                    yield srt.Subtitle(
                        idx,
                        subtitle.start - adjust_time,
                        subtitle.end - adjust_time,
                        subtitle.content,
                    )
                    idx += 1
                    break
        else:
            yield srt.Subtitle(
                idx,
                first_subtitle.start - adjust_time,
                first_subtitle.end - adjust_time,
                first_subtitle.content,
            )
            idx += 1

        # keep captions after timestamp two but before timestamp one
        for subtitle in subs:
            if timestamp_one <= subtitle.start:
                break
            yield srt.Subtitle(
                idx,
                subtitle.start - adjust_time,
                subtitle.end - adjust_time,
                subtitle.content,
            )
            idx += 1

        # remove captions after timestamp one
        for subtitle in subs:
            pass


# Command Line Interface
def parse_args():
    examples = {
        "Remove captions within :05 - :08": "srt remove -i example.srt --t1 00:00:5,00 --t2 00:00:8,00",
        "Remove captions non-sequentially": "srt remove -i example.srt --t1 00:00:8,00 --t2 00:00:5,00",
        "Remove captions from :16 to the end of the file.": "srt remove -i example.srt --t1 00:00:16,00",
        "Remove from :00 to :16 and adjust subsequent captions": "srt remove -i example.srt --t2 00:00:16,00",
        "Remove every caption": "srt remove -i example.srt",
    }
    parser = utils.basic_parser(description=__doc__, examples=examples)
    parser.add_argument(
        "--start",
        "--t1",
        metavar=("TIMESTAMP"),
        type=lambda arg: srt.srt_timestamp_to_timedelta(arg),
        default=datetime.timedelta(0),
        nargs="?",
        help="The timestamp to start removing from.",
    )
    parser.add_argument(
        "--end",
        "--t2",
        metavar=("TIMESTAMP"),
        type=lambda arg: srt.srt_timestamp_to_timedelta(arg),
        default=datetime.timedelta(0),
        nargs="?",
        help="The timestamp to stop removing at.",
    )
    parser.add_argument(
        "--at",
        "--adjust",
        action="store_true",
        help="Adjust the timestamps of non-removed captions",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(level=args.log_level)
    utils.set_basic_args(args)
    removed_subs = remove_by_timestamp(args.input, args.start, args.end, args.adjust)
    output = utils.compose_suggest_on_fail(removed_subs, strict=args.strict)
    args.output.write(output)


if __name__ == "__main__":  # pragma: no cover
    main()

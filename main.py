from typing import List

import click
import glob

from sfcreator.sfz import SfzWriter
from sfcreator.soundfont.soundfont import SoundFont, Sample, NoteNameMidiNumberMapper, HighLowKeyDistributor


def list_supported_files(directory):
    return glob.glob(directory + "/*.wav")


@click.group()
def cli():
    pass


@cli.command()
@click.argument('directory')
def sfz(directory: str):
    files = list_supported_files(directory)
    samples: List[Sample] = []
    mapper = NoteNameMidiNumberMapper()
    for file in files:
        samples.append(mapper.mapped_sample(file))
    soundfont = SoundFont(samples)
    HighLowKeyDistributor().distribute(soundfont)
    SfzWriter().write(directory + "/soundfont.sfz", soundfont)


if __name__ == '__main__':
    cli()

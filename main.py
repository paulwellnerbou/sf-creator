import os
from typing import List

import click
import glob

from sfcreator.decentsampler import DecentSamplerWriter
from sfcreator.sfz import SfzWriter
from sfcreator.soundfont.soundfont import SoundFont, Sample, NoteNameMidiNumberMapper, HighLowKeyDistributor


def list_supported_files(directory):
    return glob.glob(directory + "/*.wav")


@click.group()
def cli():
    pass


@cli.command()
@click.argument('directory')
@click.option('--highkey', required=False, type=int, default=108)
@click.option('--lowkey', required=False, type=int, default=21)
@click.option('--instrument', help="name of the instrument", required=False, type=str)
@click.option('--loopmode',
              help="loop mode, no_loop (default), one_shot, loop_continuous or loop_sustain,"
                   " see https://sfzformat.com/opcodes/loop_mode",
              required=False, type=str, default="no_loop")
@click.option('--polyphony',
              help="Polyphony voice limit, see https://sfzformat.com/opcodes/polyphony",
              required=False, type=str, default=None)
def sfz(directory: str, lowkey: int, highkey: int, instrument: str, loopmode: str, polyphony: str):
    soundfont = make_soundfont(directory, highkey, instrument, loopmode, lowkey, polyphony)
    SfzWriter().write(directory, soundfont)


@cli.command()
@click.argument('directory')
@click.option('--highkey', required=False, type=int, default=108)
@click.option('--lowkey', required=False, type=int, default=21)
@click.option('--instrument', help="name of the instrument", required=False, type=str)
@click.option('--image', required=False, type=str)
@click.option('--loopmode',
              help="loop mode, only supported for sfz. For compatibility reasons, --loopmode=one_shot will cause"
                   " --release=20 for decent sampler, to ensure samples are always played until the end.",
              required=False, type=str, default="no_loop")
@click.option('--polyphony',
              help="Polyphony voice limit, not supported in decent sampler format.",
              required=False, type=str, default=None)
def decentsampler(directory: str, lowkey: int, highkey: int, instrument: str, loopmode: str, polyphony: str,
                  image: str):
    soundfont = make_soundfont(directory, highkey, instrument, loopmode, lowkey, polyphony)
    DecentSamplerWriter().write(directory, soundfont, image)


def make_soundfont(directory, highkey, instrument, loopmode, lowkey, polyphony):
    files = list_supported_files(directory)
    samples: List[Sample] = []
    mapper = NoteNameMidiNumberMapper()
    for file in files:
        samples.append(mapper.mapped_sample(file))
    soundfont = SoundFont(samples, loop_mode=loopmode, polyphony=polyphony)
    if instrument is None or len(instrument) == 0:
        soundfont.instrument_name = os.path.basename(os.path.dirname(directory))
    else:
        soundfont.instrument_name = instrument
    HighLowKeyDistributor().distribute(soundfont, low_key=lowkey, high_key=highkey)
    return soundfont


if __name__ == '__main__':
    cli()

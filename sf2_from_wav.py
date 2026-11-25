#!/usr/bin/env python3
"""Create a minimal SF2 bank containing one mono PCM WAV mapped across the keyboard.
Supports uncompressed 8/16-bit mono WAV input. This is a basic conversion utility.
"""
import argparse, struct, wave, os

def ck(tag, payload):
    return tag + struct.pack("<I", len(payload)) + payload

def listck(payload):
    return ck(b"LIST", payload)

def fixed_name(s, n=20):
    return s.encode("ascii", "replace")[:n-1] + b"\0" + b"\0" * (n-len(s.encode("ascii","replace")[:n-1])-1)

def make_sf2(wav_path, out_path, preset_name):
    with wave.open(wav_path, "rb") as w:
        channels, width, rate, frames = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
        if channels != 1 or width not in (1,2) or w.getcomptype() != "NONE":
            raise ValueError("Input WAV must be uncompressed mono 8-bit or 16-bit PCM.")
        raw = w.readframes(frames)
    if width == 1:
        # SF2 samples are signed 16-bit PCM; convert unsigned 8-bit PCM
        pcm = bytes()
        vals = [((b-128)<<8) for b in raw]
        pcm = struct.pack("<"+"h"*len(vals), *vals)
    else:
        pcm = raw
    sample_count = len(pcm)//2
    pcm += b"\0"*46  # SF2 sample guard points

    info = b"INFO"+ck(b"ifil",struct.pack("<HH",2,1))+ck(b"isng",b"EMU8000\0")+ck(b"INAM",preset_name.encode("utf-8","replace")+b"\0")
    sdta = b"sdta"+ck(b"smpl",pcm)

    # Preset header and terminal header
    phdr = fixed_name(preset_name)+struct.pack("<HHHBBH",0,0,0,0,0,0)+fixed_name("EOP")+struct.pack("<HHHBBH",0,0,1,0,0,0)
    pbag = struct.pack("<HH",0,0)+struct.pack("<HH",1,0)
    pmod = b"\0"*10
    pgen = struct.pack("<HH",41,0) # instrument index 0

    inst = fixed_name(preset_name)+struct.pack("<H",0)+fixed_name("EOI")+struct.pack("<H",1)
    ibag = struct.pack("<HH",0,0)+struct.pack("<HH",3,0)
    imod = b"\0"*10
    # instrument zone generators: key range 0-127, sampleID, root key override
    igen = struct.pack("<HH",43,0x7f00)+struct.pack("<HH",53,0)+struct.pack("<HH",58,60)
    shdr = fixed_name("Sample")+struct.pack("<IIIIIBbHH",0,sample_count,0,0,rate,60,0,0,1)+fixed_name("EOS")+struct.pack("<IIIIIBbHH",sample_count,sample_count,sample_count,sample_count,rate,60,0,0,0)
    pdta = b"pdta"+ck(b"phdr",phdr)+ck(b"pbag",pbag)+ck(b"pmod",pmod)+ck(b"pgen",pgen)+ck(b"inst",inst)+ck(b"ibag",ibag)+ck(b"imod",imod)+ck(b"igen",igen)+ck(b"shdr",shdr)
    body = b"sfbk"+listck(info)+listck(sdta)+listck(pdta)
    with open(out_path,"wb") as f: f.write(ck(b"RIFF",body))
    print("Wrote", out_path)

if __name__=="__main__":
    p=argparse.ArgumentParser(description="Basic WAV-to-SF2 converter")
    p.add_argument("wav", help="mono PCM WAV (8-bit or 16-bit)")
    p.add_argument("output", help="output .sf2 filename")
    p.add_argument("--name",default="My SoundFont",help="preset/instrument name")
    a=p.parse_args()
    make_sf2(a.wav,a.output,a.name)

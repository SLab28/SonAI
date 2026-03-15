// SonaiPad — soft pad instrument, sustained and slowly evolving
SynthDef(\SonaiPad, { |freq_hz=220, detune=0.02, cutoff=1200, amp=0.3, dur=30, attack=3.0, release=5.0|
    var osc1 = SinOsc.ar(freq_hz);
    var osc2 = SinOsc.ar(freq_hz * (1 + detune));
    var osc3 = Saw.ar(freq_hz * 0.5, 0.3);
    var mix = (osc1 + osc2 + osc3) / 3;
    var filtered = LPF.ar(mix, cutoff + (SinOsc.kr(0.1) * (cutoff * 0.2)));
    var env = EnvGen.kr(Env.linen(attack, dur - attack - release, release), doneAction: 2);
    Out.ar(0, Pan2.ar(filtered * amp * env, 0));
}).add;

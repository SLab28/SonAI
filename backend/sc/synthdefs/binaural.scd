// SonaiBinaural — stereo binaural beat generator
// Left ear = carrier_hz, Right ear = carrier_hz + beat_hz
SynthDef(\SonaiBinaural, { |carrier_hz=110, beat_hz=40, amp=0.2, dur=60|
    var left = SinOsc.ar(carrier_hz, 0, amp);
    var right = SinOsc.ar(carrier_hz + beat_hz, 0, amp);
    var env = EnvGen.kr(Env.linen(2, dur - 4, 2), doneAction: 2);
    Out.ar(0, [left, right] * env);
}).add;

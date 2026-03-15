// SonaiDrone — sub-bass or fundamental drone, very long sustain
SynthDef(\SonaiDrone, { |freq_hz=55, harmonics=3, amp=0.4, dur=120|
    var sig = SinOsc.ar(freq_hz) * 0.5;
    harmonics.do { |i|
        sig = sig + (SinOsc.ar(freq_hz * (i + 2), 0, 0.3 / (i + 2)));
    };
    var env = EnvGen.kr(Env.linen(5, dur - 10, 5), doneAction: 2);
    Out.ar(0, Pan2.ar(sig * amp * env, 0));
}).add;

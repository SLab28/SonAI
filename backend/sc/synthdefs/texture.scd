// SonaiTexture — filtered noise drone for texture layers
SynthDef(\SonaiTexture, { |density=0.5, brightness=0.5, amp=0.3, dur=30, pan=0|
    var cutoff = brightness.linexp(0, 1, 200, 8000);
    var noise = PinkNoise.ar(1);
    var filtered = LPF.ar(noise, cutoff);
    var grainRate = density.linexp(0, 1, 0.5, 20);
    var trig = Dust.ar(grainRate);
    var grain = filtered * trig.lagud(0.001, 0.05);
    var sig = (filtered * 0.3) + (grain * 0.7);
    var env = EnvGen.kr(Env.linen(3, dur - 6, 3), doneAction: 2);
    Out.ar(0, Pan2.ar(sig * amp * env, pan));
}).add;

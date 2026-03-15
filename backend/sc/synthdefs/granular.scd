// SonaiGranular — granular synthesis cloud from loaded buffer
SynthDef(\SonaiGranular, { |bufNum=0, density=0.5, pitch_var=0.1, dur=30, amp=0.4|
    var grainRate = density.linexp(0, 1, 2, 80);
    var trig = Dust.ar(grainRate);
    var pos = LFNoise1.kr(0.5).range(0, BufDur.kr(bufNum));
    var pitchRatio = 1 + (LFNoise1.kr(2) * pitch_var);
    var sig = GrainBuf.ar(2, trig, 0.1, bufNum, pitchRatio, pos);
    var env = EnvGen.kr(Env.linen(2, dur - 4, 2), doneAction: 2);
    Out.ar(0, sig * amp * env);
}).add;

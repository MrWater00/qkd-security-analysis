# QKD Security Analysis

A small research project on quantum key distribution (QKD) security.

## Plan

1. **BB84 simulation** (done): `bb84.py`
2. **Detector side-channel attack simulation** (planned)
3. **Write-up: why MDI-QKD defends against detector attacks** (planned)

## Step 1: BB84

An idealized BB84 simulation in pure Python (no dependencies). It covers
random bit and basis choice, Bob's measurement, basis sifting, and QBER
estimation, with an optional intercept-resend eavesdropper.

Run it:

```
python bb84.py
```

Typical results (1000 photons):

| Scenario | QBER |
|---|---|
| No eavesdropper | 0% |
| Intercept-resend Eve | ~25% |

## Limitations

This is an idealized model. It has no photon loss, detector noise, error
correction or privacy amplification, and it is not a hardware or
finite-key security analysis.

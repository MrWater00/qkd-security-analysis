# QKD Security Analysis

A hands-on project to understand how quantum key distribution (QKD) works, how real implementations get attacked, and why some protocols defend against those attacks.

**Status:** step 1 of 3 done.

| Step | What | Status |
|---|---|---|
| 1 | BB84 simulation in Python | Done |
| 2 | Detector side-channel attack simulation (detector blinding) | Planned |
| 3 | Short write-up: why measurement-device-independent QKD (MDI-QKD) defends against detector attacks | Planned |

---

## Background

### The problem

Alice and Bob want a shared secret key so they can encrypt messages. Eve can listen to everything on the line between them. Classical key exchange relies on math problems being hard. QKD relies on physics: measuring a quantum state disturbs it.

### Qubits and bases

BB84 sends information in single photons. Each photon is prepared in one of two **bases**:

| Basis | Bit 0 | Bit 1 |
|---|---|---|
| Straight (+) | vertical polarization | horizontal polarization |
| Diagonal (x) | 45 degrees | 135 degrees |

The key rule:

- Measure in the **same** basis the photon was prepared in: you get the correct bit.
- Measure in the **other** basis: you get a random bit (50/50), and the photon's state is destroyed.

Eve cannot copy an unknown quantum state (the no-cloning theorem), so she cannot measure a photon and also pass on an identical one.

### The protocol

1. Alice picks a random bit and a random basis for each photon and sends it.
2. Bob picks a random basis for each photon and measures.
3. Over a public channel, Alice and Bob announce their **bases** (never the bits) and keep only the positions where the bases matched. This is the **sifted key** (about 50% of photons).
4. They sacrifice a random sample of the sifted key and compare it publicly. The fraction of mismatches is the **QBER** (quantum bit error rate).
5. If the QBER is low, the remaining bits become the key. If it is high, they throw the run away.

### Why Eve gets caught

In the intercept-resend attack, Eve measures every photon in a random basis and resends what she saw. Half the time she guesses the wrong basis, which randomizes the photon. For positions where Alice's and Bob's bases match, that gives Bob a wrong bit with probability 1/2 x 1/2 = **25%**. Without Eve the QBER is 0% in this idealized model.

Rule of thumb from the literature: BB84 with standard post-processing tolerates a QBER of roughly 11%. 25% is far above that.

---

## Step 1: BB84 simulation

File: [`bb84.py`](bb84.py). Pure Python 3, standard library only.

### Run it

```
python bb84.py
```

Example output:

```
--- No Eve ---
photons sent : 1000
sifted bits  : 473  (~50% expected)
QBER         : 0.0%
final key    : 379 bits, identical = True

--- With Eve (intercept-resend) ---
photons sent : 1000
sifted bits  : 529  (~50% expected)
QBER         : 22.9%
final key    : 424 bits, identical = False
```

Numbers vary per run because everything is random.

### Use it as a module

```python
from bb84 import run_bb84

result = run_bb84(n=20000, eve=True, seed=1)
print(result["qber"])
```

`run_bb84(n, eve, seed)` returns a dict with `sent`, `sifted`, `sampled`, `qber`, `key_len` and `keys_match`.

### How the code maps to the protocol

| Code | Protocol step |
|---|---|
| `alice_bits`, `alice_bases` | Alice's random bits and bases |
| `measure(bit, prep_basis, meas_basis)` | The physics rule: same basis gives the bit, different basis gives a coin flip |
| `if eve:` block | Intercept-resend attack |
| `bob_bases`, `bob_bits` | Bob's random bases and measurements |
| `keep` list | Sifting |
| `sample_idx`, `qber` | Error estimation on a sacrificed sample |

### Results

Averaged over repeated runs with 20,000 photons:

| Scenario | QBER |
|---|---|
| No eavesdropper | 0% |
| Intercept-resend Eve | about 23% to 27% (theory: 25%) |

The spread comes from the finite sample used to estimate the QBER.

---

## Limitations

This is an idealized model, intended for learning and as a base for the next steps. It does **not** include:

- photon loss or channel noise
- detector dark counts or imperfections
- error correction and privacy amplification, so the final "key" is only a raw key, not a secure one
- finite-key security analysis
- authentication of the classical channel (BB84 needs it, and the simulation assumes it)
- any real hardware

The 25% figure applies to the intercept-resend attack only. Other attacks have different signatures.

---

## Roadmap

### Step 2: Detector side-channel attack

Real security proofs assume perfect devices. Real detectors are not perfect. In a detector-blinding attack, Eve shines bright light at Bob's single-photon detectors so they stop acting as single-photon detectors and instead respond to Eve's classical light pulses. She can then force Bob's detectors to click when and how she chooses, without raising the QBER. The plan is to add a detector model to this simulation and show an attack that keeps the QBER low while Eve learns the key.

### Step 3: Why MDI-QKD defends against it

In measurement-device-independent QKD, Alice and Bob both send photons to an untrusted middle node that performs the measurement and only announces the result. Since no honest party's detector is exposed to Eve's control, detector attacks like blinding stop working. The write-up will explain the protocol, why it removes this class of attacks, and what it costs (rate and distance, extra complexity).

---

## References

- C. H. Bennett and G. Brassard, "Quantum cryptography: Public key distribution and coin tossing", 1984. The original BB84 paper.
- P. W. Shor and J. Preskill, "Simple proof of security of the BB84 quantum key distribution protocol", Physical Review Letters, 2000. Source of the roughly 11% error threshold.
- L. Lydersen et al., "Hacking commercial quantum cryptography systems by tailored bright illumination", Nature Photonics, 2010. Detector blinding on real systems.
- H.-K. Lo, M. Curty and B. Qi, "Measurement-device-independent quantum key distribution", Physical Review Letters, 2012. The MDI-QKD proposal.

## License

Not yet chosen.

"""BB84 quantum key distribution: idealized simulation (no noise, no hardware).

Bases: 0 = straight (+), 1 = diagonal (x)
Rule:  measure in the same basis as prepared -> correct bit
       measure in a different basis           -> random bit (50/50)
"""
import random

N = 1000          # number of photons Alice sends
SAMPLE = 0.2      # fraction of the sifted key sacrificed to estimate QBER


def measure(bit, prep_basis, meas_basis):
    """Simulate measuring one photon."""
    if prep_basis == meas_basis:
        return bit
    return random.randint(0, 1)


def run_bb84(n=N, eve=False, seed=None):
    if seed is not None:
        random.seed(seed)

    # Alice: random bits, random bases
    alice_bits = [random.randint(0, 1) for _ in range(n)]
    alice_bases = [random.randint(0, 1) for _ in range(n)]

    # Photons travel. Each one is (bit, basis) as Alice prepared it.
    photons = list(zip(alice_bits, alice_bases))

    # Eve (optional): intercept-resend. She measures with a random basis,
    # then sends a fresh photon prepared in the basis she used.
    if eve:
        resent = []
        for bit, basis in photons:
            eve_basis = random.randint(0, 1)
            eve_bit = measure(bit, basis, eve_basis)
            resent.append((eve_bit, eve_basis))
        photons = resent

    # Bob: random bases, measures
    bob_bases = [random.randint(0, 1) for _ in range(n)]
    bob_bits = [measure(b, pb, mb) for (b, pb), mb in zip(photons, bob_bases)]

    # Sifting: publicly compare bases only, keep matching positions
    keep = [i for i in range(n) if alice_bases[i] == bob_bases[i]]
    alice_key = [alice_bits[i] for i in keep]
    bob_key = [bob_bits[i] for i in keep]

    # Error check: sacrifice a random sample, compare bits publicly
    k = max(1, int(len(keep) * SAMPLE))
    sample_idx = set(random.sample(range(len(keep)), k))
    errors = sum(alice_key[i] != bob_key[i] for i in sample_idx)
    qber = errors / k

    # Remaining bits are the final raw key
    final_alice = [b for i, b in enumerate(alice_key) if i not in sample_idx]
    final_bob = [b for i, b in enumerate(bob_key) if i not in sample_idx]

    return {
        "sent": n,
        "sifted": len(keep),
        "sampled": k,
        "qber": qber,
        "key_len": len(final_alice),
        "keys_match": final_alice == final_bob,
    }


def report(label, r):
    print(f"--- {label} ---")
    print(f"photons sent : {r['sent']}")
    print(f"sifted bits  : {r['sifted']}  (~50% expected)")
    print(f"QBER         : {r['qber']:.1%}")
    print(f"final key    : {r['key_len']} bits, identical = {r['keys_match']}")
    print()


if __name__ == "__main__":
    report("No Eve", run_bb84(eve=False))
    report("With Eve (intercept-resend)", run_bb84(eve=True))
    # Detection threshold used in practice is roughly 11% QBER.
    # Eve's attack gives ~25%, far above it.

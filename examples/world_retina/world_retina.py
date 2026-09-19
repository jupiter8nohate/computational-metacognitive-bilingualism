from __future__ import annotations

from dataclasses import dataclass
import copy
import numpy as np

# CMB // WORLD RETINA
# Synthetic research prototype only.
#
# PATTERN != PROOF
# PROFILE != PERSON
# MODEL != REALITY
# HUMAN_AGENCY > MACHINE_AUTHORITY

SEED = 8
RNG = np.random.default_rng(SEED)

WORLD_DIMENSIONS = 6
SENSOR_COUNT = 4

SATELLITE = 0
AERIAL = 1
PUBLIC_GROUND = 2
CONSENT_RETINA = 3


@dataclass
class Genome:
    sensor_weights: np.ndarray
    acuity: float
    field_of_view: float
    memory_depth: float
    attention_strength: float
    brain_w1: np.ndarray
    brain_b1: np.ndarray
    brain_w2: np.ndarray
    brain_b2: np.ndarray

    def clone(self) -> "Genome":
        return copy.deepcopy(self)


@dataclass
class Observation:
    signal: np.ndarray
    uncertainty: np.ndarray
    consent_mask: np.ndarray


def make_genome() -> Genome:
    hidden = 18
    return Genome(
        sensor_weights=RNG.uniform(0.1, 1.0, SENSOR_COUNT),
        acuity=float(RNG.uniform(0.2, 0.8)),
        field_of_view=float(RNG.uniform(0.2, 1.0)),
        memory_depth=float(RNG.uniform(0.0, 1.0)),
        attention_strength=float(RNG.uniform(0.1, 1.0)),
        brain_w1=RNG.normal(0, 0.3, (hidden, WORLD_DIMENSIONS * 2)),
        brain_b1=np.zeros(hidden),
        brain_w2=RNG.normal(0, 0.3, (WORLD_DIMENSIONS, hidden)),
        brain_b2=np.zeros(WORLD_DIMENSIONS),
    )


def generate_world() -> np.ndarray:
    world = RNG.beta(2.0, 5.0, WORLD_DIMENSIONS)
    if RNG.random() < 0.25:
        world[int(RNG.integers(0, WORLD_DIMENSIONS - 1))] = RNG.uniform(0.7, 1.0)
    return world


def sensor_profile(sensor: int) -> np.ndarray:
    return np.array([
        [0.95, 0.80, 0.30, 0.65, 0.90, 0.00],
        [0.85, 0.65, 0.70, 0.50, 0.60, 0.00],
        [0.35, 0.45, 0.95, 0.45, 0.20, 0.00],
        [0.00, 0.00, 0.00, 0.00, 0.00, 1.00],
    ])[sensor]


def observe(
    genome: Genome,
    world: np.ndarray,
    retina_consent: bool,
) -> Observation:
    total_signal = np.zeros(WORLD_DIMENSIONS)
    total_weight = np.zeros(WORLD_DIMENSIONS)
    consent_mask = np.ones(WORLD_DIMENSIONS)

    for sensor in range(SENSOR_COUNT):
        if sensor == CONSENT_RETINA and not retina_consent:
            consent_mask[-1] = 0.0
            continue

        sensitivity = sensor_profile(sensor)
        weight = genome.sensor_weights[sensor] * sensitivity
        precision = 0.15 + 0.50 * genome.acuity + 0.35 * genome.field_of_view
        noise_scale = np.clip(0.30 * (1.0 - precision), 0.01, 0.30)
        noisy = np.clip(
            world * sensitivity + RNG.normal(0, noise_scale, WORLD_DIMENSIONS),
            0,
            1,
        )
        total_signal += noisy * weight
        total_weight += weight

    fused = np.divide(total_signal, np.maximum(total_weight, 1e-6))
    uncertainty = np.clip(
        1.0 - total_weight / (total_weight.max() + 1e-6),
        0,
        1,
    )
    fused[-1] *= consent_mask[-1]

    return Observation(
        signal=fused,
        uncertainty=uncertainty,
        consent_mask=consent_mask,
    )


def brain(genome: Genome, observation: Observation) -> np.ndarray:
    input_vector = np.concatenate([observation.signal, observation.uncertainty])
    hidden = np.tanh(genome.brain_w1 @ input_vector + genome.brain_b1)
    hidden *= 1.0 + genome.attention_strength * np.abs(hidden)
    output = genome.brain_w2 @ hidden + genome.brain_b2
    return 1.0 / (1.0 + np.exp(-np.clip(output, -20, 20)))


def score(genome: Genome, episodes: int = 30) -> float:
    error_total = 0.0

    for _ in range(episodes):
        world = generate_world()
        consent = bool(RNG.random() > 0.5)
        observation = observe(genome, world, retina_consent=consent)
        prediction = brain(genome, observation)
        target = world.copy()

        # No consent means no fitness pressure to reconstruct the private signal.
        if not consent:
            target[-1] = prediction[-1]

        error_total += float(np.mean((prediction - target) ** 2))

    compute_cost = (
        0.025 * genome.acuity
        + 0.018 * genome.field_of_view
        + 0.015 * genome.memory_depth
        + 0.020 * genome.attention_strength
        + 0.003 * float(np.sum(genome.sensor_weights))
    )

    return -error_total / episodes - compute_cost


def mutate(parent: Genome) -> Genome:
    child = parent.clone()
    child.sensor_weights = np.clip(
        child.sensor_weights + RNG.normal(0, 0.08, SENSOR_COUNT),
        0,
        2,
    )

    for field in ("acuity", "field_of_view", "memory_depth", "attention_strength"):
        setattr(
            child,
            field,
            float(np.clip(getattr(child, field) + RNG.normal(0, 0.07), 0, 1)),
        )

    for array in (child.brain_w1, child.brain_b1, child.brain_w2, child.brain_b2):
        mask = RNG.random(array.shape) < 0.08
        array += mask * RNG.normal(0, 0.10, array.shape)

    return child


def evolve(
    generations: int = 40,
    population_size: int = 40,
    elites: int = 6,
) -> Genome:
    population = [make_genome() for _ in range(population_size)]

    for generation in range(generations):
        ranked = sorted(population, key=score, reverse=True)
        best = ranked[0]

        if generation % 5 == 0:
            print(
                f"GEN={generation:03d} "
                f"acuity={best.acuity:.3f} "
                f"fov={best.field_of_view:.3f} "
                f"memory={best.memory_depth:.3f} "
                f"attention={best.attention_strength:.3f}"
            )

        next_population = [g.clone() for g in ranked[:elites]]
        while len(next_population) < population_size:
            parent = ranked[int(RNG.integers(0, max(elites, population_size // 2)))]
            next_population.append(mutate(parent))
        population = next_population

    return max(population, key=lambda genome: score(genome, episodes=100))


def demonstrate(genome: Genome) -> None:
    labels = (
        "wildfire",
        "flood",
        "traffic",
        "maritime",
        "vegetation",
        "retinal_marker",
    )
    world = generate_world()
    observation = observe(genome, world, retina_consent=True)
    prediction = brain(genome, observation)

    print("\nCMB://WORLD_RETINA")
    for index, label in enumerate(labels):
        print(
            f"{label:16} true={world[index]:.3f} "
            f"observed={observation.signal[index]:.3f} "
            f"model={prediction[index]:.3f}"
        )


if __name__ == "__main__":
    evolved = evolve()
    demonstrate(evolved)

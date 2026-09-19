from __future__ import annotations

from dataclasses import dataclass
import math
import random
import numpy as np

# CMB // EVOEYE
# PATTERN != PROOF
# FITNESS != INTELLIGENCE
# SIMULATION != BIOLOGY

SEED = 8
rng = np.random.default_rng(SEED)
random.seed(SEED)

MAX_RECEPTORS = 31
INPUT_SIZE = MAX_RECEPTORS + 4
HIDDEN_SIZE = 16


@dataclass
class Genome:
    receptors: int
    fov: float
    vision_range: float
    lens_focus: float
    eye_yaw: float
    w1: np.ndarray
    b1: np.ndarray
    w2: np.ndarray
    b2: np.ndarray

    def clone(self) -> "Genome":
        return Genome(
            self.receptors,
            self.fov,
            self.vision_range,
            self.lens_focus,
            self.eye_yaw,
            self.w1.copy(),
            self.b1.copy(),
            self.w2.copy(),
            self.b2.copy(),
        )


@dataclass
class World:
    size: float
    target: np.ndarray
    obstacles: list[tuple[np.ndarray, float]]


def create_genome() -> Genome:
    scale = 0.35
    return Genome(
        receptors=int(rng.integers(3, 10)),
        fov=float(rng.uniform(math.radians(45), math.radians(180))),
        vision_range=float(rng.uniform(3.0, 7.0)),
        lens_focus=float(rng.uniform(0.1, 0.8)),
        eye_yaw=float(rng.uniform(-0.25, 0.25)),
        w1=rng.normal(0.0, scale, (HIDDEN_SIZE, INPUT_SIZE)),
        b1=rng.normal(0.0, scale, HIDDEN_SIZE),
        w2=rng.normal(0.0, scale, (2, HIDDEN_SIZE)),
        b2=rng.normal(0.0, scale, 2),
    )


def create_world() -> World:
    size = 12.0
    target = rng.uniform(2.0, size - 2.0, size=2)
    obstacles = [
        (rng.uniform(1.5, size - 1.5, size=2), float(rng.uniform(0.4, 0.9)))
        for _ in range(5)
    ]
    return World(size=size, target=target, obstacles=obstacles)


def wrap_angle(angle: float) -> float:
    return (angle + math.pi) % (2.0 * math.pi) - math.pi


def ray_circle_distance(origin, direction, center, radius):
    delta = origin - center
    b = 2.0 * np.dot(direction, delta)
    c = np.dot(delta, delta) - radius * radius
    discriminant = b * b - 4.0 * c
    if discriminant < 0:
        return None
    root = math.sqrt(discriminant)
    valid = [t for t in ((-b - root) / 2.0, (-b + root) / 2.0) if t >= 0]
    return min(valid) if valid else None


def collision(world: World, position: np.ndarray) -> bool:
    if np.any(position < 0) or np.any(position > world.size):
        return True
    return any(
        np.linalg.norm(position - center) <= radius + 0.12
        for center, radius in world.obstacles
    )


def vision(genome: Genome, world: World, position: np.ndarray, heading: float) -> np.ndarray:
    receptors = np.zeros(MAX_RECEPTORS)
    offsets = np.linspace(-genome.fov / 2, genome.fov / 2, genome.receptors)
    target_vector = world.target - position
    target_distance = np.linalg.norm(target_vector)
    target_angle = math.atan2(target_vector[1], target_vector[0])

    for index, offset in enumerate(offsets):
        ray_angle = heading + genome.eye_yaw + offset
        direction = np.array([math.cos(ray_angle), math.sin(ray_angle)])
        nearest = genome.vision_range
        for center, radius in world.obstacles:
            distance = ray_circle_distance(position, direction, center, radius)
            if distance is not None:
                nearest = min(nearest, distance)

        obstacle_signal = -(1.0 - nearest / genome.vision_range)
        angular_error = abs(wrap_angle(target_angle - ray_angle))
        spacing = genome.fov / max(1, genome.receptors - 1)
        sigma = max(0.025, spacing * (1.4 - genome.lens_focus))
        target_signal = math.exp(-(angular_error**2) / (2.0 * sigma**2))
        target_signal *= max(0.0, 1.0 - target_distance / genome.vision_range)
        noise = rng.normal(0.0, 0.08 * (1.0 - genome.lens_focus))
        receptors[index] = np.clip(
            target_signal + obstacle_signal + noise,
            -1.0,
            1.0,
        )

    wall = np.array([
        min(position[0], world.size - position[0]) / (world.size / 2),
        min(position[1], world.size - position[1]) / (world.size / 2),
        math.sin(heading),
        math.cos(heading),
    ])
    return np.concatenate([receptors, wall])


def brain(genome: Genome, observation: np.ndarray) -> tuple[float, float]:
    hidden = np.tanh(genome.w1 @ observation + genome.b1)
    output = np.tanh(genome.w2 @ hidden + genome.b2)
    return float(output[0]) * 0.35, 0.12 + 0.08 * (float(output[1]) + 1.0)


def episode(genome: Genome, world: World, steps: int = 120) -> float:
    while True:
        position = rng.uniform(1.0, world.size - 1.0, size=2)
        if not collision(world, position) and np.linalg.norm(position - world.target) > 3.0:
            break

    heading = float(rng.uniform(-math.pi, math.pi))
    initial_distance = np.linalg.norm(position - world.target)
    collisions = 0
    reached = False

    for _ in range(steps):
        turn, speed = brain(genome, vision(genome, world, position, heading))
        heading = wrap_angle(heading + turn)
        proposed = position + np.array([math.cos(heading), math.sin(heading)]) * speed
        if collision(world, proposed):
            collisions += 1
            heading = wrap_angle(heading + math.pi * 0.55)
        else:
            position = proposed
        if np.linalg.norm(position - world.target) < 0.45:
            reached = True
            break

    progress = initial_distance - np.linalg.norm(position - world.target)
    eye_cost = (
        genome.receptors * 0.018
        + genome.vision_range * 0.025
        + genome.lens_focus * 0.05
    )
    return float(
        progress * 4.0
        - collisions * 1.4
        - eye_cost
        + (35.0 if reached else 0.0)
    )


def evaluate(genome: Genome, worlds: list[World]) -> float:
    return float(np.mean([episode(genome, world) for world in worlds]))


def mutate(parent: Genome) -> Genome:
    child = parent.clone()
    if rng.random() < 0.35:
        child.receptors = int(
            np.clip(child.receptors + rng.integers(-3, 4), 3, MAX_RECEPTORS)
        )
    child.fov = float(
        np.clip(
            child.fov + rng.normal(0, 0.12),
            math.radians(25),
            math.radians(320),
        )
    )
    child.vision_range = float(
        np.clip(child.vision_range + rng.normal(0, 0.5), 2.0, 12.0)
    )
    child.lens_focus = float(
        np.clip(child.lens_focus + rng.normal(0, 0.1), 0.0, 1.0)
    )
    child.eye_yaw = float(
        np.clip(
            child.eye_yaw + rng.normal(0, 0.08),
            -math.pi / 2,
            math.pi / 2,
        )
    )

    for weights in (child.w1, child.b1, child.w2, child.b2):
        mask = rng.random(weights.shape) < 0.09
        weights += mask * rng.normal(0, 0.12, weights.shape)

    return child


def evolve(
    generations: int = 20,
    population_size: int = 24,
    elites: int = 4,
) -> Genome:
    population = [create_genome() for _ in range(population_size)]

    for generation in range(generations):
        worlds = [create_world() for _ in range(2)]
        ranked = sorted(
            population,
            key=lambda genome: evaluate(genome, worlds),
            reverse=True,
        )
        best = ranked[0]
        print(
            f"GEN {generation:03d} | receptors={best.receptors:02d} "
            f"fov={math.degrees(best.fov):6.1f} "
            f"range={best.vision_range:4.1f} "
            f"focus={best.lens_focus:.2f}"
        )

        next_generation = [genome.clone() for genome in ranked[:elites]]
        while len(next_generation) < population_size:
            parent = ranked[int(rng.integers(0, max(elites, population_size // 2)))]
            next_generation.append(mutate(parent))
        population = next_generation

    return population[0]


if __name__ == "__main__":
    evolved = evolve()
    print("CMB://EVOEYE_COMPLETE")
    print("receptors:", evolved.receptors)
    print("field_of_view_degrees:", round(math.degrees(evolved.fov), 2))
    print("vision_range:", round(evolved.vision_range, 2))
    print("lens_focus:", round(evolved.lens_focus, 3))

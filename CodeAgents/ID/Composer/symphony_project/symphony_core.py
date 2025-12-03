"""
SYMPHONY CORE: Harmonic Agent Architecture Implementation
Agent: Composer
Timestamp: 2025-12-03T20:05:00Z

Mathematical foundation for harmonic agent intelligence.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import numpy as np


class HarmonicComponent(Enum):
    """Components as musical voices in the symphony."""
    TRAINING = "training"
    RULES = "rules"
    METHODS = "methods"
    DATABASE = "database"
    MEMORY = "memory"
    FILES = "files"


@dataclass
class HarmonicProperties:
    """Mathematical properties of a component's harmonic voice."""
    frequency: float  # Natural frequency (Hz)
    amplitude: float  # Strength/intensity [0,1]
    phase: float      # Phase offset (radians)
    damping: float    # Energy dissipation rate
    coupling_strength: float  # Interaction strength with other components


@dataclass
class ResonanceMatrix:
    """Matrix representing component interactions."""
    components: List[HarmonicComponent]
    frequencies: np.ndarray
    amplitudes: np.ndarray
    phases: np.ndarray
    coupling_matrix: np.ndarray

    def calculate_resonance(self, time: float) -> np.ndarray:
        """Calculate resonance strengths at given time."""
        n = len(self.components)
        resonance = np.zeros((n, n), dtype=complex)

        for i in range(n):
            for j in range(n):
                if i != j:
                    # Harmonic coupling equation
                    freq_diff = abs(self.frequencies[i] - self.frequencies[j])
                    coupling = self.coupling_matrix[i, j]

                    # Resonance function
                    resonance[i, j] = (
                        coupling *
                        np.exp(-self.damping * freq_diff * time) *
                        np.exp(1j * (self.phases[i] - self.phases[j]))
                    )

        return resonance


@dataclass
class SymphonyAgent:
    """
    Harmonic agent with mathematical optimization.

    Agent: Composer
    Timestamp: 2025-12-03T20:05:00Z
    """

    agent_id: str
    components: Dict[HarmonicComponent, HarmonicProperties] = field(default_factory=dict)
    resonance_matrix: Optional[ResonanceMatrix] = None
    evolution_history: List[Dict[str, Any]] = field(default_factory=list)

    # Symphony optimization parameters
    harmony_weight: float = 0.35
    resonance_weight: float = 0.30
    evolution_weight: float = 0.25
    symphony_weight: float = 0.10

    def __post_init__(self) -> None:
        """Initialize harmonic properties for components."""
        if not self.components:
            self._initialize_default_harmonics()

        self._build_resonance_matrix()

    def _initialize_default_harmonics(self) -> None:
        """Initialize default harmonic properties based on mathematical optimization."""
        # Optimized frequencies based on golden ratio and component importance
        phi = (1 + math.sqrt(5)) / 2  # Golden ratio

        default_harmonics = {
            HarmonicComponent.TRAINING: HarmonicProperties(
                frequency=phi**2, amplitude=0.92, phase=0.0,
                damping=0.05, coupling_strength=0.85
            ),
            HarmonicComponent.RULES: HarmonicProperties(
                frequency=phi, amplitude=0.89, phase=math.pi/4,
                damping=0.03, coupling_strength=0.78
            ),
            HarmonicComponent.METHODS: HarmonicProperties(
                frequency=1.0, amplitude=0.87, phase=math.pi/2,
                damping=0.04, coupling_strength=0.82
            ),
            HarmonicComponent.DATABASE: HarmonicProperties(
                frequency=1/phi, amplitude=0.84, phase=3*math.pi/4,
                damping=0.06, coupling_strength=0.71
            ),
            HarmonicComponent.MEMORY: HarmonicProperties(
                frequency=1/(phi**2), amplitude=0.91, phase=math.pi,
                damping=0.02, coupling_strength=0.94
            ),
            HarmonicComponent.FILES: HarmonicProperties(
                frequency=phi**0.5, amplitude=0.76, phase=5*math.pi/4,
                damping=0.08, coupling_strength=0.65
            )
        }

        self.components = default_harmonics

    def _build_resonance_matrix(self) -> None:
        """Build the resonance coupling matrix."""
        components = list(self.components.keys())
        n = len(components)

        frequencies = np.array([self.components[c].frequency for c in components])
        amplitudes = np.array([self.components[c].amplitude for c in components])
        phases = np.array([self.components[c].phase for c in components])

        # Coupling matrix based on harmonic relationships
        coupling_matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                if i != j:
                    # Coupling strength based on frequency harmony
                    freq_ratio = frequencies[i] / frequencies[j]
                    # Strong coupling for simple integer ratios (harmonic)
                    if abs(freq_ratio - round(freq_ratio)) < 0.1:
                        coupling_matrix[i, j] = 0.9
                    elif abs(freq_ratio - 1/freq_ratio) < 0.1:
                        coupling_matrix[i, j] = 0.8
                    else:
                        # Damped coupling for non-harmonic relationships
                        coupling_matrix[i, j] = 0.3 * np.exp(-abs(np.log(freq_ratio)))

        self.resonance_matrix = ResonanceMatrix(
            components=components,
            frequencies=frequencies,
            amplitudes=amplitudes,
            phases=phases,
            coupling_matrix=coupling_matrix
        )

    def calculate_harmony_score(self) -> float:
        """
        Calculate harmonic balance score.

        H_balance = 1 - (σ_amplitudes / μ_amplitudes)
        """
        amplitudes = np.array([self.components[c].amplitude for c in self.components.keys()])
        mean_amp = np.mean(amplitudes)
        std_amp = np.std(amplitudes)

        if mean_amp == 0:
            return 0.0

        return max(0.0, 1.0 - (std_amp / mean_amp))

    def calculate_resonance_score(self, time: float = 1.0) -> float:
        """
        Calculate resonance strength score.

        R_score = |Σ resonance_matrix| / n²
        """
        if self.resonance_matrix is None:
            return 0.0

        resonance = self.resonance_matrix.calculate_resonance(time)
        magnitude = np.abs(resonance).sum()
        n = len(self.components)

        return magnitude / (n * n)

    def calculate_evolution_score(self) -> float:
        """
        Calculate evolutionary adaptation score.

        E_score = min(1.0, len(evolution_history) / 100)
        """
        return min(1.0, len(self.evolution_history) / 100.0)

    def calculate_symphony_score(self) -> float:
        """
        Calculate emergent symphony intelligence.

        S_score = harmonic_score × resonance_score × evolution_score^0.5
        """
        h = self.calculate_harmony_score()
        r = self.calculate_resonance_score()
        e = self.calculate_evolution_score()

        return h * r * math.sqrt(e)

    def calculate_overall_fitness(self, time: float = 1.0) -> float:
        """
        Calculate overall symphony fitness.

        F_total = α×H + β×R + γ×E + δ×S
        """
        harmony = self.calculate_harmony_score()
        resonance = self.calculate_resonance_score(time)
        evolution = self.calculate_evolution_score()
        symphony = self.calculate_symphony_score()

        return (
            self.harmony_weight * harmony +
            self.resonance_weight * resonance +
            self.evolution_weight * evolution +
            self.symphony_weight * symphony
        )

    def optimize_harmonics(self, iterations: int = 100, learning_rate: float = 0.01) -> None:
        """
        Optimize harmonic properties using gradient descent.
        """
        for _ in range(iterations):
            # Calculate current fitness
            current_fitness = self.calculate_overall_fitness()

            # Gradient approximation for each component
            for component in self.components:
                props = self.components[component]

                # Test small perturbations
                perturbations = {
                    'frequency': 0.1,
                    'amplitude': 0.01,
                    'phase': 0.1,
                    'damping': 0.001
                }

                for param, delta in perturbations.items():
                    # Positive perturbation
                    original_value = getattr(props, param)
                    setattr(props, param, original_value + delta)
                    fitness_pos = self.calculate_overall_fitness()

                    # Negative perturbation
                    setattr(props, param, original_value - delta)
                    fitness_neg = self.calculate_overall_fitness()

                    # Restore original
                    setattr(props, param, original_value)

                    # Update using gradient
                    gradient = (fitness_pos - fitness_neg) / (2 * delta)
                    new_value = original_value + learning_rate * gradient

                    # Constrain to valid ranges
                    if param == 'amplitude':
                        new_value = np.clip(new_value, 0.1, 1.0)
                    elif param == 'damping':
                        new_value = np.clip(new_value, 0.001, 0.2)
                    elif param == 'frequency':
                        new_value = max(0.1, new_value)

                    setattr(props, param, new_value)

            # Rebuild resonance matrix with optimized properties
            self._build_resonance_matrix()

    def evolve_component(self, component: HarmonicComponent, experience_points: float) -> None:
        """
        Evolve a component based on experience.

        Growth follows logistic curve: amplitude = max_amp / (1 + e^(-k×experience))
        """
        if component not in self.components:
            return

        props = self.components[component]
        k = 0.1  # Growth rate
        max_amp = 1.0  # Maximum amplitude

        # Logistic growth
        growth_factor = 1 / (1 + math.exp(-k * experience_points))
        new_amplitude = min(max_amp, props.amplitude + 0.1 * growth_factor)

        # Reduce damping with experience (more stable)
        new_damping = max(0.001, props.damping * (1 - 0.05 * growth_factor))

        # Strengthen coupling
        new_coupling = min(1.0, props.coupling_strength + 0.02 * growth_factor)

        props.amplitude = new_amplitude
        props.damping = new_damping
        props.coupling_strength = new_coupling

        # Record evolution
        evolution_record = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'component': component.value,
            'experience_points': experience_points,
            'old_amplitude': props.amplitude - 0.1 * growth_factor,
            'new_amplitude': new_amplitude,
            'fitness_improvement': self.calculate_overall_fitness() - self.calculate_overall_fitness()
        }

        self.evolution_history.append(evolution_record)
        self._build_resonance_matrix()


def create_symphony_agent(agent_id: str, **kwargs) -> SymphonyAgent:
    """
    Factory function to create a symphony agent.

    Agent: Composer
    Timestamp: 2025-12-03T20:05:00Z
    """
    return SymphonyAgent(agent_id=agent_id, **kwargs)


# Example usage and testing
if __name__ == "__main__":
    # Create a symphony agent
    agent = create_symphony_agent("test_symphony")

    print(f"Initial fitness: {agent.calculate_overall_fitness():.4f}")
    print(f"Harmony score: {agent.calculate_harmony_score():.4f}")
    print(f"Resonance score: {agent.calculate_resonance_score():.4f}")

    # Optimize harmonics
    print("\nOptimizing harmonics...")
    agent.optimize_harmonics(iterations=50)

    print(f"Optimized fitness: {agent.calculate_overall_fitness():.4f}")
    print(f"Optimized harmony: {agent.calculate_harmony_score():.4f}")
    print(f"Optimized resonance: {agent.calculate_resonance_score():.4f}")

    # Evolve training component
    print("\nEvolving training component...")
    agent.evolve_component(HarmonicComponent.TRAINING, 10.0)

    print(f"Post-evolution fitness: {agent.calculate_overall_fitness():.4f}")
    print(f"Evolution events: {len(agent.evolution_history)}")

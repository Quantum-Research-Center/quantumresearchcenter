#!/usr/bin/env python3
"""Build the Quantum Mechanics, Consciousness, and Intelligence course."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from course_builder import METHOD_GUIDE, Course, build

COURSE_TITLE = 'Quantum Mechanics, Consciousness, and Intelligence'
COURSE_SUBTITLE = 'Physical definitions of intelligence and consciousness compatible with quantum theory'
COURSE_ABOUT = 'Quantum mechanics places observation, interaction, and records at the center of physical description, yet never defines what an observer, an intelligent agent, or a conscious system is. This advanced course constructs formal, non-mystical definitions of intelligence and consciousness that remain strictly compatible with unitarity, decoherence, no-signalling, and thermodynamics.'
COURSE_PREREQUISITES = 'Complete <a href="../foundations/index.html">Quantum Foundations</a> and <a href="../interpretations/index.html">Interpretations of Quantum Mechanics</a>, or bring equivalent knowledge of density operators, tensor products, partial traces, decoherence, and projective/POVM measurement. <a href="../information-theory/index.html">Quantum Information Theory</a> is helpful for entropy and channel bounds.'
COURSE_EXTRA = '<p>Ten chapters progress from the observer gap in physics through open quantum systems, decoherence, and thermodynamics of memory to formal definitions of intelligence (Chapter 4) and consciousness (Chapter 9), concluding with biological brains, classical AI, and quantum agents.</p><p>Each chapter includes worked checks, exercises with hints and reasoned solutions, a summary, and primary-source readings. Explanations stay conversational while tying every claim to explicit equations, operational assumptions, and physical bounds.</p><p>Conventions: finite-dimensional examples use normalized kets and left-to-right tensor order; \\(\\ket{\\pm}=(\\ket{0}\\pm\\ket{1})/\\sqrt{2}\\); \\(X, Y, Z\\) denote the Pauli operators; \\(\\operatorname{Tr}\\) denotes the trace; logarithms in entropy are base 2 for bits or natural when noted alongside \\(k_B T\\).</p><p>Read with an assumption ledger: separate what follows from unitary quantum mechanics and thermodynamics from what is a proposed definition or an empirical hypothesis about biological or engineered substrates.</p>'

COURSE = Course(
    root=ROOT,
    title=COURSE_TITLE,
    tagline='Observers, agency, and intrinsic experience',
    subtitle=COURSE_SUBTITLE,
    about=COURSE_ABOUT,
    prerequisites=COURSE_PREREQUISITES,
    extra=COURSE_EXTRA,
    description='Advanced course defining intelligence and consciousness compatible with quantum mechanics: decoherence, thermodynamics of memory, agency, quantum reference frames, integrated information, and artificial quantum agents.',
    resources='<nav class="book-resources" aria-label="Related courses"><a href="../interpretations/index.html">Interpretations of Quantum Mechanics</a><a href="../information-theory/index.html">Quantum Information Theory</a><a href="../foundations/index.html">Quantum Foundations</a></nav>',
    search_example='decoherence, Landauer, intelligence, or consciousness',
    guide=METHOD_GUIDE,
)

if __name__ == '__main__':
    build(COURSE)

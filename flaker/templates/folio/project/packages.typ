// ========================================================
// MODULAR TYPST PACKAGE MANIFEST (packages.typ)
// Preamble hub for vector drawing, math, diagrams, & tables
// ========================================================

// --- 1. Vector Drawing & Graphing (The "TikZ" of Typst) ---
// CeTZ provides a comprehensive TikZ-inspired vector canvas
#import "@preview/cetz:0.5.2"

// Fletcher provides elegant commutative diagrams and state machines
#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge

// --- 2. Advanced Mathematics & Physics Notation ---
// Mathematica/Physics notation: differential forms, matrices, bra-kets
#import "@preview/physica:0.9.8": *

// MiTeX allows writing native LaTeX equations directly inside Typst blocks (optional)
// #import "@preview/mitex:0.2.7": mitex

// --- 3. Flowcharts & Software Architecture Diagrams ---
// Native Mermaid renderer for software flowcharts, sequences, and classes
#import "@preview/merman:0.5.0": mermaid

// --- 4. Advanced Tables & Data Grids ---
// Publication-grade table styling, custom colspans, rowspans, and cell styling
#import "@preview/tablex:0.0.9": tablex, cellx, hlinex, vlinex

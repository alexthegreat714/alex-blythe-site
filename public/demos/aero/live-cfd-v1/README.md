# Live CFD: time-dependent square wake

This independently authored browser example advances density and both momentum
components with a D2Q9 two-relaxation-time lattice Boltzmann scheme. The canvas
colors are recomputed from each new solution, with no tracers, translated images,
interpolated video frames, or prescribed wake shape.

## Case and equations

- Grid 192 × 80; square occupies x=42..53, y=34..45.
- Lattice units dx=dt=1; inlet u=0.065; square side D=12.
- nu=(tau_even-0.5)/3=0.00975; tau_even=0.52925; Re=uD/nu=80.
- tau_odd=0.5+(3/16)/(tau_even-0.5).
- Halfway link bounce-back at the square; solid velocities are zero.
- Zou/He velocity inlet, density-one outlet; periodic cross-stream boundaries.
- Isothermal weakly compressible flow; p=rho/3 in lattice units.
- A small localized cross-stream disturbance breaks initial reflection symmetry.

The collision updates even and odd opposite-direction population pairs separately,
then populations stream to neighboring cells. The scheme approximates isothermal
Navier–Stokes flow at low Mach number. Vorticity uses centered differences; speed
is sqrt(u²+v²); the displayed pressure coefficient is 2(rho-1)/(3 U²).

## Actual calculation, repeated

`wake.bin` is the Float32 distribution field obtained after 12,000 steps of this
solver. The worker resumes it and solves another 12,000 steps, then restores the
checkpoint and repeats. The loop boundary is a restart, not a claim of exact
periodicity. Pause stops time integration. Offscreen/hidden pages stop requesting
steps. Reduced-motion preferences start with a static computed snapshot.

The Excel download and its LaTeX paper describe the separate steady scalar
transport exercise. They do not validate this fluid solver.

## Verification

From the website checkout:

```sh
node scripts/verify-live-cfd.mjs
```

This regenerates the checkpoint and `checks.json` and verifies:

1. D2Q9 weights and uniform-flow preservation.
2. Taylor–Green velocity decay on 32² and 64² periodic lattices. The reference
   amplitude is U exp(-2 nu (2 pi/N)² t). Initial velocity is
   u=-U cos(2 pi x/N) sin(2 pi y/N), v=U sin(2 pi x/N) cos(2 pi y/N).
   U*N and t/N² are held fixed for the comparison. Relative velocity L2 error is
   0.0048612 and 0.0012192. This validates a periodic analytical case, not the wake.
3. The wake for 24,000 steps: finite fields, boundary values, zero solid velocity,
   density bounds, Mach bound, and changing cross-stream velocity.
4. Deterministic restart from the checkpoint. Its SHA-256 is in `checks.json`.

The observed maximum Mach number is about 0.171. This is a coarse teaching
simulation with boundary/domain effects and low-Mach approximation error.
No experimental validation, wake grid independence, drag accuracy, or universal
percentage accuracy is established.

## References

- Zou and He, pressure/velocity and bounce-back boundaries:
  https://arxiv.org/abs/comp-gas/9611001
- Palabos TRT formulation and magic parameter:
  https://unigespc.gitlab.io/palabos/docs/html/d7/d77/classplb_1_1_base_t_r_tdynamics.html

/** Educational constant-density continuity screen, never a CFD prediction. */
export function nozzleScreen(radiusMm: number) {
  if (!Number.isFinite(radiusMm) || radiusMm < 6 || radiusMm > 12) throw new RangeError('Throat radius must be 6–12 mm');
  const areaM2 = Math.PI * (radiusMm / 1000) ** 2;
  const density = 101325 / (287.05 * 300);
  const velocity = 0.01 / (density * areaM2);
  return { radiusMm, areaMm2: areaM2 * 1e6, velocity, density,
    areaRatio: (24 / radiusMm) ** 2, modified: Math.abs(radiusMm - 8) > 1e-8 };
}

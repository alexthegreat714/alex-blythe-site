"""Reproduce the pre-reveal Seo channel friction screen.

This script intentionally reads only VISIBLE_INPUT_PACKET.json and does not
contain the publication correlation or any result-bearing source values.
"""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
packet = json.loads((ROOT / "VISIBLE_INPUT_PACKET.json").read_text(encoding="utf-8"))
g = packet["geometry"]
fluid = packet["fluids"]
op = packet["operating_condition"]

rho = float(fluid["density_kg_m3"])
mu = float(fluid["dynamic_viscosity_Pa_s"])
re = float(op["hot_reynolds"])
dh = float(g["hydraulic_diameter_m"])
length = float(g["straight_flow_length_m"])
area = float(g["hot_free_flow_area_m2"])
plates = int(packet["configuration"]["hot_plates"])
channels_per_plate = int(packet["configuration"]["channels_per_plate"])

velocity = re * mu / (rho * dh)
mass_flux = rho * velocity
fanning = 16.0 / re
pressure_drop = 4.0 * fanning * length * mass_flux**2 / (2.0 * dh * rho)
total_mass_flow = rho * velocity * area
per_channel_mass_flow = total_mass_flow / (plates * channels_per_plate)
dh_from_area = 4.0 * area * length / float(g["hot_effective_heat_transfer_area_m2"])

result = {
    "Re": re,
    "hydraulic_diameter_reconstructed_m": dh_from_area,
    "hydraulic_diameter_source_m": dh,
    "velocity_m_s": velocity,
    "mass_flux_kg_m2_s": mass_flux,
    "fanning_friction_factor": fanning,
    "channel_pressure_drop_Pa": pressure_drop,
    "total_hot_mass_flow_kg_s": total_mass_flow,
    "per_hot_channel_mass_flow_kg_s": per_channel_mass_flow,
}
print(json.dumps(result, indent=2, sort_keys=True))

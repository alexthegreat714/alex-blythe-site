# HX-02 ambiguity register

| ID | Severity | Topic | Status | Consequence |
|---|---|---|---|---|
| A-01 | BLOCKING | 3-D manifold/header topology | UNRESOLVED | Core and port losses/flow distribution cannot be reconstructed. |
| A-02 | BLOCKING | Pressure measurement stations | UNRESOLVED | A CFD pressure span could use the wrong measurement plane. |
| A-03 | BLOCKING | Thermal measurement definition | UNRESOLVED | Bulk temperatures and heat duty cannot be mapped exactly. |
| A-04 | BLOCKING | Wall material and properties | UNRESOLVED | CHT/wall-temperature prediction would require an invented model. |
| A-05 | MAJOR | Effective area and hydraulic diameter | Rounded-source mismatch | Printed values remain authoritative until the custodian clarifies definitions. |
| A-06 | MAJOR | Matched operating-point records | PARTIAL | Unmatched conditions must not be compared. |

Blocking ambiguities remain open. No geometry, boundary condition, material model, or acceptance criterion is silently invented.

# Microduck cable review

Complete as a local engineering review; not a manufacturing or power-up release.

- Five actual published-mesh views with 16 saved cable solids, shown without proxy context boxes.
- Offline English/Chinese HTML guide with five embedded PNGs, PDF, and 23-row connection list.
- Exact cable STL vertices independently compared with overlay JSON: 16/16 match.
- Chrome offline rendering and PDF export pass; five PNGs decoded and checked nonblank; local guide links and ten copied PCB-source hashes pass.
- Public HAT footprint pin nets read back from pinned KiCad source and compared against the connector record.
- JLC appendix identifies official HAT Gerber/BOM/POS and the separate unprototyped replica IMU source. No replica IMU manufacturing exports exist in the pinned clean clone.

Open physical issues are preserved: actual board/connector identity; 49.75 mm historical J14 projection mismatch; missing/failed routes; all wire cut lengths; flexible cable motion/clearance; servo voltage mismatch; HAT DRC 40 errors and 9 warnings. No external upload, message, quote submission, order or hardware operation.

Root owns final integration into the next immutable Microduck release and commit/push. Review-C was not modified.

Added `Compare the three versions.html` and PDF: seven bilingual comparison rows covering our reconstruction, the pinned community replica and the commercial original; current XL330 choice and unadopted HD-1910-C001 candidate explicitly separated. Local official source hashes in VERSION COMPARISON.json. Offline Chrome comparison render/PDF checked (seven rows, no browser errors). Generator: tools/build_version_comparison.py.

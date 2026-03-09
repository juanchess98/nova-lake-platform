# Stabilization Notes (Module 1)

This document captures the initial integration issues encountered while making NovaLake fully operational on Windows + Docker + Git Bash, and how each issue was resolved.

References:
- architecture index: `docs/architecture.md`
- Module 1 formal architecture: `docs/architecture/module_01_lakehouse_foundation.md`
- ADRs: `docs/decisions.md`

## Summary

The foundation architecture was correct, but multiple runtime/tooling edge cases had to be solved for a smooth local developer experience. These were mostly environment integration issues rather than data-model design issues.

## Issues Encountered and Resolutions

1. Docker engine unavailable (`dockerDesktopLinuxEngine` / pipe errors)
- Symptom: image pull/build failed with daemon connection errors.
- Cause: Docker Desktop engine not running.
- Resolution: explicit startup verification (`docker version`, `docker context ls`) added to runbook guidance.

2. Spark image tag not found (`bitnami/spark:3.5.1`)
- Symptom: compose pull failed with manifest not found.
- Cause: upstream tag no longer available.
- Resolution: migrated to `apache/spark:3.5.1` base and explicit master/worker commands.

3. `spark-submit` not found in PATH
- Symptom: `exec: "spark-submit": executable file not found`.
- Cause: binary not on PATH in selected image.
- Resolution: standardized explicit binary path `/opt/spark/bin/spark-submit`.

4. Git Bash Linux path rewriting
- Symptom: `/opt/...` converted to `C:/Program Files/Git/opt/...`.
- Cause: MSYS path conversion.
- Resolution: scripts now set `MSYS_NO_PATHCONV=1`.

5. Python package import path (`ModuleNotFoundError: core`)
- Symptom: Spark job could not import internal modules.
- Cause: project root not in Python path during job execution.
- Resolution: `PYTHONPATH=/opt/novalake` added in compose services.

6. Iceberg classes not found at runtime
- Symptom: `ClassNotFoundException: org.apache.iceberg.spark.SparkCatalog`.
- Cause: runtime dependency retrieval was fragile.
- Resolution: custom Spark image with Iceberg runtime jar pre-bundled.

7. Derby metastore lock contention (`XSDB6`)
- Symptom: Spark SQL startup error due to `metastore_db` lock.
- Cause: default Hive metastore behavior in CLI sessions.
- Resolution: SQL wrappers enforce `spark.sql.catalogImplementation=in-memory`.

8. Jupyter Lab startup failures
- Symptom: lab container up but UI unreachable or immediate container exit.
- Causes:
  - entrypoint mismatch with Spark base image
  - missing permissions for `/home/spark`
  - dependency pin incompatibility (`pandas==2.2.3`)
  - missing `pyspark` in notebook kernel
- Resolution:
  - lab-specific entrypoint forcing `jupyter lab`
  - home/runtime directory creation and ownership fix
  - compatible package versions
  - dedicated `PySpark (NovaLake)` kernel spec preconfigured for Iceberg catalog.

## Outcome

- Reproducible local platform with Spark + Iceberg + Postgres services.
- Reliable CLI and notebook UX for exploration.
- Cleaner and more portable operational scripts for Windows and Unix-like shells.

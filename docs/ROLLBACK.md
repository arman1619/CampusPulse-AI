# Rollback

CampusPulse uses a blue-green rollback model. Version A remains live while Version B is built, pushed and deployed to the inactive environment. If Version B fails health/smoke checks **before** the switch, the pipeline does not move production traffic; this is failure containment rather than a rollback.

After a successful switch, the previous healthy environment is retained. If production verification shows a regression, run the CNAME swap in the reverse direction using `scripts/aws-rollback.sh` or `scripts/aws-rollback.ps1`, then verify the restored environment. The failed version remains identifiable through its immutable image/application-version tag for diagnosis.

```text
Version A healthy
      ↓
Version B deployed to inactive environment
      ↓
B health/smoke verification
  ↙ fail          ↘ pass
A stays active     swap traffic
                       ↓
                 production verify
                  ↙ fail   ↘ pass
              swap back     complete
                 to A
```

A safe local simulation is provided by `scripts/local-rollback-simulation.sh`. It demonstrates the control decision without falsely claiming AWS network traffic was changed. Database migrations used with blue-green releases must be backward compatible while A and B can coexist.

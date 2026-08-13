CampusPulse AI Terraform syntax correction

Purpose:
- Replaces malformed single-line HCL blocks in the original release.
- Defaults AWS region to eu-west-2 (London).
- Uses cost-aware initial settings: t3.small, db.t4g.micro, blue only, CodeBuild small.
- Blue-green remains supported; enable it later for assessment evidence.

Copy these files into:
D:\CAMPUSPULSE-AI\infrastructure\terraform\
replacing files of the same names.

Do not place HF_TOKEN in any .tf or .tfvars file committed to Git.

# Windows 11 / RTX 5080 inference

On September 29, 2026, the pinned Qwen3.5-9B Q4_K_M model and llama.cpp b11149
Windows CUDA 13.4 runtime were downloaded to this PC and verified against the
committed sizes and SHA-256 checksums. The server loaded on the RTX 5080 and
served a structured generation through the application's own model transport.
The model endpoint is `http://127.0.0.1:8101`. Remote evaluation from the Mac
has not yet been tested.

The Mac retains the app, Docker tools, database, and evidence. The intended PC
role is model inference only, listening on `127.0.0.1:8101` and reached from the
Mac through an SSH tunnel on a separate local port, `127.0.0.1:8102`.

## Run on the PC

From the repository root in PowerShell:

```powershell
.\.venv\Scripts\python.exe scripts\pc\model_server.py setup   # First time; ~6.3 GB
.\.venv\Scripts\python.exe scripts\pc\model_server.py serve   # Keep this window open
```

In another PowerShell window:

```powershell
.\.venv\Scripts\python.exe scripts\pc\model_server.py probe
```

`setup` resumes interrupted downloads, checks their pinned sizes and SHA-256
digests, and installs the verified ZIP contents under ignored `artifacts/`.
`serve` checks those files again, binds only to loopback, and loads 99 GPU layers.
The probe checks the model alias, server build, GGUF path, context, tokenization,
and a small structured completion through `agentguard.model.LocalModel`. Stop a
foreground server with Ctrl+C. The server does not start automatically after a
reboot. On this PC the measured initial load used about 6.8 GB of GPU memory;
the six-token probe completed in about 0.35 seconds after load.

## Mac connection still to do

- [OpenSSH bootstrap](../scripts/pc/bootstrap-ssh.ps1), based on Microsoft's
  [installation](https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse)
  and [administrator key-management](https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_keymanagement)
  instructions. It requires an elevated PowerShell window as the intended PC
  administrator and a trusted Private LAN. It preserves existing keys, adds the
  supplied public key, and restricts the standard SSH firewall rule to the
  private local subnet. It does not open the model HTTP port.
- [Runtime asset pins](../config/pc-windows-runtime.json) for the official
  [llama.cpp b11149 Windows CUDA 13.4 release](https://github.com/ggml-org/llama.cpp/releases/tag/b11149).
  The executable and CUDA dependency archives total approximately 573 MB.
  The archives and GPU execution have now been verified on this PC with driver
  610.47. This is a runtime observation, not a general driver compatibility claim.
- A dedicated SSH key in the ignored `artifacts/pc-inference/` directory on the
  original Mac. The private key stays on the Mac and is excluded from Git.
  `bootstrap-ready.ps1` in that directory contains the public key and is ready
  to paste into an elevated PowerShell window on the PC.

The PowerShell bootstrap has been reviewed against the documentation but has
not been executed or syntax-checked by PowerShell on this Mac.

## Connect the Mac application

1. On the PC, paste/run `artifacts/pc-inference/bootstrap-ready.ps1` from the Mac
   in **PowerShell as Administrator**. If it reports a Public network, mark the
   trusted home LAN Private in Windows Network settings, then rerun.
2. Record its SSH username, LAN IPv4 address, Ed25519 host-key fingerprint, and
   `nvidia-smi` GPU/driver/memory output. No password or private key is needed
   in chat. Compare the PC's host-key fingerprint when first connecting.
3. Connect with the dedicated key and verify the host-key fingerprint. The model
   and runtime are already installed on this PC; run the probe again after the
   SSH tunnel is established.
4. Implement and test the remote inference preflight before running an eval.
   The current local preflight intentionally requires local model/runtime files
   and an exact local server path; an SSH tunnel alone does not satisfy it.
   Do not remove those checks or label a remote server as locally verified.
5. Freeze a fresh development comparison with the remote model and runtime
   evidence. Preserve the Mac studies and their source fingerprints. Validate
   decision correctness and useful effects before a new 400-trial release study.

The bootstrap grants key access under Windows' administrator-account OpenSSH
convention. Stop the `sshd` service and remove this project's public-key line
from `C:\ProgramData\ssh\administrators_authorized_keys` when that access is no
longer wanted. Leave unrelated authorized keys intact.

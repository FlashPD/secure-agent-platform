# Windows 11 / RTX 5080 handoff

PC setup is deferred until the next session. No connection to the PC, Windows
installation, CUDA execution, or remote evaluation has been performed.

The Mac retains the app, Docker tools, database, and evidence. The intended PC
role is model inference only, listening on `127.0.0.1:8101` and reached from the
Mac through an SSH tunnel on a separate local port, `127.0.0.1:8102`.

## Prepared now

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
  Their SHA-256 digests and byte sizes came from the release metadata. They have
  not been downloaded or tested on the PC; driver compatibility is unverified.
- A dedicated SSH key in the ignored `artifacts/pc-inference/` directory on the
  original Mac. The private key stays on the Mac and is excluded from Git.
  `bootstrap-ready.ps1` in that directory contains the public key and is ready
  to paste into an elevated PowerShell window on the PC.

The PowerShell bootstrap has been reviewed against the documentation but has
not been executed or syntax-checked by PowerShell on this Mac.

## Next session

1. On the PC, paste/run `artifacts/pc-inference/bootstrap-ready.ps1` from the Mac
   in **PowerShell as Administrator**. If it reports a Public network, mark the
   trusted home LAN Private in Windows Network settings, then rerun.
2. Record its SSH username, LAN IPv4 address, Ed25519 host-key fingerprint, and
   `nvidia-smi` GPU/driver/memory output. No password or private key is needed
   in chat. Compare the PC's host-key fingerprint when first connecting.
3. Connect with the dedicated key, verify hardware and driver compatibility,
   then install the checksum-pinned CUDA runtime and verify GPU offload.
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

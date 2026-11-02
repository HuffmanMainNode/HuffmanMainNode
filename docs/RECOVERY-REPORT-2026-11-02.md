# Ecosystem Recovery and GitHub Verification Report

**Review date:** 2026-11-02  
**Scope:** Four public repositories in the Halloween 2026 workstream.

This is a public-safe engineering report. It does not include local databases, credentials, private keys, private user data, or private incident details.

## Default-branch state

| Repository | Main commit at review | License | Root changelog | Root security policy | CI |
|---|---|---|---|---|---|
| [Open-Swarm](https://github.com/HuffmanMainNode/-Open-Swarm) | `677df8a085907761d9201a94bcddac156a7d1a23` | MIT | Yes | Yes | Green on Python 3.11-3.13 |
| [HCO](https://github.com/HuffmanMainNode/Huffman-Cyber-Observatory) | `273dcbe03ea634907bc6570f2dee9bdc2c8b4fdc` | MIT | Yes | Yes | Green on Python 3.11-3.13 after both Actions updates merged |
| [Halloween OSINT](https://github.com/HuffmanMainNode/Halloween-OSINT-2026) | `be84ebb5aeb97ed2d891151d613d36f95dd4ddd8` | Apache-2.0 | Yes | Yes | Green on Python 3.11-3.13 |
| [OIX](https://github.com/HuffmanMainNode/Open-Intelligence-Exchange) | `f37cf58447ed30b36660a45ec223644fb7dfac38` | MIT | Yes | Yes | Green on Python 3.11-3.13 |

## Recovery and remediation merged

### Open-Swarm
- Restored postponed annotations and fixed the import-time crash.
- Added lease IDs, stale-worker rejection, lease-expiry exhaustion, and audit events.
- Added approval/rejection state and CLI operations, including migration of legacy unapproved queued tasks.
- Hardened Ollama URL validation and POSIX queue-state permissions.
- Added Python 3.11-3.13 CI, CLI demo smoke coverage, and engineering/security documentation.
- Closed historical PR #1 without merging it because it contained a superseded, less-hardened snapshot. The old branch remains as history.

### Huffman Cyber Observatory
- Fixed scan-root-relative directory exclusions.
- Added scan coverage counts, redacted candidate reporting, and expanded token/private-key patterns.
- Hardened Ed25519 private-key file creation.
- Updated SBOM/KEV documentation and added CLI regression tests.
- Merged Dependabot's checkout v7 update after all three Python matrix jobs passed.
- Merged setup-python v7 on a fresh branch after the stale Dependabot branch conflicted; all three Python matrix jobs passed before merge.

### Halloween OSINT 2026
- Added public-hostname SSRF protections and connects to the validated address with the original hostname as TLS SNI.
- Added optional MCP root scoping, symlink containment checks, and output overwrite protection.
- Added malformed JSON-RPC handling and synchronized version reporting.
- Documented EVM inspection as CLI-only and clarified the earlier duplicated commit message in the changelog.
- Confirmed Apache-2.0 remains the repository license.

### Open Intelligence Exchange
- Enforced receiver-side TTL bounds and recipient verification.
- Added capability checks and durable SQLite replay protection with connection closure and atomic duplicate rejection.
- Hardened private-key file creation and updated threat-model and durable-replay documentation.
- The standalone two-process example still uses the in-memory replay cache; the optional SQLite cache is available as a library component.

## Integration demonstration

A synthetic integration demo is included at [examples/ecosystem_demo.py](../examples/ecosystem_demo.py). It tests:

1. OIX signed task request, recipient check, capability authorization, and durable replay rejection.
2. Open-Swarm task persistence, explicit approval fixture, and successful mock-worker completion.
3. Halloween MCP creation of a SHA-256 evidence manifest under a configured root.
4. HCO Ed25519 signing and verification of the manifest bytes.
5. OIX signed evidence receipt containing the manifest digest.

The demo uses only temporary synthetic data, local in-process calls, a mock adapter, and temporary keys. It is not a production transport, interactive approval service, or proof of real-world evidence authenticity. The profile-repository PR workflow passed Ruff, Bandit, pytest, and the executable demo on Python 3.11, 3.12, and 3.13 (run `41376947667`, commit `9cbc32f39a5b6b1972899666091ba7ded449212a`).

## Outstanding / not verified

- Local clones, working-tree changes, stashes, unpushed commits, cloud workspace state, and any local `.openswarm/state.sqlite3` were not accessible during this GitHub-only review. Those remain unverified and cannot be recovered from GitHub alone.
- HCO optional non-interactive passphrase input remains deferred.
- OIX network transport, key rotation/revocation, encrypted private-key storage, and full RFC 8785 canonicalization remain out of scope.
- Open-Swarm OIX bridge, distributed scheduling, multi-tenant isolation, and OS-level sandbox remain unimplemented.
- Halloween EVM RPC is CLI-only; MCP root confinement is active only when configured.
- Repository descriptions/topics and the leading hyphen in `-Open-Swarm` were not changed.
- No v0.1.x tags or signed release bundles have been created.
- No independent third-party security audit or certification has been performed.

## Commit provenance

The GitHub commits and Actions runs are the evidence of pushed source state. This report intentionally does not claim that local-only artifacts were recovered. See each repository's commit history and Actions page for the live, current state.


## Ecosystem task status

- **E1, umbrella index:** implemented in the public [HuffmanMainNode profile repository](https://github.com/HuffmanMainNode/HuffmanMainNode), PR #1. It adds a repository index, architecture diagram, license table, limitations, and links to the demo and this report.
- **E2, shared core:** decision documented. No shared package extracted because OIX identity signing, HCO artifact signing, and the two manifest schemas have different contracts. The demo verifies the actual cross-project boundary by signing the Halloween manifest bytes with HCO and carrying its digest in an OIX receipt.
- **E3, end-to-end demo:** implemented with synthetic data and passed the three-version CI matrix. This is an in-process proof, not a networked deployment or production bridge.
- **E4, releases:** changelogs exist, but no v0.1.x tags, release bundles, SBOM-attached releases, or published checksums have been created.
- **E5, licensing/governance:** current per-repository licenses are documented and retained. No retroactive relicensing was performed.
- **E6, NIST mapping:** optional and not implemented.

## Pull-request cleanup

- Open-Swarm PR #1 was closed as superseded, not merged. PRs #2 and #3 were merged.
- HCO Dependabot PR #1 and rebased PR #6 were merged after all three Python matrix jobs passed. The stale original Dependabot PR #2 was closed after it conflicted with the first update.
- Halloween PR #1 was merged.
- OIX PRs #1 and #2 were merged.
- The umbrella index/demo was merged through [HuffmanMainNode PR #1](https://github.com/HuffmanMainNode/HuffmanMainNode/pull/1), producing main commit `0a22a7ce4e699b713bd1e10a52d7cab4ef5f1ce4`. Its synthetic integration workflow passed Ruff, Bandit, pytest, and the executable demo on Python 3.11, 3.12, and 3.13 before merge.

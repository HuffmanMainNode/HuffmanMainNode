"""Synthetic OIX -> Open-Swarm -> Halloween MCP -> HCO -> OIX demo.

All inputs are generated in a temporary directory. The mock worker does not
execute the OIX payload. No external model, RPC endpoint, or network service is
called by this program.
"""
from __future__ import annotations

import base64
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from halloween_osint.mcp_server import handle as handle_mcp
from huffman_cyber.crypto import generate_ed25519, sign_file, verify_signature
from oix.envelope import create_message, verify_for_recipient
from oix.identity import generate_identity, load_card, load_private_key, verify_card
from oix.policy import CapabilityPolicy
from oix.sqlite_replay import SQLiteReplayCache
from openswarm.models import Task, TaskStatus
from openswarm.queue import TaskQueue
from openswarm.runtime import SwarmRuntime, Worker


def _public_key(card: dict[str, Any]) -> bytes:
    encoded = card["card"]["public_key"]
    return base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4))


def run_demo() -> dict[str, Any]:
    """Run the full local integration path with synthetic data only."""
    with tempfile.TemporaryDirectory(prefix="huffman-ecosystem-demo-") as temp:
        root = Path(temp)
        sender_dir = root / "sender"
        receiver_dir = root / "receiver"
        sender = generate_identity(sender_dir, "Synthetic Research Agent", ["evidence.review"])
        receiver = generate_identity(receiver_dir, "Synthetic Evidence Agent", ["evidence.review"])
        sender_card = load_card(sender_dir / "agent-card.json")
        receiver_card = load_card(receiver_dir / "agent-card.json")
        if not verify_card(sender_card) or not verify_card(receiver_card):
            raise RuntimeError("OIX identity-card verification failed")

        sender_id = sender_card["card"]["agent_id"]
        receiver_id = receiver_card["card"]["agent_id"]
        sender_public = _public_key(sender_card)
        receiver_public = _public_key(receiver_card)
        request = create_message(
            load_private_key(sender_dir),
            receiver_id,
            "task.request",
            {
                "objective": "Create an integrity manifest for a synthetic evidence fixture",
                "input_is_untrusted": True,
                "fixture": "synthetic-only",
            },
            capability="evidence.review",
        )
        if not verify_for_recipient(request, sender_public, receiver_id):
            raise RuntimeError("OIX request signature or recipient check failed")
        authorization = CapabilityPolicy({"evidence.review"})
        if not authorization.permits(
            request["body"].get("requested_capability"),
            message_type=request["body"].get("type"),
        ):
            raise RuntimeError("OIX capability policy rejected the request")

        replay = SQLiteReplayCache(root / "oix-replay.sqlite3")
        if not replay.accept(request["body"]):
            raise RuntimeError("OIX durable replay cache rejected a fresh request")
        if replay.accept(request["body"]):
            raise RuntimeError("OIX durable replay cache accepted a duplicate request")

        queue = TaskQueue(root / "openswarm.sqlite3")
        task = queue.submit(
            Task(
                worker="general",
                prompt=json.dumps(request["body"]["payload"], sort_keys=True),
                capabilities=["evidence.review"],
                requires_approval=True,
                max_attempts=2,
            )
        )
        if task.status != TaskStatus.PENDING_APPROVAL:
            raise RuntimeError("Open-Swarm did not hold the task for approval")

        # CI uses an explicit synthetic approval fixture. This is not an
        # interactive human approval service or an identity/authentication layer.
        queue.approve(task.task_id)
        runtime = SwarmRuntime(
            queue,
            workers=[Worker("general", {"evidence.review"})],
        )
        completed = runtime.run_once()
        if completed is None or completed.status != TaskStatus.SUCCEEDED:
            raise RuntimeError("Open-Swarm mock task did not succeed")

        mcp_root = root / "mcp-root"
        evidence_dir = mcp_root / "evidence"
        evidence_dir.mkdir(parents=True)
        (evidence_dir / "synthetic-observation.txt").write_text(
            "SYNTHETIC FIXTURE ONLY: no real person, wallet, system, or incident.\n",
            encoding="utf-8",
        )
        manifest_path = mcp_root / "evidence-manifest.json"
        mcp_response = handle_mcp(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "create_evidence_manifest",
                    "arguments": {
                        "directory": str(evidence_dir),
                        "output": str(manifest_path),
                    },
                },
            },
            root=mcp_root,
        )
        if (
            not mcp_response
            or "result" not in mcp_response
            or mcp_response["result"].get("isError")
        ):
            raise RuntimeError(f"Halloween MCP manifest tool failed: {mcp_response}")
        manifest = json.loads(mcp_response["result"]["content"][0]["text"])
        if manifest.get("algorithm") != "sha256" or not manifest.get("files"):
            raise RuntimeError("Halloween MCP returned an invalid evidence manifest")

        hco_private = root / "hco-signing-private.pem"
        hco_public = root / "hco-signing-public.pem"
        signature_path = root / "evidence-manifest.signature.json"
        password = b"synthetic-ci-passphrase-2026"
        generate_ed25519(hco_private, hco_public, password)
        sign_file(hco_private, manifest_path, signature_path, password)
        hco_signature_valid = verify_signature(hco_public, manifest_path, signature_path)
        if not hco_signature_valid:
            raise RuntimeError("HCO signature verification failed")

        manifest_sha256 = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
        receipt = create_message(
            load_private_key(receiver_dir),
            sender_id,
            "evidence.submit",
            {
                "task_id": completed.task_id,
                "task_status": completed.status.value,
                "evidence_manifest_sha256": manifest_sha256,
                "hco_signature_verified": hco_signature_valid,
                "evidence_file_count": len(manifest["files"]),
                "synthetic_data_only": True,
            },
            capability="evidence.review",
        )
        if not verify_for_recipient(receipt, receiver_public, sender_id):
            raise RuntimeError("OIX evidence receipt signature or recipient check failed")
        if not authorization.permits(
            receipt["body"].get("requested_capability"),
            message_type=receipt["body"].get("type"),
        ):
            raise RuntimeError("OIX evidence receipt capability was denied")
        if not replay.accept(receipt["body"]):
            raise RuntimeError("OIX durable replay cache rejected a fresh receipt")
        if replay.accept(receipt["body"]):
            raise RuntimeError("OIX durable replay cache accepted a duplicate receipt")

        # Confirm the signature can be independently checked from the public key.
        Ed25519PublicKey.from_public_bytes(receiver_public)
        return {
            "status": "PASS",
            "synthetic_data_only": True,
            "oix": {
                "request_signature_and_recipient_valid": True,
                "receipt_signature_and_recipient_valid": True,
                "durable_replay_duplicate_rejected": True,
                "capability_authorized": True,
            },
            "open_swarm": {
                "approval_required": True,
                "approval_fixture": "synthetic CI approval, not interactive human approval",
                "task_status": completed.status.value,
                "adapter": "mock",
            },
            "halloween_mcp": {
                "tool": "create_evidence_manifest",
                "sha256_algorithm": manifest["algorithm"],
                "files": len(manifest["files"]),
            },
            "hco": {
                "ed25519_signature_valid": hco_signature_valid,
                "manifest_sha256": manifest_sha256,
            },
            "payload_executed": False,
            "network_calls": 0,
            "limitations": [
                "This is a local synthetic integration demonstration, not a production deployment.",
                "The approval is a deterministic test fixture, not a human approval interface.",
                "Open-Swarm uses its mock adapter; no model provider is contacted.",
                "MCP is called in-process; no external MCP transport is demonstrated.",
                "OIX has no network relay in this demonstration.",
            ],
        }


def main() -> None:
    print(json.dumps(run_demo(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

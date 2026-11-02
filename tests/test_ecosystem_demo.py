from examples.ecosystem_demo import run_demo


def test_synthetic_cross_repository_demo_passes():
    result = run_demo()
    assert result["status"] == "PASS"
    assert result["synthetic_data_only"] is True
    assert result["oix"]["request_signature_and_recipient_valid"] is True
    assert result["oix"]["receipt_signature_and_recipient_valid"] is True
    assert result["oix"]["durable_replay_duplicate_rejected"] is True
    assert result["open_swarm"]["task_status"] == "succeeded"
    assert result["halloween_mcp"]["files"] == 1
    assert result["hco"]["ed25519_signature_valid"] is True
    assert result["payload_executed"] is False
    assert result["network_calls"] == 0

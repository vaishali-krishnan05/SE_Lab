import pytest

from cloud_storage_tier import (
    process_storage_tenants,
    monitor_replication_latency,
)


def test_invalid_inputs():
    with pytest.raises(ValueError):
        process_storage_tenants("invalid", 10.0)

    with pytest.raises(ValueError):
        process_storage_tenants([], -1.0)


def test_empty_tenant_list():
    result = process_storage_tenants([], 10.0)

    assert result == {
        "total_billed": 0.0,
        "status": "ZERO_USAGE",
    }


@pytest.mark.parametrize(
    "tier, size, expected_charge",
    [
        ("hot", 100, 2.5),
        ("cool", 100, 1.5),
        ("archive", 100, 0.5),
        ("hot", 600, 13.5),
    ],
)
def test_tier_and_size_branches(tier, size, expected_charge):
    tenant = {
        "account_active": True,
        "tier": tier,
        "buckets": [{"size_gb": size}],
    }

    result = process_storage_tenants([tenant], 10.0)

    assert result["total_billed"] == expected_charge
    assert result["status"] == "BILLED"


def test_inactive_tenant():
    tenant = {
        "account_active": False,
        "tier": "hot",
        "buckets": [{"size_gb": 100}],
    }

    result = process_storage_tenants([tenant], 10.0)

    assert result["status"] == "ZERO_USAGE"


def test_unknown_tier():
    tenant = {
        "account_active": True,
        "tier": "invalid",
        "buckets": [{"size_gb": 100}],
    }

    result = process_storage_tenants([tenant], 10.0)

    assert result["status"] == "ZERO_USAGE"


@pytest.mark.parametrize("size", [0, -10])
def test_nonpositive_bucket_size(size):
    tenant = {
        "account_active": True,
        "tier": "hot",
        "buckets": [{"size_gb": size}],
    }

    result = process_storage_tenants([tenant], 10.0)

    assert result["status"] == "ZERO_USAGE"


def test_corrupted_hot_bucket():
    tenant = {
        "account_active": True,
        "tier": "hot",
        "buckets": [
            {
                "size_gb": 100,
                "corrupted": True,
                "egress_gb": 0,
            }
        ],
    }

    result = process_storage_tenants([tenant], 10.0)

    assert result["status"] == "ZERO_USAGE"


def test_corrupted_archive_bucket():
    tenant = {
        "account_active": True,
        "tier": "archive",
        "buckets": [
            {
                "size_gb": 100,
                "corrupted": True,
                "egress_gb": 0,
            },
            {"size_gb": 200},
        ],
    }

    result = process_storage_tenants([tenant], 10.0)

    assert result["status"] == "ZERO_USAGE"


def test_egress_threshold():
    tenant = {
        "account_active": True,
        "tier": "hot",
        "buckets": [
            {"size_gb": 100, "egress_gb": 100},
            {"size_gb": 100, "egress_gb": 150},
        ],
    }

    result = process_storage_tenants([tenant], 10.0)

    assert result["total_billed"] == 9.0
    assert result["status"] == "BILLED"


def test_backup_vault():
    tenant = {
        "account_active": True,
        "tier": "hot",
        "has_backup_vault": True,
        "buckets": [{"size_gb": 100}],
    }

    result = process_storage_tenants([tenant], 10.0)

    assert result["total_billed"] == 12.5
    assert result["status"] == "BILLED"


def test_audit_threshold():
    tenant = {
        "account_active": True,
        "tier": "hot",
        "buckets": [{"size_gb": 0} for _ in range(5)],
    }

    result = process_storage_tenants([tenant], 10.0)

    assert result["status"] == "AUDIT_FLAGGED"


def test_four_flags_do_not_trigger_audit():
    tenant = {
        "account_active": True,
        "tier": "hot",
        "buckets": [{"size_gb": 0} for _ in range(4)]
        + [{"size_gb": 100}],
    }

    result = process_storage_tenants([tenant], 10.0)

    assert result == {
        "total_billed": 2.5,
        "status": "BILLED",
    }


def test_no_replication_data():
    assert monitor_replication_latency([]) == "NO_DATA"


def test_empty_node_logs():
    assert monitor_replication_latency([[]]) == "SYNCED"


def test_latency_at_threshold():
    assert monitor_replication_latency([[200]]) == "SYNCED"


def test_single_high_latency():
    assert monitor_replication_latency([[250]]) == "SYNCED"


def test_high_latency_then_recovery():
    assert monitor_replication_latency([[250, 100, 250]]) == "SYNCED"


def test_consecutive_high_latency():
    assert (
        monitor_replication_latency([[250, 260]])
        == "SYNC_LAG_ALERT"
    )


def test_alert_on_later_node():
    assert monitor_replication_latency([
        [250],
        [100, 220, 230],
    ]) == "SYNC_LAG_ALERT"
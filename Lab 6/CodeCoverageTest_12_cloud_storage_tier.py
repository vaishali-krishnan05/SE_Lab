import pytest

from cloud_storage_tier import (
    process_storage_tenants,
    monitor_replication_latency,
)


def test_invalid_tenant_input():
    with pytest.raises(ValueError):
        process_storage_tenants("invalid", 10.0)


def test_negative_support_fee():
    with pytest.raises(ValueError):
        process_storage_tenants([], -1.0)


def test_storage_tiers_and_billing():
    tenants = [
        {
            "account_active": True,
            "tier": "hot",
            "has_backup_vault": True,
            "buckets": [
                {"size_gb": 100, "egress_gb": 150},
                {"size_gb": 600, "egress_gb": 100},
            ],
        },
        {
            "account_active": True,
            "tier": "cool",
            "buckets": [{"size_gb": 200}],
        },
        {
            "account_active": True,
            "tier": "archive",
            "buckets": [{"size_gb": 200}],
        },
    ]

    result = process_storage_tenants(tenants, 10.0)

    assert result == {
        "total_billed": 34.0,
        "status": "BILLED",
    }


def test_inactive_tenant_is_skipped():
    tenants = [
        {
            "account_active": False,
            "tier": "hot",
            "buckets": [{"size_gb": 100}],
        }
    ]

    result = process_storage_tenants(tenants, 10.0)

    assert result == {
        "total_billed": 0.0,
        "status": "ZERO_USAGE",
    }


def test_unknown_tier_is_flagged():
    tenants = [
        {
            "account_active": True,
            "tier": "unknown",
            "buckets": [{"size_gb": 100}],
        }
    ]

    result = process_storage_tenants(tenants, 10.0)

    assert result["total_billed"] == 0.0
    assert result["status"] == "ZERO_USAGE"


def test_invalid_bucket_size_is_skipped():
    tenants = [
        {
            "account_active": True,
            "tier": "hot",
            "buckets": [
                {"size_gb": 0},
                {"size_gb": -10},
                {"size_gb": 100},
            ],
        }
    ]

    result = process_storage_tenants(tenants, 10.0)

    assert result == {
        "total_billed": 2.5,
        "status": "BILLED",
    }


def test_corrupted_hot_bucket():
    tenants = [
        {
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
    ]

    result = process_storage_tenants(tenants, 10.0)

    assert result == {
        "total_billed": 0.0,
        "status": "ZERO_USAGE",
    }


def test_corrupted_archive_bucket():
    tenants = [
        {
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
    ]

    result = process_storage_tenants(tenants, 10.0)

    assert result == {
        "total_billed": 0.0,
        "status": "ZERO_USAGE",
    }


def test_audit_flagged_after_multiple_invalid_tiers():
    tenants = [
        {"account_active": True, "tier": "invalid"}
        for _ in range(5)
    ]

    result = process_storage_tenants(tenants, 10.0)

    assert result == {
        "total_billed": 0.0,
        "status": "AUDIT_FLAGGED",
    }


def test_no_replication_data():
    assert monitor_replication_latency([]) == "NO_DATA"


def test_replication_latency_alert():
    assert (
        monitor_replication_latency([[250, 260]])
        == "SYNC_LAG_ALERT"
    )


def test_replication_latency_recovers():
    assert (
        monitor_replication_latency([[250, 100, 250]])
        == "SYNCED"
    )
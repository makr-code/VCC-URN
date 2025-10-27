from vcc_urn.service import URNService


def test_service_generate_and_resolve_local():
    svc = URNService()
    urn = svc.generate(state="by", domain="bau", obj_type="bescheid", local="AZ-123", store=True)
    assert urn.startswith("urn:de:by:bau:bescheid:")
    manifest = svc.resolve(urn)
    assert manifest["urn"] == urn
    assert manifest["type"] == "bescheid"
    assert manifest["domain"] == "bau"
    assert manifest["country"] == "by"
    results = svc.search_by_uuid(manifest["uuid"])  # default limit
    assert any(r["urn"] == urn for r in results)

from vcc_urn.urn import URN


def test_generate_and_parse_roundtrip():
    u = URN.generate(state="nrw", domain="bimschg", obj_type="anlage", local_aktenzeichen="4711-0815-K1")
    s = u.as_string()
    assert s.startswith("urn:de:nrw:bimschg:anlage:")
    parsed = URN(s)
    c = parsed.to_dict()
    assert c["state"] == "nrw"
    assert c["domain"] == "bimschg"
    assert c["obj_type"] == "anlage"
    assert c["local_aktenzeichen"] == "4711-0815-K1"
    assert len(c["uuid"]) == 36


def test_invalid_urn_rejected():
    bad = "urn:de:nrw:domain:missingparts"
    try:
        URN(bad)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_invalid_nid_rejected():
    u = URN.generate(state="nrw", domain="bimschg", obj_type="anlage", local_aktenzeichen="4711")
    s = u.as_string().replace("urn:de:", "urn:xx:")
    try:
        URN(s)
        assert False, "Expected ValueError for unexpected NID"
    except ValueError:
        pass

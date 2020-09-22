"""Integration tests."""
import requests


def test_phenotypes(host_url):
    """Simple test of running server."""

    payload = {
        "output": "single-dropdown.options",
        "outputs": {
            "id": "single-dropdown",
            "property": "options"
        },
        "inputs": [
            {
                "id": "single-dropdown",
                "property": "search_value",
                "value": "zz"
            }
        ],
        "changedPropIds": [
            "single-dropdown.search_value"
        ]
    }

    response = requests.post(
        f'{host_url}/_dash-update-component',
        headers={"Content-Type": "application/json"}, json=payload
    )

    assert response.ok

    genes = response.json()
    assert genes['response']
    assert genes['response']["single-dropdown"]
    assert genes['response']["single-dropdown"]["options"]
    options = genes['response']["single-dropdown"]["options"]
    expected =["ZZEF1/ENSG00000074755", "ZZZ3/ENSG00000036549"]
    for e in expected:
        assert e in [o['label'] for o in options]

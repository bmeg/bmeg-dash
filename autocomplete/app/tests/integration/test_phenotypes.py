"""Integration tests."""
import requests


def test_phenotypes(host_url):
    """Simple test of running server."""

    payload = {
        "output": "process-multiple-output.children",
        "outputs": {
            "id": "process-multiple-output",
            "property": "children"
        },
        "inputs": [
            {
                "id": "process-multiple",
                "property": "n_clicks",
                "value": 0
            }
        ],
        "changedPropIds": [
            "process-multiple.n_clicks"
        ],
        "state": [
            {
                "id": "multi-dropdown",
                "property": "value",
                "value": [
                    "ADH4/ENSG00000198099",
                    "ZNF98/ENSG00000197360"
                ]
            }
        ]
    }

    response = requests.post(
        f'{host_url}/_dash-update-component',
        headers={"Content-Type": "application/json"}, json=payload
    )

    assert response.ok

    phenotypes = response.json()
    assert phenotypes['response']
    assert phenotypes['response']["process-multiple-output"]
    assert phenotypes['response']["process-multiple-output"]["children"]
    assert "phenotypes" in phenotypes['response']["process-multiple-output"]["children"]

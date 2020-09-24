"""Integration tests."""
import requests


def test_cache_info(host_url):
    """Simple test of running server."""

    payload = {
        "output": "info-cache-output.children",
        "outputs": {
            "id": "info-cache-output",
            "property": "children"
        },
        "inputs": [
            {
                "id": "info-cache",
                "property": "n_clicks",
                "value": 1
            }
        ],
        "changedPropIds": [
            "info-cache.n_clicks"
        ]
    }
    response = requests.post(
        f'{host_url}/_dash-update-component',
        headers={"Content-Type": "application/json"}, json=payload
    )

    assert response.ok

    cache = response.json()
    assert cache['response']
    assert cache['response']["info-cache-output"]
    assert cache['response']["info-cache-output"]["children"]
    assert 'hits' in cache['response']["info-cache-output"]["children"]
    assert 'misses' in cache['response']["info-cache-output"]["children"]


def test_cache_clear(host_url):
    """Simple test of running server."""

    payload = {
        "output": "cache-output.children",
        "outputs": {
            "id": "cache-output",
            "property": "children"
        },
        "inputs": [
            {
                "id": "clear-cache",
                "property": "n_clicks",
                "value": 1
            }
        ],
        "changedPropIds": [
            "clear-cache.n_clicks"
        ]
    }

    response = requests.post(
        f'{host_url}/_dash-update-component',
        headers={"Content-Type": "application/json"}, json=payload
    )

    assert response.ok

    cache = response.json()
    assert cache['response']
    assert cache['response']["cache-output"]
    assert cache['response']["cache-output"]["children"]
    assert "Cache reset" in cache['response']["cache-output"]["children"]

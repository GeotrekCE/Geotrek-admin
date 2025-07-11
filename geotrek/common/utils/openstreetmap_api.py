import xml.etree.ElementTree as ET
from urllib.parse import urljoin

import requests
from django.conf import settings
from django.utils.translation import gettext as _
from requests_oauthlib import OAuth2Session

from geotrek.authent.models import UserProfile


def get_osm_oauth_uri(redirect_uri):
    """
    Generate the OpenStreetMap OAuth2 URI
    """
    client_id = settings.OSM_CLIENT_ID
    scope = "write_api"

    client = OAuth2Session(client_id=client_id, redirect_uri=redirect_uri, scope=scope)
    url = urljoin(settings.OSM_API_BASE_URL, "/oauth2/authorize/")

    uri, state = client.authorization_url(url)

    return uri, state


def get_osm_token(code, state_client, state_server, redirect_uri, user_id):
    """
    Get a token for the OpenStreetMap API and save it in database.
    """
    if not code or not state_server:
        msg = _("code or state is missing")
        raise Exception(msg)

    if state_client != state_server:
        msg = _("invalid state")
        raise Exception(msg)

    client_id = settings.OSM_CLIENT_ID
    client_secret = settings.OSM_CLIENT_SECRET
    scope = "write_api"

    client = OAuth2Session(client_id=client_id, redirect_uri=redirect_uri, scope=scope)
    url = urljoin(settings.OSM_API_BASE_URL, "/oauth2/token/")

    token = client.fetch_token(url, code=code, client_secret=client_secret)

    user = UserProfile.objects.get(user_id=user_id)
    user.osm_token = f"Bearer {token.get('access_token')}"
    user.save()


def create_changeset(token, user_agent, comment):
    # API url
    url = urljoin(settings.OSM_API_BASE_URL, "/api/0.6/changeset/create/")

    # XML data
    osm = ET.Element("osm", {"version": "0.6"})
    changeset = ET.SubElement(osm, "changeset")
    ET.SubElement(changeset, "tag", k="created_by", v=user_agent)
    ET.SubElement(changeset, "tag", k="comment", v=comment)

    data = ET.tostring(osm, encoding="utf-8", xml_declaration=True).decode()

    # header
    headers = {
        "Authorization": token,
        "User-Agent": f"{settings.OSM_APPLICATION_NAME}/0.1",
        "Content-Type": "text/xml",
    }

    response = requests.put(url, headers=headers, data=data)

    # handle errors
    if response.status_code != 200:
        match response.status_code:
            case 400:
                msg = _("Bad Request: Changeset")
            case 405:
                msg = _("Method Not Allowed: Changeset")
            case _:
                try:
                    response.raise_for_status()
                except Exception as e:
                    msg = str(e)
        raise requests.exceptions.RequestException(msg)

    changeset_id = response.content.decode()
    return changeset_id


def get_element(type, id):
    url = urljoin(settings.OSM_API_BASE_URL, f"api/0.6/{type}/{id}.json")

    response = requests.get(url)

    # handle errors
    if response.status_code != 200:
        match response.status_code:
            case 404:
                msg = _("OpenStreetMap object %(type)s(%(id)s) not found") % (
                    {"type": type, "id": id}
                )
            case 410:
                msg = _("OpenStreetMap object %(type)s(%(id)s) has been deleted") % (
                    {"type": type, "id": id}
                )
            case _:
                try:
                    response.raise_for_status()
                except Exception as e:
                    msg = str(e)
        raise requests.exceptions.RequestException(msg)

    return response.json()["elements"][0]


def update_element(token, changeset_id, object):
    # API url
    url = urljoin(
        settings.OSM_API_BASE_URL, f"/api/0.6/{object['type']}/{object['id']}"
    )

    # XML data
    osm = ET.Element("osm", {"version": "0.6"})

    elements_tags = ["changeset", "id", "lat", "lon", "version", "visible"]
    attributs = {k: str(v) for k, v in object.items() if k in elements_tags}
    attributs["changeset"] = changeset_id
    element = ET.SubElement(osm, object["type"], attributs)

    if "nodes" in object:
        for node in object["nodes"]:
            ET.SubElement(element, "nd", {"ref": str(node)})

    if "members" in object:
        for member in object["members"]:
            ET.SubElement(
                element,
                "member",
                {
                    "type": str(member["type"]),
                    "ref": str(member["ref"]),
                    "role": str(member["role"]),
                },
            )

    for key, value in object["tags"].items():
        ET.SubElement(element, "tag", {"k": key, "v": value})

    data = ET.tostring(osm, encoding="utf-8", xml_declaration=True).decode()

    # header
    headers = {
        "Authorization": token,
        "User-Agent": f"{settings.OSM_APPLICATION_NAME}/0.1",
        "Content-Type": "text/xml",
    }

    response = requests.put(url, headers=headers, data=data)

    # handle errors
    if response.status_code != 200:
        match response.status_code:
            case 400:
                msg = _("Bad Request: Element")
            case 404:
                msg = _("Element not found")
            case 409:
                msg = _("Changeset closed")
            case 412:
                msg = _("Nodes/Ways that compose the element does not exist")
            case 429:
                msg = _("Too Many Requests")
            case _:
                try:
                    response.raise_for_status()
                except Exception as e:
                    msg = str(e)
        raise requests.exceptions.RequestException(msg)


def close_changeset(token, changeset_id):
    url = urljoin(
        settings.OSM_API_BASE_URL, f"/api/0.6/changeset/{changeset_id}/close/"
    )

    # header
    headers = {
        "Authorization": token,
        "User-Agent": f"{settings.OSM_APPLICATION_NAME}/0.1",
    }

    response = requests.put(url, headers=headers)

    # handle errors
    if response.status_code != 200:
        match response.status_code:
            case 404:
                msg = _("Changeset not found")
            case 405:
                msg = _("Method Not Allowed: Changeset")
            case 409:
                msg = _("Changeset already closed")
            case _:
                try:
                    response.raise_for_status()
                except Exception as e:
                    msg = str(e)
        raise requests.exceptions.RequestException(msg)

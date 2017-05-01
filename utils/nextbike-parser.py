# coding=utf-8
import json
from collections import OrderedDict
from urllib2 import urlopen

import unidecode as unidecode
from slugify import slugify


def resolve_network_name(network_name, country_key, country_name, city_name, domain):
    name = (network_name.replace("Tirol", "")
            .replace("World", "")
            .replace("Niederösterreich", "")
            .replace("Stuttgart", "")
            .replace("Innsbruck", "")
            .replace("nextbike " + country_key, "")
            .replace("nextbike " + domain.upper(), "")
            .replace("nextbike", "").replace(country_name, "")
            .replace(country_name, "")
            .strip())

    if name == city_name:
        name = ""

    return name


def resolve_network_tag(network_name, city_name):
    if network_name:
        tag = network_name + "-" + city_name
    else:
        tag = "nextbike-" + city_name

    return tag


def retrieve_networks(data):
    results = []

    for country in data['countries']:
        network_name = country['name'].encode('UTF-8')
        domain = country['domain'].encode('UTF-8')
        country_key = country['country'].encode('UTF-8')
        country_name = country['country_name'].encode('UTF-8')

        for city in country['cities']:
            network = OrderedDict()

            city_name = city['name'].encode('UTF-8')
            city_uid = city['uid']
            city_lat = city['lat']
            city_lng = city['lng']
            network_name = resolve_network_name(network_name, country_key, country_name, city_name, domain)
            tag = resolve_network_tag(network_name, city_name)
            stripped_tag = unidecode.unidecode(tag.decode('UTF-8'))

            network['domain'] = domain
            network['tag'] = slugify(stripped_tag.decode('UTF-8'))
            network['city_uid'] = city_uid

            network['meta'] = OrderedDict()

            if network_name:
                network['meta']['name'] = network_name.decode('UTF-8')

            network['meta']['city'] = city_name.decode('UTF-8')
            network['meta']['country'] = country_key
            network['meta']['latitude'] = float(city_lat)
            network['meta']['longitude'] = float(city_lng)

            results.append(network)

    results.sort(key=lambda k: k['city_uid'])

    return results


if __name__ == "__main__":
    url = 'https://api.nextbike.net/maps/nextbike-live.json?list_cities=1'
    response = urlopen(url)
    jsonData = json.load(response)

    networks = retrieve_networks(jsonData)

    json_dump = json.dumps({'instances': networks}, ensure_ascii=False, indent=4, separators=(',', ': ')).encode('UTF-8')

    print (json_dump)

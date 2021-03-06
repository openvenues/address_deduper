from address_deduper.views.base import *

from address_normalizer.deduping.near_duplicates import *

from address_normalizer.models.address import *

class AddressView(BaseView):
    
    blueprint = Blueprint('addresses', __name__, url_prefix='/addresses')

    @classmethod
    def address_from_params(cls, require_street=True, require_latlon=True):
        address = Address(request.args, strict=False)

        if require_street and not address.street:
            abort(400, 'street must be specified')
        if require_latlon and (not address.latitude or not address.longitude):
            abort(400, 'latitude and longitude must be specified')

        return address

    @classmethod
    def addresses_from_json(cls, require_street=True, require_latlon=True):
        key, batch = ('addresses', True) if 'batch' in request.args else ('address', False)
        try:
            data = request.json
        except Exception:
            abort(400, 'POST request was not JSON or could not be parsed')

        data = data.get(key)
        if not data:
            abort(400, 'The key "{}" could not be found in the request data'.format(key))
        
        addresses = [Address(a) for a in (data if batch else [data])]
        if not require_latlon and not require_street:
            return addresses

        for a in addresses:
            if require_street and not a.street:
                abort(400, 'All addresses must include "street" key')
            if require_latlon and (not a.latitude or not a.longitude):
                abort(400, 'All addresses must include "latitude" and "longitude" keys')

        return addresses

    @route('/normalize', methods=['GET'])
    def normalize_get(cls):
        address = cls.address_from_params(require_latlon=False)
        surface_forms = AddressNearDupe.expanded_street_address(address)
        return jsonify({'address': address.to_primitive(),
                        'normalized_expansions': list(surface_forms)})


    @route('/normalize', methods=['POST'])
    def normalize_post(cls):
        addresses = cls.addresses_from_json(require_latlon=False)
        return jsonify({'addresses': [{'address': address.to_primitive(),
                                        'normalized_expansions': list(AddressNearDupe.expanded_street_address(address))} for address in addresses]})


    @route('/dedupe', methods=['GET'])
    def exists(cls):
        address = cls.address_from_params()
        existence = AddressNearDupe.check([address], add=False)
        return_val = {}
        if existence:
            _, (guid, dupe) = existence[0]
            response = {'guid': guid, 'dupe': dupe}
            if 'debug' in request.values and dupe:
                existing_address = AddressNearDupe.storage.get(guid)
                if existing_address:
                    response['object'] = dict(address)
                    response['existing'] = json.loads(existing_address)
            return jsonify(response)
        else:
            abort(500, 'Unknown error')


    @route('/dedupe', methods=['POST'])
    def dedupe(cls):
        addresses = cls.addresses_from_json()
        created = AddressNearDupe.check(addresses, add=True)
        obj_dict = {a.guid: a for a in addresses}
        response = [{'guid': guid, 'dupe': dupe} for _, (guid, dupe) in created]
        if 'debug' in request.values:
            guids = [guid for _, (guid, dupe) in created if dupe]
            existing_addresses = {guid: a if not a else json.loads(a) for guid, a in AddressNearDupe.storage.multiget(guids).iteritems()}
            for i, r in enumerate(response):
                if r['dupe']:
                    guid = r['guid']
                    existing_address = existing_addresses[guid] or dict(obj_dict[guid])
                    r['object'] = dict(addresses[i])
                    r['existing'] = existing_address
        return jsonify({'addresses': response})

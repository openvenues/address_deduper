from address_normalizer.views.base import *

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
            return jsonify({'guid': guid, 'dupe': dupe})
        else:
            abort(500, 'Unknown error')


    @route('/dedupe', methods=['POST'])
    def dedupe(cls):
        addresses = cls.addresses_from_json()
        created = AddressNearDupe.check(addresses, add=True)
        return jsonify({'addresses': [{'guid': guid, 'dupe': dupe} for _, (guid, dupe) in created]})

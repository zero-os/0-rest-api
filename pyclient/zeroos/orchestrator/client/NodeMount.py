"""
Auto-generated class for NodeMount
"""

from . import client_support


class NodeMount(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(device, fstype, mountpoint, opts):
        """
        :type device: str
        :type fstype: str
        :type mountpoint: str
        :type opts: str
        :rtype: NodeMount
        """

        return NodeMount(
            device=device,
            fstype=fstype,
            mountpoint=mountpoint,
            opts=opts,
        )

    def __init__(self, json=None, **kwargs):
        if not json and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'NodeMount'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'device'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.device = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'fstype'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.fstype = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'mountpoint'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.mountpoint = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'opts'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.opts = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)

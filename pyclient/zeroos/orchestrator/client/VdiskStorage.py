"""
Auto-generated class for VdiskStorage
"""

from . import client_support


class VdiskStorage(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(blockCluster, id, objectCluster=None, slaveCluster=None):
        """
        :type blockCluster: str
        :type id: str
        :type objectCluster: str
        :type slaveCluster: str
        :rtype: VdiskStorage
        """

        return VdiskStorage(
            blockCluster=blockCluster,
            id=id,
            objectCluster=objectCluster,
            slaveCluster=slaveCluster,
        )

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'VdiskStorage'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'blockCluster'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.blockCluster = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'id'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.id = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'objectCluster'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.objectCluster = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'slaveCluster'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.slaveCluster = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)

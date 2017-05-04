"""
Auto-generated class for BridgeCreate
"""
from .BridgeCreateSetting import BridgeCreateSetting
from .EnumBridgeCreateNetworkMode import EnumBridgeCreateNetworkMode

from . import client_support


class BridgeCreate(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(name, nat, networkMode, setting, hwaddr=None):
        """
        :type hwaddr: str
        :type name: str
        :type nat: bool
        :type networkMode: EnumBridgeCreateNetworkMode
        :type setting: BridgeCreateSetting
        :rtype: BridgeCreate
        """

        return BridgeCreate(
            hwaddr=hwaddr,
            name=name,
            nat=nat,
            networkMode=networkMode,
            setting=setting,
        )

    def __init__(self, json=None, **kwargs):
        if not json and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'BridgeCreate'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'hwaddr'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.hwaddr = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'name'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.name = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'nat'
        val = data.get(property_name)
        if val is not None:
            datatypes = [bool]
            try:
                self.nat = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'networkMode'
        val = data.get(property_name)
        if val is not None:
            datatypes = [EnumBridgeCreateNetworkMode]
            try:
                self.networkMode = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'setting'
        val = data.get(property_name)
        if val is not None:
            datatypes = [BridgeCreateSetting]
            try:
                self.setting = client_support.val_factory(val, datatypes)
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
